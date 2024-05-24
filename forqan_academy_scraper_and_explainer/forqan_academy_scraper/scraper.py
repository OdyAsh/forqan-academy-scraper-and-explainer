import os
import functools
from typing import Dict, List, Optional, Tuple, Union, Literal, Any
import requests
from requests import Session, Response
import re

from logaru_logger.the_logger import logger, log_decorator
from odyash_general_functions.odyash_general_functions import save_data

# Define a partial function called log_partial_decorator,
# since I'm too lazy to write the arguments each time in "@log_decorator(...)"
log_partial_decorator = functools.partial(log_decorator, 
                                        exit=(os.getenv('DEBUG', '1')=='1'),
                                        level=(os.getenv('DEBUG', '1')=='1'))


def _get_post_request_constants() -> Tuple[Dict[str, str], Dict[str, str], Dict[str, str]]:
    """
    Get the headers, data, and cookies obtained from the cURL command.

    This function returns the headers, data, and cookies obtained from the cURL command.

    Notes:
    - The "cookies", "headers", and "data" parts of the code below were copied 
    from the network tab in the browser's developer tools. 
        - Specifically, while opening the dev. tool, you sign into the website, then when you go to the 'Network' 
            tab, and you can see the requests made by the browser. 
        - You can then right-click on the request which sends the login data and select 'Copy as cURL (bash)'. 
        - You can then paste the copied cURL command into a tool like https://curlconverter.com/python/ 
            to convert it to Python requests code which is similar to the code defined in 
            this function. 
            - Example of how to do this is in this article: 
                https://dev.to/serpapi/13-ways-to-scrape-any-public-data-from-any-website-1bn9#xhr-requests

    Returns:
        Tuple[Dict[str, str], Dict[str, str], Dict[str, str]: A tuple of dictionaries 
        where the first element is the headers, the second element is the data, 
        and the third element is the cookies.
    """
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9,en-GB;q=0.8,ar;q=0.7',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
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

    data = {
        'username-17384': 'XXXXXXXXXXXXXXXX',
        'user_password-17384': 'XXXXXXXXXXXXXXXX',
        'form_id': '17384',
        'um_request': '',
        '_wpnonce': 'XXXXXXXXXXXXXXXX',
        '_wp_http_referer': '/login/',
        'rememberme': '1',
    }

    cookies = {
        'wordpress_test_cookie': 'WP+Cookie+check',
    }

    return headers, data, cookies



def _get_post_request_variables(payload: Dict[str, str], sess: Session) -> str:
    """
    Retrieves the value of the '_wpnonce' parameter from the login page response.

    TODO: explain that you found this out by checking that website didn't respond correcrtly anymore 
    in the following day of writing the code, so you had to compare 
    the payload (data) with the new one fetched from the networks tab 
    to see if there are any differences

    Args:
        payload (Dict[str, str]): The payload dictionary.
        sess (Session): The session object used for making HTTP requests.

    Returns:
        str: The value of the '_wpnonce' parameter.

    Raises:
        Exception: If the '_wpnonce' value cannot be found in the response.
    """
    response = sess.get('https://forqanacademy.com/login/')
    save_data(response.text, "login_page_html")
        
    match = re.search(r'id="_wpnonce".*?value="([^"]*)"', response.text)
    if not match:
        raise Exception('Could not find wpnonce')
    wpnonce = match.group(1)
    logger.debug(f"wpnonce: {wpnonce}")

    return wpnonce


@log_decorator()
def login(username: str = None, 
            password: str = None) -> Tuple[Session, Response]:
    """
    Logs into the Forqan Academy website and returns a session and the response.

    This function logs into the Forqan Academy website using the provided username 
    and password, and returns a session where the user is logged in and the response 
    from the POST request to the login URL.

    Args:
        username (str): The username to log in with.
        password (str): The password to log in with.

    Returns:
        Tuple[Session, Response]: A tuple where the first element is a 
        requests.Session object where the user is logged in, and the second 
        element is the Response object from the POST request to the login URL.
    """

    headers, data, cookies = _get_post_request_constants()

    sess = requests.Session()
        
    wpnonce = _get_post_request_variables(data, sess)

    if username is None:
        username = os.getenv('MY_USERNAME')
    if password is None:
        password = os.getenv('MY_PASSWORD')

    data.update({
        '_wpnonce': wpnonce, 
        'username-17384': username, 
        'user_password-17384': password
        })

    response = sess.post('https://forqanacademy.com/login/', headers=headers, data=data, cookies=cookies)

    return sess, response