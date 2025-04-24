import os
import subprocess

from flask import session as flask_session, current_app, abort, url_for, redirect
from flask_login import current_user
import cv2

from myclimbz.models import Video


def check_access_to_file(filename: str, ignore_session: bool = False):
    """
    Check that the user is the owner of the videos, and that the session of the videos
    is currently open.
    TODO: this may belong in __init__.py, where all access rights are handled.

    Args:
        filename as a string. It is expected to define the user id and the session id
        as the first two elements of the name, separated by underscores.
    """
    user_id, session_id = [int(n) for n in filename.split("_", 2)[:2]]

    if current_user.id != user_id:
        flask_session["error"] = "You are not the owner of this file."
        abort(403)

    if not ignore_session and session_id != flask_session["session_id"]:
        flask_session["error"] = (
            "The session is closed. Redirecting to the session's page."
        )
        return redirect(url_for("sessions.page_session", session_id=session_id))


def get_video_frames(video_path: str, fps: int = 2) -> tuple[str, int, int, int]:
    """
    - Extract and dump `fps` frames per second from the video.
    - Return the prefix of the frames filenames, the number of frames and the FPS of the
    video and the number of frames extracted per second of video.
    - The frames are not extracted again if the filenames exist.
    """

    cap = cv2.VideoCapture(video_path)
    video_fps = cap.get(cv2.CAP_PROP_FPS)
    frame_interval = int(video_fps / fps)
    frames = list()

    # if the frames were extracted previously, return the path to them
    video_fname = os.path.splitext(os.path.basename(video_path))[0]
    frames_fname_prefix = f"{video_fname}_fps{fps}_frame"
    n_frames = [
        None
        for fname in os.listdir(current_app.config["FRAMES_FOLDER"])
        if fname.startswith(frames_fname_prefix)
    ]
    if len(n_frames) > 0:
        return frames_fname_prefix, len(n_frames), video_fps, fps

    # extract frames
    frame_count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if frame_count % frame_interval == 0:
            frames.append(reduce_frame(frame))
        frame_count += 1

    cap.release()

    # dump frames
    for idx, frame in enumerate(frames):
        cv2.imwrite(
            os.path.join(
                current_app.config["FRAMES_FOLDER"],
                f"{frames_fname_prefix}{idx}.jpg",
            ),
            frame,
        )

    return frames_fname_prefix, len(frames), video_fps, fps


def trim_video(video: Video, start: int, end: int):
    """
    Extract and store from the video starting at frame `start` and ending
    at frame `end`. The clip is stored with the same name as the original video,
    with a suffix stating the start and end frames of the clip.

    TODO: the trimmed video is a bit longer than it should.
    """

    # build input and output paths
    input_path = os.path.join(current_app.config["VIDEOS_FOLDER"], video.fname)
    base, ext = os.path.splitext(input_path)
    output_path = f"{base}_trim{start}-{end}{ext}"
    if os.path.exists(output_path):
        return

    # trim the video
    start_seconds = start / video.fps_taken
    duration = (end - start) / video.fps_taken
    command = [
        "ffmpeg",
        "-i",
        input_path,
        "-ss",
        str(start_seconds),
        "-t",
        str(duration),
        output_path,
    ]
    subprocess.run(command, check=True)


def reduce_frame(frame: cv2.typing.MatLike, max_size: int = 512) -> cv2.typing.MatLike:
    """
    Reduce the resolution of the frames to a max height/width of 512 pixels,
    without altering the shape.
    """
    height, width = frame.shape[:2]
    scale = min(512 / float(height), 512 / float(width))
    if scale < 1:
        new_dims = (int(width * scale), int(height * scale))
        return cv2.resize(frame, new_dims, interpolation=cv2.INTER_AREA)
