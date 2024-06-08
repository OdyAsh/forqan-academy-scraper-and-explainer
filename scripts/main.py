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

session, response = fsc.login()

login_response_html_string = response.text
logger.debug(f"login_response_html_string: {login_response_html_string[-100:]}")
save_data(login_response_html_string, "login_response_html_string")

# %% 
# getting the URLs of each Forqan module using regex
forqan_modules_urls = fsc.get_forqan_modules_urls_using_regex(login_response_html_string)
logger.debug(f"forqan_modules_urls: {forqan_modules_urls}")
save_data(forqan_modules_urls, "forqan_modules_urls", file_extension="json")

# %%
# getting the info (tuple) of each module page
modules_name_and_html = fsc.get_modules_info_using_regex(forqan_modules_urls, session)

# saving intermediate outputs for debugging purposes
save_data(modules_name_and_html[0][1], "module_pages_first_url_response")
save_data(modules_name_and_html[-1][1], "module_pages_last_url_response")

# %%
# getting the lessons info from each module page
lessons_names_and_urls_per_module = fsc.get_lessons_name_and_urls_using_regex(modules_name_and_html)

# saving intermediate outputs for debugging purposes
save_data(lessons_names_and_urls_per_module, "lessons_names_and_urls_per_module", file_extension="json")

# %%
# getting the video URLs and descriptions for each lesson
final_forqan_info = {}
for i, ((module_name, _), module_url) in enumerate(zip(modules_name_and_html, forqan_modules_urls)):
    module_num = f"{i+1:02d}"
    logger.debug(f"module num and name: {module_num}: {module_name}")
    cur_module_lessons = lessons_names_and_urls_per_module[i]
    final_forqan_info[f"module_{module_num}"] = {"name": module_name, "url": module_url, "lessons": []}
    
    for lesson_name, lesson_url in cur_module_lessons:
        logger.debug(f"lesson_name: {lesson_name}")
        logger.debug(f"lesson_url: {lesson_url}")
        lesson_response = session.get(lesson_url)
        lesson_html_string = lesson_response.text
        soup = BeautifulSoup(lesson_html_string, 'html.parser')
        lesson_content = {}

        if re.search(r'يرجى العودة وإكمال', lesson_html_string) or re.search(r'متوفر في', lesson_html_string):
            lesson_content['not_available'] = True
            logger.debug(f"lesson_name: {lesson_name} is not available yet")
        elif "المحاضرات" in lesson_name:
            logger.debug(f"revision lesson_title: {lesson_name}")
            pdf_name = lesson_name.replace('&#8211;', '-')
            invalid_chars = r'[\\/:*?"<>|]'
            pdf_name = re.sub(invalid_chars, '', lesson_name)
            lesson_content['pdf_name'] = pdf_name
            logger.debug(f"its pdf_name: {pdf_name}")

            pdf_url = soup.find('a', class_='ui button fluid primary btn text-link')['href']
            lesson_content['pdf_url'] = pdf_url
            logger.debug(f"pdf_url: {pdf_url}")
        else:
            video_url = soup.find('iframe')['src']
            lesson_content['video_url'] = video_url
            logger.debug(f"video_url: {video_url}")

            div_tag = soup.find('div', class_='ld-tab-content ld-visible lesson-materials-btns')
            text_content = div_tag.get_text(separator='\n\n', strip=True)
            # a keyword which indicates the end of the section describing the video
            # check _unused_manually_visualize_lesson_desc() for details
            desc_termination_keyword = "لمشاهدة"
            video_description = text_content.split(desc_termination_keyword)[0].strip()
            lesson_content['video_description'] = video_description
            logger.debug(f"video_description: {video_description}")
        
        final_forqan_info[f"module_{module_num}"]["lessons"].append({
            "name": lesson_name,
            "url": lesson_url,
            **lesson_content
        })

# saving intermediate outputs for debugging purposes
save_data(final_forqan_info, "final_forqan_info", file_extension="json")


# %%
# create a dictionary with the following structure:
# {
#     "module_1": {
#         "name": "module_1_name",
#         "url": "module_1_URL",
#         "lessons": [
#             {
#                 "name": "lesson_1_name",
#                 "url": "lesson_1_URL",
#                 "video_url": "lesson_1_video_URL"
#                 "video_description": "lesson_1_video_description"
#             },
#             {
#                 ...
#             },
#             ...
#         ]
#     },
#     "module_2": {
#         ...
#     },
#     ...
# }



# %%
