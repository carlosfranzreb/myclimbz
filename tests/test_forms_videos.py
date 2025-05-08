"""
When uploading a single video, the user should fill the following forms:

1. Annotate video - mark sections that display climbing.
2. Add climb - input the route of the video and the climbing facts.
  - If desired, the user can add/edit their opinion on the route.
3. Return to last URL.

If the user uploads multiple videos, the user must first sort them before going to the
annotation page.
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sqlalchemy import text

from .conftest import (
    HOME_TITLE,
    HOME_URL,
    EXISTING_OBJECTS,
    get_existing_route,
    fill_form,
)
import subprocess


def test_add_video(driver, db_session, started_session_id) -> None:
    """
    Tests that the user can upload and annotate a single video.
    as it is deleted with delete_video_info before redirecting the user to the home
    page (see the end of videos.annotate_video)
    """
    # go to the home page
    if driver.current_url not in [HOME_URL, HOME_URL + "/"]:
        driver.get(HOME_URL)
        WebDriverWait(driver, 30).until(EC.title_is(HOME_TITLE))

    # open the form to add videos
    driver.find_element(By.ID, "add_videos").click()
    file_input = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
    )
    # create 2-second video with ffmpeg
    video_path = "/tmp/test_video.mp4"
    ffmpeg_command = [
        "ffmpeg",
        "-y",
        "-f",
        "lavfi",
        "-i",
        "color=c=black:s=640x480:d=2",
        "-pix_fmt",
        "yuv420p",
        video_path,
    ]
    subprocess.run(ffmpeg_command, check=True)

    # upload the video
    file_input.send_keys(video_path)
    WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit']"))
    ).click()
    WebDriverWait(driver, 30).until(
        lambda d: d.current_url == HOME_URL + "/annotate_video/1/0"
    )

    # the video should have 5 frames, as we are capturing 2 fps per default
    total_frames_element = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.ID, "total-frames"))
    )
    assert total_frames_element.text.strip() == "5"

    # fill the form with a climbing section from 1 to 5 and submit
    route_name, route_id = get_existing_route(
        db_session, EXISTING_OBJECTS["sector"], idx=1
    )
    form_accepted = fill_form(
        driver,
        None,
        {
            "name": route_name,
            "sections-0-start": 1,
            "sections-0-end": 5,
            "skip_opinion": True,
        },
    )
    assert form_accepted

    # check that the video and the attempt were added to the database
    for table in ["video", "video_attempt"]:
        query = text(f"SELECT COUNT(*) FROM {table}")
        n_rows = db_session.execute(query).fetchall()[0][0]
        assert n_rows == 1, table

    video_id = db_session.execute(text("SELECT id FROM video")).fetchall()[0][0]
    attempt = db_session.execute(
        text("SELECT video_id, start_frame, end_frame FROM video_attempt")
    ).fetchall()[0]
    assert attempt[0] == video_id
    assert attempt[1] == 1
    assert attempt[2] == 5

    # check that the climb was added with one attempt
    sql_query = text(
        f"""
        SELECT n_attempts,sent FROM climb
        WHERE session_id = {started_session_id}
        AND route_id = {route_id};
        """
    )
    results = db_session.execute(sql_query).fetchall()
    assert len(results) == 1
    n_attempts, sent = results[0]
    assert n_attempts == 1
    assert not sent
