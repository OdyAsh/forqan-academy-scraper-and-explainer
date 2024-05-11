# %%
# autoreload reloads modules automatically before entering the execution of code typed at the IPython prompt
# however, if you define an entirely new function or class in the imported modules (i.e., .py files)
# then you'll need to re-run the 'from .. import' statements in the notebook
try:    
    if '__file__' in globals():
        raise
    from IPython import get_ipython
    ipython = get_ipython()
    print('wwwoooow')
    ipython.run_line_magic('load_ext', 'autoreload')
    ipython.run_line_magic('autoreload', '2')
except Exception as e:
    print('file is founddd')
    pass

# %% 
# # Imports

import re
import requests
from bs4 import BeautifulSoup as bs

from forqan_academy_scraper.scraper import login
from logaru_logger.the_logger import logger

# %% 
logger.info("Welcome to Forqan scraper & Explainer!")

session, response = login()

# %% 

# Assuming response.text is your HTML string
login_response_html_string = response.text

# Regular expression pattern to match 'a' tags with class 'ld-item-name'
pattern = r'<a href="(.*?)" class="ld-item-name">'

# Find all matches in the HTML string
module_urls = re.findall(pattern, login_response_html_string)

print(module_urls)

# Now we have a list of URLs, we can loop through them and get the HTML of each module page
module_pages = []
for url in module_urls:
    response = sess.get(url)
    module_pages.append(response.text)


# %%
    
# Getting the lesson URLs from each module page
    
# Regular expression pattern to match the 'a' tag with the required class
a_tag_pattern = r'<a class="ld-item-name.*?" href="(.*?)">.*?<span class="ld-topic-title">(.*?)</span>'
for module_page in module_pages:
    # Now 'lessons_matched' is a list of tuples, where each tuple contains the href URL and the text inside the 'span' tag
    lessons_matched = re.findall(a_tag_pattern, module_page, re.DOTALL)
    
    # print("For module: " + module_page)
    print("Lessons matched: ")
    print(lessons_matched)
    print()

# print(response.status_code)
# print(response)
# print(response.text)

# # store the response in a txt file
# with open("response.txt", "w", encoding='utf-8') as file:
#     file.write(response.text)

# %%
