from collections import namedtuple

from flask import (
    render_template,
    session as flask_session,
    request,
    redirect,
    url_for,
    abort,
)
from flask_login import current_user, login_required

from myclimbz.models import Session, Area


@login_required
def render(*args, **kwargs) -> str:
    """
    Our own wrapper for the render_template function from Flask, adding arguments that are
    always required.

    - A title is required.
    - If an error is defined in the session, it is popped and added to the kwargs.
    - If an open session is defined in the session, it is added to the kwargs.
    - Add the current user's name and ID to the kwargs.
    - Save the URL in the session, unless it starts with "edit_".
    """

    # ensure title exists and add video info if neededs
    if "title" not in kwargs:
        abort(500)

    if "video_upload_status" in flask_session:
        video_idx, n_videos = flask_session["video_upload_status"]
        kwargs["title"] += f" (video {video_idx+1}/{n_videos})"

    # add other kwargs
    kwargs["error"] = flask_session.pop("error", None)
    kwargs["username"] = current_user.name
    kwargs["user_id"] = current_user.id
    kwargs["user_role"] = current_user.role
    kwargs["user_grade_scale"] = current_user.grade_scale

    # discern form pages from the rest
    path = request.path
    if (
        path.startswith("/edit_")
        or path.startswith("/add_")
        or path.startswith("/sort_")
        or path.startswith("/annotate_")
    ):
        kwargs["is_form"] = True
    else:
        kwargs["is_form"] = False
        flask_session["call_from_url"] = path

    session_id = flask_session.get("session_id", None)
    if session_id is not None:
        if session_id == "project_search":
            area = Area.query.get(flask_session["area_id"])
            session_obj = namedtuple("Session", ["is_project_search", "area"])(
                True, namedtuple("Area", ["name"])(area.name)
            )
            kwargs["open_session"] = session_obj
        else:
            kwargs["open_session"] = Session.query.get(session_id)

    return render_template(
        *args,
        **kwargs,
    )


def redirect_after_form_submission(*args, **kwargs) -> str:
    """
    - If the user is currently annotating videos and there are videos
        that remain to be annotated, the user is redirected to the next
        video.
    - Otherwise, the user is is redirected to "call_from_url" page.
    """
    video_id = flask_session.get("video_id", None)
    if video_id:
        video_idx, n_videos = flask_session["video_upload_status"]
        if video_idx + 1 < n_videos:
            print(video_idx, n_videos)
            print("CALLING")
            url = url_for(
                "videos.annotate_video", n_videos=n_videos, video_idx=video_idx + 1
            )
            print(url)
            return redirect(
                url_for(
                    "videos.annotate_video", n_videos=n_videos, video_idx=video_idx + 1
                )
            )
        else:
            delete_video_info()

    return redirect(flask_session.pop("call_from_url"))


def delete_video_info():
    """
    Delete video info from flask_session. The files are not deleted.
    """
    for session_key in ["video_id", "video_upload_status", "video_fnames"]:
        if session_key in flask_session:
            del flask_session[session_key]
