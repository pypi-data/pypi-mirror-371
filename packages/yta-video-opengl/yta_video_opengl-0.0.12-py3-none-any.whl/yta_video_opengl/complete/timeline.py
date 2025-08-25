"""
When we are reading from a source, the reader
has its own time base and properties. When we
are writing, the writer has different time
base and properties. We need to adjust our
writer to be able to write, because the videos
we read can be different, and the video we are
writing is defined by us. The 'time_base' is
an important property or will make ffmpeg
become crazy and deny packets (that means no
video written).
"""
from yta_video_opengl.complete.track import Track
from yta_video_opengl.video import Video
from yta_validation.parameter import ParameterValidator
from typing import Union
from fractions import Fraction


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
        return max(
            track.end
            for track in self.tracks
        )

    def __init__(
        self,
        size: tuple[int, int] = (1_920, 1_080),
        fps: float = 60.0,
        audio_fps: float = 44_100.0, # 48_000.0 for aac
        # TODO: I don't like this name
        # TODO: Where does this come from (?)
        audio_nb_samples: int = 1024
    ):
        # TODO: By now we are using just two video
        # tracks to test the composition
        # TODO: We need to be careful with the
        # priority, by now its defined by its
        # position in the array
        self.tracks: list[Track] = [
            Track(
                size = size,
                fps = fps,
                audio_fps = audio_fps,
                # TODO: I need more info about the audio
                # I think
                audio_nb_samples = audio_nb_samples
            ),
            Track(
                size = size,
                fps = fps,
                audio_fps = audio_fps,
                # TODO: I need more info about the audio
                # I think
                audio_nb_samples = audio_nb_samples
            )
        ]
        """
        All the video tracks we are handling.
        """
        # TODO: Handle the other properties
        self.size = size
        self.fps = fps
        self.audio_fps = audio_fps

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
        # TODO: This is temporary logic by now 
        # just to be able to test mixing frames
        # from 2 different tracks at the same
        # time
        index = 1 * do_use_second_track

        self.tracks[index].add_video(video, t)

        return self
    
    # TODO: This method is not for the Track but
    # for the timeline, as one track can only
    # have consecutive elements
    def get_frame_at(
        self,
        t: float
    ) -> 'VideoFrame':
        """
        Get all the frames that are played at the
        't' time provided, but combined in one.
        """
        frames = (
            track.get_frame_at(t)
            for track in self.tracks
        )
        # TODO: Here I receive black frames because
        # it was empty, but I don't have a way to
        # detect those black empty frames because
        # they are just VideoFrame instances... I
        # need a way to know so I can skip them if
        # other frame in other track, or to know if
        # I want them as transparent or something

        # TODO: Combinate them, I send first by now
        return next(frames)
    
    def get_audio_frames_at(
        self,
        t: float
    ):
        # TODO: What if the different audio streams
        # have also different fps (?)
        frames = []
        for track in self.tracks:
            # TODO: Make this work properly
            audio_frames = track.get_audio_frames_at(t)

            # TODO: Combine them
            if audio_frames is not None:
                frames = audio_frames
                break
            
        #from yta_video_opengl.utils import get_silent_audio_frame
        #make_silent_audio_frame()
        for frame in frames:
            yield frame
            
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

        from yta_video_opengl.writer import VideoWriter
        from yta_video_opengl.utils import get_black_background_video_frame, get_silent_audio_frame

        writer = VideoWriter('test_files/output_render.mp4')
        # TODO: This has to be dynamic according to the
        # video we are writing
        writer.set_video_stream(
            codec_name = 'h264',
            fps = self.fps,
            size = self.size,
            pixel_format = 'yuv420p'
        )
        
        writer.set_audio_stream(
            codec_name = 'aac',
            fps = self.audio_fps
        )
        
        audio_pts = 0
        for t in get_ts(start, end, self.fps):
            frame = self.get_frame_at(t)

            # We need to adjust our output elements to be
            # consecutive and with the right values
            # TODO: We are using int() for fps but its float...
            frame.time_base = Fraction(1, int(self.fps))
            #frame.pts = int(video_frame_index / frame.time_base)
            frame.pts = int(t / frame.time_base)

            # TODO: We need to handle the audio
            writer.mux_video_frame(
                frame = frame
            )

            #print(f'    [VIDEO] Here in t:{str(t)} -> pts:{str(frame.pts)} - dts:{str(frame.dts)}')

            num_of_audio_frames = 0
            for audio_frame in self.get_audio_frames_at(t):
                # TODO: The track gives us empty (black)
                # frames by default but maybe we need a
                # @dataclass in the middle to handle if
                # we want transparent frames or not and/or
                # to detect them here because, if not,
                # they are just simple VideoFrames and we
                # don't know they are 'empty' frames

                # We need to adjust our output elements to be
                # consecutive and with the right values
                # TODO: We are using int() for fps but its float...
                audio_frame.time_base = Fraction(1, int(self.audio_fps))
                #audio_frame.pts = int(audio_frame_index / audio_frame.time_base)
                audio_frame.pts = audio_pts
                # We increment for the next iteration
                audio_pts += audio_frame.samples
                #audio_frame.pts = int(t + (audio_frame_index * audio_frame.time_base) / audio_frame.time_base)

                #print(f'[AUDIO] Here in t:{str(t)} -> pts:{str(audio_frame.pts)} - dts:{str(audio_frame.dts)}')

                num_of_audio_frames += 1
                print(audio_frame)
                writer.mux_audio_frame(audio_frame)
            print(f'Num of audio frames: {str(num_of_audio_frames)}')

        writer.mux_video_frame(None)
        writer.mux_audio_frame(None)
        writer.output.close()


# TODO: I don't want to have this here
def get_ts(
    start: float,
    end: float,
    fps: int
):
    """
    Obtain, without using a Progression class and
    importing the library, a list of 't' time
    moments from the provided 'start' to the also
    given 'end', with the 'fps' given as parameter.
    """
    dt = 1.0 / fps
    times = []

    t = start
    while t <= end:
        times.append(t + 0.000001)
        t += dt

    return times