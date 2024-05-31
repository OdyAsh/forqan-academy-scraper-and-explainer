# %%
# autoreload reloads modules automatically before entering the execution of code typed at the IPython prompt
# however, if you define an entirely new function or class in the imported modules (i.e., .py files)
# then you'll need to re-run the 'from .. import' statements in the notebook
try:    
    if '__file__' in globals():
        raise
    from IPython import get_ipython
    ipython = get_ipython()
    ipython.run_line_magic('load_ext', 'autoreload')
    ipython.run_line_magic('autoreload', '2')
except Exception as e:
    pass

# %% 
# # Imports

import re
from typing import List, Tuple

from forqan_academy_scraper.scraper import (
    login, 
    get_forqan_modules_urls_using_regex, 
    get_modules_info_using_regex,
    get_lessons_info_using_regex
)
from logaru_logger.the_logger import logger
from odyash_general_functions.odyash_general_functions import save_data

# %% 
logger.info("Welcome to Forqan scraper & Explainer!")

session, response = login()

login_response_html_string = response.text
logger.debug(f"login_response_html_string: {login_response_html_string[-100:]}")
save_data(login_response_html_string, "login_response_html_string")

# %% 
# getting the URLs of each Forqan module using regex
forqan_modules_urls = get_forqan_modules_urls_using_regex(login_response_html_string)
logger.debug(f"forqan_modules_urls: {forqan_modules_urls}")
save_data(forqan_modules_urls, "forqan_modules_urls")

# %%
# getting the info (tuple) of each module page
modules_name_and_html = get_modules_info_using_regex(forqan_modules_urls, session)

# saving intermediate outputs for debugging purposes
save_data(modules_name_and_html[0][1], "module_pages_first_url_response")
save_data(modules_name_and_html[-1][1], "module_pages_last_url_response")

# %%
# getting the lessons info from each module page
lessons_info = get_lessons_info_using_regex(modules_name_and_html)

# saving intermediate outputs for debugging purposes
save_data(lessons_info, "lessons_info", file_extension="json")

# %%
