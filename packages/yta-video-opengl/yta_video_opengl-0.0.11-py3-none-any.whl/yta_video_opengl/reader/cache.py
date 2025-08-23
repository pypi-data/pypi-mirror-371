"""
The pyav container stores the information based
on the packets timestamps (called 'pts'). Some
of the packets are considered key_frames because
they include those key frames.

Also, this library uses those key frames to start
decodifying from there to the next one, obtaining
all the frames in between able to be read and
modified.

This cache system will look for the range of 
frames that belong to the key frame related to the
frame we are requesting in the moment, keeping in
memory all those frames to be handled fast. It
will remove the old frames if needed to use only
the 'size' we set when creating it.
"""
from yta_video_opengl.utils import t_to_pts, pts_to_t, pts_to_index, index_to_pts
from yta_video_frame_time import T
from av.container import InputContainer
from av.video.stream import VideoStream
from av.audio.stream import AudioStream
from av.video.frame import VideoFrame
from av.audio.frame import AudioFrame
from yta_validation.parameter import ParameterValidator
from yta_validation import PythonValidator
from fractions import Fraction
from collections import OrderedDict
from typing import Union

import numpy as np
import math


class VideoFrameCache:
    """
    Class to manage the frames cache of a video
    within a video reader instance.
    """

    @property
    def fps(
        self
    ) -> float:
        """
        The frames per second as a float.
        """
        return (
            float(self.stream.average_rate)
            if self.stream.type == 'video' else
            float(self.stream.rate)
        )
    
    @property
    def time_base(
        self
    ) -> Union[Fraction, None]:
        """
        The time base of the stream.
        """
        return self.stream.time_base

    def __init__(
        self,
        container: InputContainer,
        stream: Union[VideoStream, AudioStream],
        size: Union[int, None] = None
    ):
        ParameterValidator.validate_mandatory_instance_of('container', container, InputContainer)
        ParameterValidator.validate_mandatory_instance_of('stream', stream, [VideoStream, AudioStream])
        ParameterValidator.validate_positive_int('size', size)

        self.container: InputContainer = container
        """
        The pyav container.
        """
        self.stream: Union[VideoStream, AudioStream] = stream
        """
        The pyav stream.
        """
        self.cache: OrderedDict = OrderedDict()
        """
        The cache ordered dictionary.
        """
        self.size: Union[int, None] = size
        """
        The size (in number of frames) of the cache.
        """
        self.key_frames_pts: list[int] = []
        """
        The list that contains the timestamps of the
        key frame packets, ordered from begining to
        end.
        """

        self._prepare()

    def _prepare(
        self
    ):
        # Index key frames
        for packet in self.container.demux(self.stream):
            if packet.is_keyframe:
                self.key_frames_pts.append(packet.pts)

        # The cache size will be auto-calculated to
        # use the amount of frames of the biggest
        # interval of frames that belongs to a key
        # frame, or a value by default
        fps = (
            float(self.stream.average_rate)
            if PythonValidator.is_instance_of(self.stream, VideoStream) else
            float(self.stream.rate)
        )
        # Intervals, but in number of frames
        intervals = np.diff(
            # Intervals of time between keyframes
            np.array(self.key_frames_pts) * self.stream.time_base
        ) * fps

        self.size = (
            math.ceil(np.max(intervals))
            if intervals.size > 0 else
            (
                self.size or
                # TODO: Make this 'default_size' a setting or something
                60
            )
        )
        
        self.container.seek(0)

    def _get_nearest_keyframe_fps(
        self,
        pts: int
    ):
        """
        Get the fps of the keyframe that is the
        nearest to the provided 'pts'. Useful to
        seek and start decoding frames from that
        keyframe.
        """
        return max([
            key_frame_pts
            for key_frame_pts in self.key_frames_pts
            if key_frame_pts <= pts
        ])

    def _store_frame_in_cache(
        self,
        frame: Union[VideoFrame, AudioFrame]
    ) -> Union[VideoFrame, AudioFrame]:
        """
        Store the provided 'frame' in cache if it
        is not on it, removing the first item of
        the cache if full.
        """
        if frame.pts not in self.cache:
            # TODO: The 'format' must be dynamic
            self.cache[frame.pts] = frame

            # Clean cache if full
            if len(self.cache) > self.size:
                self.cache.popitem(last = False)

        return frame

    def _get_frame_by_pts(
        self,
        pts: int
    ) -> Union[VideoFrame, AudioFrame, None]:
        """
        Get the frame that has the provided 'pts'.

        This method will start decoding frames from the
        most near key frame (the one with the nearer
        pts) until the one requested is found. All those
        frames will be stored in cache.

        This method must be called when the frame 
        requested is not stored in the caché.
        """
        # Look for the most near key frame
        key_frame_pts = self._get_nearest_keyframe_fps(pts)

        # Go to the key frame that includes it
        self.container.seek(key_frame_pts, stream = self.stream)

        decoded = None
        for frame in self.container.decode(self.stream):
            # TODO: Could 'frame' be None (?)
            if frame.pts is None:
                continue

            # Store in cache if needed
            self._store_frame_in_cache(frame)

            if frame.pts >= pts:
                decoded = self.cache[frame.pts]
                break

        # TODO: Is this working? We need previous 
        # frames to be able to decode...
        return decoded

    def get_frame(
        self,
        index: int
    ) -> Union[VideoFrame, AudioFrame]:
        """
        Get the frame with the given 'index' from
        the cache.
        """
        # TODO: Maybe we can accept 'pts' also
        pts = index_to_pts(index, self.time_base, self.fps)

        return (
            self.cache[pts]
            if pts in self.cache else
            self._get_frame_by_pts(pts)
        )
    
    def get_frame_from_t(
        self,
        t: float
    ) -> Union[VideoFrame, AudioFrame]:
        """
        Get the frame with the given 't' time moment
        from the cache.
        """
        return self.get_frame(T.video_frame_time_to_video_frame_index(t, self.fps))

    def get_frames(
        self,
        start: float = 0,
        end: Union[float, None] = None
    ):
        """
        Get all the frames in the range between
        the provided 'start' and 'end' time in
        seconds.
        """
        # We use the cache as iterator if all the frames
        # requested are stored there
        pts_list = [
            t_to_pts(t, self.time_base)
            for t in T.get_frame_indexes(self.stream.duration, self.fps, start, end)
        ]

        if all(
            pts in self.cache
            for pts in pts_list
        ):
            for pts in pts_list:
                yield self.cache[pts]

        # If not all, we ignore the cache because we
        # need to decode and they are all consecutive
        start = t_to_pts(start, self.time_base)
        end = (
            t_to_pts(end, self.time_base)
            if end is not None else
            None
        )
        key_frame_pts = self._get_nearest_keyframe_fps(start)

        # Go to the nearest key frame to start decoding
        self.container.seek(key_frame_pts, stream = self.stream)

        for packet in self.container.demux(self.stream):
            for frame in packet.decode():
                if frame.pts is None:
                    continue

                # We store all the frames in cache
                self._store_frame_in_cache(frame)

                if frame.pts < start:
                    continue

                if (
                    end is not None and
                    frame.pts > end
                ):
                    return
                
                # TODO: Maybe send a @dataclass instead (?)
                yield (
                    frame,
                    pts_to_t(frame.pts, self.time_base),
                    pts_to_index(frame.pts, self.time_base, self.fps)
                )
    
    def clear(
        self
    ) -> 'VideoFrameCache':
        """
        Clear the cache by removing all the items.
        """
        self.cache.clear()

        return self