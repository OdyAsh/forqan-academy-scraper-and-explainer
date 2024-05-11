import os
import functools
from typing import Dict, List, Optional, Tuple, Union, Literal, Any
import requests
from requests import Session, Response

from logaru_logger.the_logger import logger, log_decorator


# Define a partial function called log_partial_decorator,
# since I'm too lazy to write the arguments each time in "@log_decorator(...)"
log_partial_decorator = functools.partial(log_decorator, 
                                          exit=(os.getenv('DEBUG', '1')=='1'),
                                          level=(os.getenv('DEBUG', '1')=='1'))


@log_decorator()
def login(username: str = None, 
            password: str = None) -> Tuple[Session, Response]:
    """
    Logs into the Forqan Academy website and returns a session and the response.

    This function logs into the Forqan Academy website using the provided username 
    and password, and returns a session where the user is logged in and the response 
    from the POST request to the login URL.

    Most of the code defined below (e.g., cookies, headers, data) was copied 
    from the network tab in the browser's developer tools. Specifically, while 
    opening the dev. tool, you sign into the website, then you go to the 'Network' 
    tab, and you can see the requests made by the browser. You can then right-click 
    on the request which sends the login data and select 'Copy as cURL'. You can 
    then paste the copied cURL command into a tool like https://curlconverter.com/python/ 
    to convert it to Python requests code which is similar to the code defined in 
    this function. Example of how to do this is in this article: 
    https://dev.to/serpapi/13-ways-to-scrape-any-public-data-from-any-website-1bn9#xhr-requests

    Args:
        username (str): The username to log in with.
        password (str): The password to log in with.

    Returns:
        Tuple[Session, Response]: A tuple where the first element is a 
        requests.Session object where the user is logged in, and the second 
        element is the Response object from the POST request to the login URL.
    """

    cookies = {
        'wordpress_test_cookie': 'WP+Cookie+check',
    }

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9,en-GB;q=0.8,ar;q=0.7',
        'cache-control': 'max-age=0',
        'content-type': 'application/x-www-form-urlencoded',
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

    if username is None:
        username = os.getenv('MY_USERNAME')
    if password is None:
        password = os.getenv('MY_PASSWORD')

    data = {
        'username-17384': username,
        'user_password-17384': password,
        'form_id': '17384',
        'um_request': '',
        '_wpnonce': 'b92a993bec',
        '_wp_http_referer': '/login/',
        'rememberme': '1',
    }

    # Create a session object
    sess = requests.Session()

    response = sess.post('https://forqanacademy.com/login/', cookies=cookies, headers=headers, data=data)

    return sess, response