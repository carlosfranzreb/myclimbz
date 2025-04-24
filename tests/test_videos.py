"""
When uploading a single video, the user should fill the following forms:

1. Annotate video - mark sections that display climbing.
2. Add climb - input the route of the video and the climbing facts.
  - If desired, the user can add/edit their opinion on the route.
3. Return to last URL.

If the user uploads multiple videos, the user must first sort them before going to the
annotation page.
"""

from typing import Generator
from time import sleep
from datetime import datetime

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from sqlalchemy import text

from .conftest import HOME_TITLE, HOME_URL, CLIMBER_ID, SLEEP_TIME, IS_CI
from .test_forms import fill_form, started_session_id
import subprocess


def test_add_video(driver, db_session, started_session_id) -> None:
    """
    Tests that the user can upload and annotate a single video.
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
        "color=c=black:s=160x120:d=2",
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

    # mark a climbing section from 1 to 5 and submit
    driver.find_element(By.ID, "sections-0-start").send_keys("1")
    driver.find_element(By.ID, "sections-0-end").send_keys("5")
    driver.find_element(By.XPATH, "//input[@type='submit']").click()

    # check that the user is sent to the "Add climb" form
    WebDriverWait(driver, 30).until(lambda d: d.current_url == HOME_URL + "/add_climb")

    # check that the video was added to the database
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
