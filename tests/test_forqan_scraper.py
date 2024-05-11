# test_forqan_scraper.py
from dotenv import load_dotenv
import os
import requests

from forqan_academy_scraper.scraper import ForqanScraper
from logaru_logger.the_logger import logger


def test_login() -> None:
    load_dotenv()
    username = os.getenv('MY_USERNAME')
    password = os.getenv('MY_PASSWORD')
    logger.info(ForqanScraper)
    session, response = ForqanScraper.login(username, password)
    logger.info(f"{session}\n{response}")
    assert isinstance(session, requests.sessions.Session)
    assert isinstance(response, requests.models.Response)

