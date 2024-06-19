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

# save the pdfs
fsc.download_revision_pdfs(forqan_lessons_info)

# %%
# TODO: add code after the imports to just fetch the `forqan_lessons_info` from a local json file, and then PDF text extraction code to be written below
#       also, check possible pdf text extraction libraries like PyMuPDF, pdfplumber, etc... relevant links:
#       4-o
#       https://github.com/zaakki-ahamed/Arabic_OCR_From_PDF/blob/main/Arabic_OCR.py
#       https://pymupdf.readthedocs.io/en/latest/installation.html , https://pymupdf.readthedocs.io/en/latest/rag.html
#       https://github.com/jsvine/pdfplumber?tab=readme-ov-file

# %%
