from yta_video_opengl.complete.track import Track
from yta_video_opengl.video import Video
from yta_validation.parameter import ParameterValidator
from typing import Union
from fractions import Fraction

import numpy as np
import av


class Timeline:
    """
    Class to represent all the tracks that
    exist on the project and to handle the
    combination of all their frames.
    """

    @property
    def end(
        self
    ) -> float:
        """
        The end of the last video of the track
        that lasts longer. This is the last time
        moment that has to be rendered.
        """
        return max(track.end for track in self.tracks)

    def __init__(
        self,
        size: tuple[int, int] = (1920, 1080),
        fps: float = 60.0
    ):
        # TODO: By now we are using just two video
        # tracks to test the composition
        # TODO: We need to be careful with the
        # priority, by now its defined by its
        # position in the array
        self.tracks: list[Track] = [Track(), Track()]
        """
        All the video tracks we are handling.
        """
        # TODO: Handle size and fps
        self.size = size
        self.fps = fps

    # TODO: Create 'add_track' method, but by now
    # we hare handling only one
    def add_video(
        self,
        video: Video,
        t: float,
        # TODO: This is for testing, it has to
        # disappear
        do_use_second_track: bool = False
    ) -> 'Timeline':
        """
        Add the provided 'video' to the timeline,
        starting at the provided 't' time moment.

        TODO: The 'do_use_second_track' parameter
        is temporary.
        """
        index = 1 * do_use_second_track

        self.tracks[index].add_video(video, t)

        return self

    # TODO: This method is not for the Track but
    # for the timeline, as one track can only
    # have consecutive elements
    def get_frame_at(
        self,
        t: float
    ) -> Union['VideoFrame', None]:
        """
        Get all the frames that are played at the
        't' time provided, but combined in one.
        """
        frames = (
            track.get_frame_at(t)
            for track in self.tracks
        )

        frames = [
            frame
            for frame in frames
            if frame is not None
        ]

        return (
            # TODO: Combinate them, I send first by now
            frames[0]
            if len(frames) > 0 else
            # TODO: Should I send None or a full
            # black (or transparent) frame? I think
            # None is better because I don't know
            # the size here (?)
            None
        )
    
    def render(
        self,
        filename: str,
        start: float = 0.0,
        end: Union[float, None] = None
    ) -> 'Timeline':
        """
        Render the time range in between the given
        'start' and 'end' and store the result with
        the also provided 'fillename'.

        If no 'start' and 'end' provided, the whole
        project will be rendered.
        """
        ParameterValidator.validate_mandatory_string('filename', filename, do_accept_empty = False)
        ParameterValidator.validate_mandatory_positive_number('start', start, do_include_zero = True)
        ParameterValidator.validate_positive_number('end', end, do_include_zero = False)

        # TODO: Limitate 'end' a bit...
        end = (
            self.end
            if end is None else
            end
        )

        if start >= end:
            raise Exception('The provided "start" cannot be greater or equal to the "end" provided.')
        # TODO: Obtain all the 't', based on 'fps'
        # that we need to render from 'start' to
        # 'end'
        # TODO: I don't want to have this here
        def generate_times(start: float, end: float, fps: int):
            dt = 1.0 / fps
            times = []

            t = start
            while t <= end:
                times.append(t + 0.000001)
                t += dt

            return times

        from yta_video_opengl.writer import VideoWriter

        writer = VideoWriter('test_files/output_render.mp4')
        # TODO: This has to be dynamic according to the
        # video we are writing
        writer.set_video_stream(
            codec_name = 'h264',
            fps = 60,
            size = (1920, 1080),
            pixel_format = 'yuv420p'
        )
        
        for t in generate_times(start, end, self.fps):
            frame = self.get_frame_at(t)

            if frame is None:
                # Replace with black background if no frame
                frame = av.VideoFrame.from_ndarray(
                    array = np.zeros((1920, 1080, 3), dtype = np.uint8),
                    format = 'rgb24'
                )

            # We need to adjust our output elements to be
            # consecutive and with the right values
            # TODO: We are using int() for fps but its float...
            frame.time_base = Fraction(1, int(self.fps))
            frame.pts = int(t / frame.time_base)

            # TODO: We need to handle the audio
            writer.mux_video_frame(
                frame = frame
            )

        writer.mux_video_frame(None)
        writer.output.close()