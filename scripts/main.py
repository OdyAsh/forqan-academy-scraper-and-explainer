# %% 
# # Imports

import requests
import re


# %% 
print("Welcome to Forqan scraper & Explainer!")
# # logging in
# print("Enter your email or mobile number: ")
# email = input()
# print("Enter your password: ")
# password = input()


cookies = {
    'wordpress_test_cookie': 'WP+Cookie+check',
}

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9,en-GB;q=0.8,ar;q=0.7',
    'cache-control': 'max-age=0',
    'content-type': 'application/x-www-form-urlencoded',
    # 'cookie': 'wordpress_test_cookie=WP+Cookie+check',
    'origin': 'https://forqanacademy.com',
    'priority': 'u=0, i',
    'referer': 'https://forqanacademy.com/login/',
    'sec-ch-ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
}

data = {
    'username-17384': 'XXX',
    'user_password-17384': 'XXX',
    'form_id': '17384',
    'um_request': '',
    '_wpnonce': 'b92a993bec',
    '_wp_http_referer': '/login/',
    'rememberme': '1',
}

# Create a session object
sess = requests.Session()

response = sess.post('https://forqanacademy.com/login/', cookies=cookies, headers=headers, data=data)

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
