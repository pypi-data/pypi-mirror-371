from yta_video_opengl.complete.video_on_track import VideoOnTrack
from yta_video_opengl.video import Video
from yta_validation.parameter import ParameterValidator
from typing import Union


# TODO: This is called Track but it is
# handling videos only. Should I have
# VideoTrack and AudioTrack (?)
class Track:
    """
    Class to represent a track in which we place
    videos, images and audio to build a video
    project.
    """

    @property
    def end(
        self
    ) -> float:
        """
        The end of the last video of this track,
        which is also the end of the track. This
        is the last time moment that has to be
        rendered.
        """
        return (
            0.0
            if len(self.videos) == 0 else
            max(
                video.end
                for video in self.videos
            )
        )

    def __init__(
        self
    ):
        self.videos: list[VideoOnTrack] = []
        """
        The list of 'VideoOnTrack' instances that
        must play on this track.
        """

    def _is_free(
        self,
        start: float,
        end: float
    ) -> bool:
        """
        Check if the time range in between the 
        'start' and 'end' time given is free or
        there is some video playing at any moment.
        """
        return not any(
            (
                video.video.start < end and
                video.video.end > start
            )
            for video in self.videos
        )
    
    def _get_video_at_t(
        self,
        t: float
    ) -> Union[VideoOnTrack, None]:
        """
        Get the video that is being played at
        the 't' time moment provided.
        """
        for video in self.videos:
            if video.start <= t < video.end:
                return video
            
        return None
    
    def get_frame_at(
        self,
        t: float
    ) -> Union['VideoFrame', None]:
        """
        Get the frame that must be displayed at
        the 't' time moment provided, which is
        a frame from the video that is being
        played at that time moment.

        Remember, this 't' time moment provided
        is about the track, and we make the
        conversion to the actual video 't' to
        get the frame.
        """
        video = self._get_video_at_t(t)

        return (
            video.get_frame_at(t)
            if video is not None else
            None
        )

    def add_video(
        self,
        video: Video,
        t: Union[float, None] = None
    ) -> 'Track':
        """
        Add the 'video' provided to the track. If
        a 't' time moment is provided, the video
        will be added to that time moment if 
        possible. If there is no other video 
        placed in the time gap between the given
        't' and the provided 'video' duration, it
        will be added succesfully. In the other
        case, an exception will be raised.

        If 't' is None, the first available 't'
        time moment will be used, that will be 0.0
        if no video, or the end of the last video.
        """
        ParameterValidator.validate_mandatory_instance_of('video', video, Video)
        ParameterValidator.validate_positive_float('t', t, do_include_zero = True)

        if t is not None:
            # TODO: We can have many different strategies
            # that we could define in the '__init__' maybe
            if not self._is_free(t, (t + video.end)):
                raise Exception('The video cannot be added at the "t" time moment, something blocks it.')
        else:
            t = self.end
        
        self.videos.append(VideoOnTrack(
            video,
            t
        ))

        # TODO: Maybe return the VideoOnTrack instead (?)
        return self