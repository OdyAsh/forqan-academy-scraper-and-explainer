# %%
# autoreload reloads modules automatically before entering the execution of code typed at the IPython prompt
# however, if you define an entirely new function or class in the imported modules (i.e., .py files)
# then you'll need to re-run the 'from .. import' statements in the notebook
try:    
    from IPython import get_ipython
    ipython = get_ipython()
    ipython.run_line_magic('load_ext', 'autoreload')
    ipython.run_line_magic('autoreload', '2')
except Exception as e:
    pass

# %% 
# # Imports

import os
import re
from typing import List, Tuple

from dotenv import load_dotenv
from bs4 import BeautifulSoup

# from forqan_academy_scraper.scraper import login, \
#     get_forqan_modules_urls_using_regex, \
#     get_modules_info_using_regex, \
#     get_lessons_name_and_urls_using_regex

from forqan_academy_scraper import scraper as fsc

from logaru_logger.the_logger import logger
from odyash_general_functions.odyash_general_functions import save_data

# %%
# Global variables

# load the environment variables
load_dotenv()

# %% 
logger.info("Welcome to Forqan scraper & Explainer!")

session, login_response_html_string = fsc.login()

# %% 
# getting the URLs of each Forqan module using regex
forqan_modules_urls = fsc.get_forqan_modules_urls_using_regex(login_response_html_string)

# %%
# getting the info (tuple) of each module page
modules_name_and_html = fsc.get_modules_info_using_regex(forqan_modules_urls, session)

# %%
# getting the lessons info from each module page
lessons_names_and_urls_per_module = fsc.get_lessons_name_and_urls_using_regex(modules_name_and_html)

# %%

# get other overview/video-urls/pdf-metadata from each lesson of each module
forqan_lessons_info = fsc.get_video_urls_descriptions_and_pdf_metadata(modules_name_and_html, 
                                                                    forqan_modules_urls, 
                                                                    lessons_names_and_urls_per_module,
                                                                    session)

# %%
# TODO: delete draft code below (or migrate to save_data() when extension is pdf)
import requests

def download_file_from_google_drive(drive_url, save_path):
    """
    Download a file from Google Drive given its URL and save it to a specified path.
    
    Args:
        drive_url (str): The URL of the Google Drive file.
        save_path (str): The path (including filename) where the file should be saved.
    """
    response = requests.get(drive_url)
    if response.status_code == 200:
        with open(save_path, 'wb') as f:
            f.write(response.content)
        print(f"File has been downloaded and saved as {save_path}")
    else:
        print("Failed to download the file.")

# Example usage
drive_url = "https://drive.google.com/uc?id=1upcHIK9F18Qe-PwRr2qr1os3k3CcjSqz"
save_path = "downloaded_file.pdf"  # You need to assign a name manually
download_file_from_google_drive(drive_url, save_path)

# %%
