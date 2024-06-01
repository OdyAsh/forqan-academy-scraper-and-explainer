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
save_data(forqan_modules_urls, "forqan_modules_urls", file_extension="json")

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
## TEMP. TODO: Refactor when the final structure of the data is known
from bs4 import BeautifulSoup

tmp_links = [
    # no desc. header
    r'https://forqanacademy.com/topic/%d8%a7%d9%84%d9%85%d8%ad%d8%a7%d8%b6%d8%b1%d8%a9-1-%d8%a7%d9%84%d9%85%d8%b1%d8%ad%d9%84%d8%a9-%d8%a7%d9%84%d9%85%d9%83%d9%8a%d8%a9/',
    
    # h4 li desc.
    r'https://forqanacademy.com/topic/%d8%a7%d9%84%d9%85%d8%ad%d8%a7%d8%b6%d8%b1%d8%a9-6-%d8%ba%d8%b2%d9%88%d8%a9-%d8%a7%d9%84%d8%a3%d8%ad%d8%b2%d8%a7%d8%a8/',
    r'https://forqanacademy.com/topic/%d8%a7%d9%84%d9%85%d8%ad%d8%a7%d8%b6%d8%b1%d8%a9-2-%d8%a7%d9%84%d8%af%d8%b1%d9%88%d8%b3-%d8%a7%d9%84%d9%85%d8%b3%d8%aa%d9%81%d8%a7%d8%af%d8%a9-%d9%85%d9%86-%d8%a7%d9%84%d9%85%d8%b1%d8%ad%d9%84%d8%a9/',
    
    # p desc.
    r'https://forqanacademy.com/topic/%d8%a7%d9%84%d9%85%d8%ad%d8%a7%d8%b6%d8%b1%d8%a9-8-%d8%ba%d8%b2%d9%88%d8%a9-%d8%a8%d9%86%d9%8a-%d9%82%d8%b1%d9%8a%d8%b8%d8%a9/'
]
# checking out html of a single lesson page without headers
resp = session.get(tmp_links[3])
lesson_html = resp.text

soup = BeautifulSoup(lesson_html, 'html.parser')
div_tag = soup.find('div', class_='ld-tab-content ld-visible lesson-materials-btns')
text_content = div_tag.get_text(separator='\n\n', strip=True)

# Print the text content
print(text_content)

save_data(text_content, 
            "04_content", 
            dir_name="../logs/temp_outputs_for_visualizing", 
            add_intermediate_counter_prefix=False,
            file_extension="txt")
# %%
