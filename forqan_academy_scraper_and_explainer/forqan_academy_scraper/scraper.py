import os
import functools
from typing import Dict, List, Optional, Tuple, Union, Literal, Any
import html
from bs4 import BeautifulSoup
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

    login_response_html_string = response.text
    logger.debug(f"login_response_html_string: {login_response_html_string[-100:]}")
    save_data(login_response_html_string, "login_response_html_string")


    return sess, login_response_html_string


@log_decorator()
def get_forqan_modules_urls_using_regex(html_string : str) -> List[str]:
    """
    Extracts the URLs of Forqan Academy modules from the given HTML string.
    
    Args:
        html_string (str): The HTML string to search for module URLs.
        
    Returns:
        list: A list of URLs of Forqan Academy modules.
    """
    
    # Regular expression pattern to match 'a' tags with class 'ld-item-name'
    pattern = r'<a href="(.*?)" class="ld-item-name">'
    
    # Find all matches in the HTML string
    forqan_modules_urls = re.findall(pattern, html_string)
    
    logger.debug(f"forqan_modules_urls: {forqan_modules_urls}")
    save_data(forqan_modules_urls, "forqan_modules_urls", file_extension="json")

    return forqan_modules_urls

@log_decorator()
def get_modules_info_using_regex(forqan_modules_urls: List[str], session: Session) -> List[Tuple[str, str]]:
    """
    Fetches and returns information about each module.

    Parameters:
    forqan_modules_urls (List[str]): A list of URLs for the Forqan modules.
    session: A requests.Session object for making the requests.

    Returns:
    List[Tuple[str, str]]: A list of tuples, where each tuple contains the module name and the HTML of the module page.
    """
    modules_name_and_html = []
    for url in forqan_modules_urls:

        # fetching the module page from the URL
        response = session.get(url)

        # getting the module name
        module_name = re.search(r'<title>(.*?)&#8211;', response.text)
        if module_name:
            module_name = module_name.group(1)
            module_name = re.sub(r'\(\d+\)', '', module_name).strip()
        else:
            module_name = "No module name found"
        logger.info(f"Module name: {module_name}")
        modules_name_and_html.append((module_name, response.text))

    # saving intermediate outputs for debugging purposes
    save_data(modules_name_and_html[0][1], "module_pages_first_url_response")
    save_data(modules_name_and_html[-1][1], "module_pages_last_url_response")


    return modules_name_and_html    

@log_decorator()
def get_lessons_name_and_urls_using_regex(modules_name_and_html: List[Tuple[str, str]]) -> List[List[Tuple[str, str]]]:
    """
    Get the lessons info from each module page.

    An "info" is a tuple containing the href URL and the lesson's name.
    Therefore, the final returned value is a list of list of tuples,
    where the outer lists represents the modules themselves,
    and each inner list contains the lessons info (i.e., a tuple) for the i-th module.

    Args:
        modules_name_and_html (List[Tuple[str, str]]): A list of tuples, where each tuple contains the module name and the HTML of the module page.

    Returns:
        List[List[Tuple[str, str]]]: A list of list of tuples, where each tuple contains the lesson's name and URL.
    """
    lessons_names_and_urls_per_module = []
    for cur_module in modules_name_and_html:
        
        # getting current module's info
        cur_module_name, cur_module_html_page = cur_module
        
        # getting each lesson's name and URL for the current module
        # TODO (learning, importance level: low): see how to not hardcode the `https://forqanacademy.com` part, 
        # while at the same time, not use `.*?/topic` since it continues to match in the html until it finds a url with `/topic` in it
        a_tag_pattern = r'<a class="ld-table-list-item-preview.*?" href="(https://forqanacademy.com/topic/.*?)">.*?<span class="ld-topic-title">(.*?)</span>'
        # IMPLEMENTATION NOTE: re.DOTALL is used to match newlines as well when using the dot (.) metacharacter
        cur_module_lessons_names_and_urls = re.findall(a_tag_pattern, cur_module_html_page, re.DOTALL) 
        if cur_module_lessons_names_and_urls:
            # Switch the order of the groups in each match
            cur_module_lessons_names_and_urls = [(match[1], match[0]) for match in cur_module_lessons_names_and_urls]

        logger.info(f"Lessons matched for module {cur_module_name}:\n{cur_module_lessons_names_and_urls}\n")
        lessons_names_and_urls_per_module.append(cur_module_lessons_names_and_urls)
        save_data(cur_module_lessons_names_and_urls, f"lessons_names_and_urls for {cur_module_name}", file_extension="json")

    # saving intermediate outputs for debugging purposes
    save_data(lessons_names_and_urls_per_module, "lessons_names_and_urls_per_module", file_extension="json")

    return lessons_names_and_urls_per_module


def _unused_manually_visualize_lesson_desc(session: Session) -> List[str]:
    """
    Check this documentation file for details on what this unused function does:
    `doc/extracting_video_desc_logic/possible_htmls.md`
    """
    tmp_links = [
        # no desc. header
        r'https://forqanacademy.com/topic/%d8%a7%d9%84%d9%85%d8%ad%d8%a7%d8%b6%d8%b1%d8%a9-1-%d8%a7%d9%84%d9%85%d8%b1%d8%ad%d9%84%d8%a9-%d8%a7%d9%84%d9%85%d9%83%d9%8a%d8%a9/',
        
        # h4 li desc.
        r'https://forqanacademy.com/topic/%d8%a7%d9%84%d9%85%d8%ad%d8%a7%d8%b6%d8%b1%d8%a9-6-%d8%ba%d8%b2%d9%88%d8%a9-%d8%a7%d9%84%d8%a3%d8%ad%d8%b2%d8%a7%d8%a8/',
        r'https://forqanacademy.com/topic/%d8%a7%d9%84%d9%85%d8%ad%d8%a7%d8%b6%d8%b1%d8%a9-2-%d8%a7%d9%84%d8%af%d8%b1%d9%88%d8%b3-%d8%a7%d9%84%d9%85%d8%b3%d8%aa%d9%81%d8%a7%d8%af%d8%a9-%d9%85%d9%86-%d8%a7%d9%84%d9%85%d8%b1%d8%ad%d9%84%d8%a9/',
        
        # p desc.
        r'https://forqanacademy.com/topic/%d8%a7%d9%84%d9%85%d8%ad%d8%a7%d8%b6%d8%b1%d8%a9-8-%d8%ba%d8%b2%d9%88%d8%a9-%d8%a8%d9%86%d9%8a-%d9%82%d8%b1%d9%8a%d8%b8%d8%a9/'
    ]
    # checking out HTML of lessons with varying description formatting
    desc_contents = []
    for i, link in enumerate(tmp_links):
        resp = session.get(link)
        lesson_html = resp.text

        soup = BeautifulSoup(lesson_html, 'html.parser')
        div_tag = soup.find('div', class_='ld-tab-content ld-visible lesson-materials-btns')
        text_content = div_tag.get_text(separator='\n\n', strip=True)

        # Print the text content
        logger.debug(text_content)

        save_data(text_content, 
                    f"{i:02}_lesson_desc_content", 
                    dir_name="../logs/temp_outputs_for_visualizing", 
                    add_intermediate_counter_prefix=False,
                    file_extension="txt")
        
        desc_contents.append(text_content)

    return desc_contents



def get_video_urls_descriptions_and_pdf_metadata(modules_name_and_html: List[Tuple[str, str]], 
                                            forqan_modules_urls: List[str], 
                                            lessons_names_and_urls_per_module: List[List[Tuple[str, str]]],
                                            session: Session
                                            ) -> Dict[str, Dict]:
    """
    Extracts and compiles video URLs, descriptions, and occasionally PDF names/URLs for each lesson in each module. PDFs summarize a couple of lessons.

    - Iterates through each module, using its name and URL to gather lesson information.
    - For each lesson, it checks if the lesson is available, a revision lesson, or a normal lesson and gathers appropriate data:
        - If not available, marks the lesson as such.
        - If a revision lesson, extracts the PDF name and URL which may summarize a couple of lessons.
        - For normal lessons, extracts the video URL and description.
    - Stores all extracted information in a structured dictionary, including video URLs, descriptions, and PDF information when applicable.

    Args:
        modules_name_and_html (List[Tuple[str, str]]): A list of tuples containing module names and their HTML content.
        forqan_modules_urls (List[str]): A list of URLs for each module.
        lessons_names_and_urls_per_module (List[List[Tuple[str, str]]]): A nested list where each sublist contains tuples of lesson names and URLs for a module.

    Returns:
        Dict[str, Dict]: A dictionary with module information, including lesson details such as names, URLs, availability, content descriptions, and occasionally PDF names/URLs.
    """
    forqan_lessons_info = {}
    # iterating by each module name/url
    for i, ((module_name, _), module_url) in enumerate(zip(modules_name_and_html, forqan_modules_urls)):
        module_num = f"{i+1:02d}"
        logger.debug(f"module num and name: {module_num}: {module_name}")
        cur_module_lessons = lessons_names_and_urls_per_module[i]
        forqan_lessons_info[f"module_{module_num}"] = {"name": module_name, "url": module_url, "lessons": []}
        
        # iterating by each lesson name/url
        for lesson_name, lesson_url in cur_module_lessons:
            logger.debug(f"lesson_name: {lesson_name}")
            logger.debug(f"lesson_url: {lesson_url}")
            lesson_response = session.get(lesson_url)
            lesson_html_string = lesson_response.text
            soup = BeautifulSoup(lesson_html_string, 'html.parser')
            lesson_content = {}

            # check if the lesson is not available yet
            if re.search(r'يرجى العودة وإكمال', lesson_html_string) or re.search(r'متوفر في', lesson_html_string):
                # store lesson's info as non-available
                lesson_content['not_available'] = True
                logger.debug(f"lesson_name: {lesson_name} is not available yet")

            # check if the lesson is a revision lesson
            elif "المحاضرات" in lesson_name:
                logger.debug(f"revision lesson_title: {lesson_name}")

                # ensure pdf_name is compatible with the file-naming system
                lesson_name = html.unescape(lesson_name).replace('–', '-')
                pdf_name = lesson_name
                invalid_chars = r'[\\/:*?"<>|]'
                pdf_name = re.sub(invalid_chars, '', pdf_name)
                lesson_content['pdf_name'] = pdf_name
                logger.debug(f"its pdf_name: {pdf_name}")

                # get pdf URL to download later
                pdf_url = soup.find('a', class_='ui button fluid primary btn text-link')['href']
                lesson_content['pdf_url'] = pdf_url
                logger.debug(f"pdf_url: {pdf_url}")

            # else, this is a normal and available lesson
            else:
                # get video URL to use later for getting .srt files using speech-to-text AI model
                try:
                    video_url = soup.find('iframe')['src']
                except:
                    logger.error('unable to find video URL, will print the soup HTML content for debugging purposes')
                    logger.debug(f"soup HTML content: {soup.prettify()}")

                lesson_content['video_url'] = video_url
                logger.debug(f"video_url: {video_url}")

                # get the description of the video
                div_tag = soup.find('div', class_='ld-tab-content ld-visible lesson-materials-btns')
                text_content = div_tag.get_text(separator='\n\n', strip=True)
                desc_termination_keyword = "لمشاهدة"
                video_description = text_content.split(desc_termination_keyword)[0].strip()
                lesson_content['video_description'] = video_description
                logger.debug(f"video_description: {video_description}")
            
            # store current lesson's info to dictionary
            forqan_lessons_info[f"module_{module_num}"]["lessons"].append({
                "name": lesson_name,
                "url": lesson_url,
                **lesson_content
            })

    # saving intermed`iate outputs for debugging purposes
    save_data(forqan_lessons_info, "forqan_lessons_info", file_extension="json")

    return forqan_lessons_info


def download_revision_pdfs(forqan_lessons_info: Dict) -> None:
    """
    Downloads PDFs from URLs found in the nested dictionary 'forqan_lessons_info' and saves them with names specified in the dictionary.

    The PDFs are saved in a subdirectory 'revisions_pdfs' within the directory specified by the 'FINAL_OUTPUTS_DIR' environment variable. 
    This subdirectory is created if it does not already exist.

    Args:
        forqan_lessons_info (Dict): A nested dictionary containing 'pdf_url' and 'pdf_name' keys among others.

    Returns:
        None
    """

    for module_info in forqan_lessons_info.values():
        module_name = module_info.get("name", "unknown_module")
        dir_name = os.path.join("revisions_pdfs", module_name)

        for lesson in module_info.get("lessons", []):
            if "pdf_url" in lesson and "pdf_name" in lesson:
                pdf_url = lesson["pdf_url"]
                pdf_name = lesson["pdf_name"]
                response = requests.get(pdf_url)
                if response.status_code != 200:
                    logger.error(f"Failed to download this pdf: {pdf_url}")
                    continue
                pdf_content = response.content
                save_data(data_to_be_saved=pdf_content, 
                        file_name=pdf_name, 
                        dir_name=dir_name, 
                        file_extension="pdf", 
                        intermediate_output=False, 
                        add_intermediate_counter_prefix=False)
                logger.info(f"Downloaded and saved: {pdf_name}.pdf")