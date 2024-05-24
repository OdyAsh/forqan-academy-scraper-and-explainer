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
import requests
from bs4 import BeautifulSoup as bs

from forqan_academy_scraper.scraper import login
from logaru_logger.the_logger import logger
from odyash_general_functions.odyash_general_functions import save_data

# %% 
logger.info("Welcome to Forqan scraper & Explainer!")

session, response = login()

login_response_html_string = response.text
logger.debug(f"login_response_html_string: {login_response_html_string[-100:]}")
save_data(login_response_html_string, "login_response_html_string")

# %% 
# Regular expression pattern to match 'a' tags with class 'ld-item-name'
pattern = r'<a href="(.*?)" class="ld-item-name">'

# Find all matches in the HTML string
module_urls = re.findall(pattern, login_response_html_string)

logger.debug(f"module_urls: {module_urls}")
save_data(module_urls, "module_urls")

# Now we have a list of URLs, we can loop through them and get the HTML of each module page
modules_name_and_html = []
for url in module_urls:
    response = session.get(url)
    module_name = re.search(r'<title>(.*?)&#8211;', response.text) #TODO: mention that it's tricky to get this regex since arabic switches up the order of the text displayed and how you removed "(1)"
    if module_name:
        module_name = module_name.group(1)
        module_name = re.sub(r'\(\d+\)', '', module_name).strip() # as sometimes the string will be like this: " مادة التفسير (1)"
    else:
        module_name = "No module name found"
    logger.info(f"Module name: {module_name}")
    modules_name_and_html.append((module_name, response.text))
save_data(modules_name_and_html[0][1], "module_pages_first_url_response")
save_data(modules_name_and_html[-1][1], "module_pages_last_url_response")



# %%
    
# Getting the lesson URLs from each module page
    
# Regular expression pattern to match the 'a' tag with the required class
a_tag_pattern = r'<a class="ld-item-name.*?" href="(.*?)">.*?<span class="ld-topic-title">(.*?)</span>'
for module in modules_name_and_html:
    module_name, module_page = module
    
    # Now 'lessons_matched' is a list of tuples, where each tuple contains the href URL and the text inside the 'span' tag
    lessons_matched = re.findall(a_tag_pattern, module_page, re.DOTALL)
    
    logger.info(f"Lessons matched for module {module_name}:\n{lessons_matched}\n")
    save_data(lessons_matched, f"lessons_matched")

# logger.info(response.status_code)
# logger.info(response)
# logger.info(response.text)

# # store the response in a txt file
# with open("response.txt", "w", encoding='utf-8') as file:
#     file.write(response.text)

# %%
