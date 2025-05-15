"""
When uploading a single video, the user should fill the following forms:

1. Annotate video - mark sections that display climbing.
2. Add climb - input the route of the video and the climbing facts.
  - If desired, the user can add/edit their opinion on the route.
3. Return to last URL.

If the user uploads multiple videos, the user must first sort them before going to the
annotation page.
"""

import os
import subprocess
import json
import math
from time import sleep
import sys

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sqlalchemy import text

from .conftest import (
    HOME_TITLE,
    HOME_URL,
    EXISTING_OBJECTS,
    CLIMBER_ID,
    get_existing_route,
    fill_form,
)


def test_add_video(driver, db_session, started_session_id) -> None:
    """
    Tests that the user can upload and annotate a single video.
    as it is deleted with delete_video_info before redirecting the user to the home
    page (see the end of videos.annotate_video)
    """
    # go to the home page
    if driver.current_url not in [HOME_URL, HOME_URL + "/"]:
        driver.get(HOME_URL)
        WebDriverWait(driver, 10).until(EC.title_is(HOME_TITLE))

    # open the form to add videos
    driver.find_element(By.ID, "add_video").click()
    # create 8-second video with ffmpeg
    video_path = "/tmp/test_video.mp4"
    ffmpeg_command = [
        "ffmpeg",
        "-y",
        "-f",
        "lavfi",
        "-i",
        "color=c=black:s=640x480:d=8",
        "-pix_fmt",
        "yuv420p",
        video_path,
    ]
    subprocess.run(ffmpeg_command, check=True)

    # upload the video and wait until it is loaded
    file_input = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
    )
    file_input.send_keys(video_path)

    # video display does not work in headless mode
    if "debugpy" in sys.modules:
        WebDriverWait(driver, 15).until(
            lambda d: d.execute_script(
                "return document.getElementById('videoPlayer').readyState"
            )
            == 4
        )

        # the video should have a duration of 8 seconds
        video_player = driver.find_element(By.ID, "videoPlayer")
        duration = driver.execute_script("return arguments[0].duration;", video_player)
        assert abs(duration - 8) < 0.2
    else:
        sleep(5)

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
            "grade": "13",
            "rating": 5,
        },
    )
    assert form_accepted

    # check that the climb was added with one attempt
    sql_query = text(
        f"""
        SELECT id,n_attempts,sent FROM climb
        WHERE session_id = {started_session_id}
        AND route_id = {route_id};
        """
    )
    results = db_session.execute(sql_query).fetchall()
    assert len(results) == 1
    climb_id, n_attempts, sent = results[0]
    assert n_attempts == 1
    assert not sent

    # check that an opinion for the route was created
    sql_query = text(
        f"""
        SELECT grade_id,comment,landing,rating FROM opinion
        WHERE climber_id = {CLIMBER_ID}
        AND route_id = {route_id};
        """
    )
    results = db_session.execute(sql_query).fetchall()
    assert len(results) == 1
    grade_id, comment, landing, rating = results[0]
    assert grade_id == 13
    assert comment is None
    assert landing == 3
    assert rating == 5

    # check that the video was recorded in the database
    results = db_session.execute(
        text("SELECT id, climb_id, base_fname FROM video")
    ).fetchall()
    assert len(results) == 1
    video_id, video_climb_id, base_fname = results[0]
    assert video_climb_id == climb_id

    # check that the attempt was recorded in the database
    results = db_session.execute(
        text("SELECT video_id, attempt_number, start, end, sent FROM video_attempt")
    ).fetchall()
    assert len(results) == 1
    attempt_video_id, attempt_number, start, end, sent = results[0]
    assert attempt_video_id == video_id
    assert attempt_number == 0
    assert start == 1
    assert end == 5
    assert not sent

    # check that the video exists
    video_fname = f"{base_fname}_{attempt_number}.mp4"
    assert os.path.exists(os.path.join("./files/videos", video_fname))

    # check that the video's duration is correct
    ffprobe_command = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "format=duration",
        "-of",
        "json",
        os.path.join("./files/videos", video_fname),
    ]
    result = subprocess.run(
        ffprobe_command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=True,
    )
    duration_info = json.loads(result.stdout)
    file_duration = float(duration_info["format"]["duration"])
    assert math.isclose(file_duration, 4.0, rel_tol=0.2)
