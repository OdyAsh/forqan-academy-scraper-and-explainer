import json
import os
import pickle
from typing import Any, Union, Dict
import requests

from pyprojroot import here

from logaru_logger.the_logger import logger

# TODO (importance level: low): logic that will set "SAVED_FILES_DICT" to key:value pairs 
#   based on the file name and the file path without extension
#   then, a boolean flag in save_data() to ask if the developer wants to
#   overwrite a saved file within the same session or increase its prefix counter its time its run within the same ipython session

def _prefix_str_with_global_counter(string: str) -> str:
    """
    Prefix a string with a counter.

    Args:
        string (str): The string to be prefixed.

    Returns:
        str: The string prefixed with a counter.
    """    
    if os.getenv('INTERMEDIATE_OUTPUTS_COUNTER') is None:
        os.environ['INTERMEDIATE_OUTPUTS_COUNTER'] = "1"

    new_string = f"{os.getenv('INTERMEDIATE_OUTPUTS_COUNTER')}_{string}"

    os.environ['INTERMEDIATE_OUTPUTS_COUNTER'] = str(int(os.getenv('INTERMEDIATE_OUTPUTS_COUNTER')) + 1)

    return new_string

def _create_directory(dir_name: str) -> None:
    """
    Create a directory if it does not exist.

    Args:
        dir_name (str): The directory name.

    Returns:
        None
    """
    os.makedirs(dir_name, exist_ok=True)

def _get_directory(dir_name: Union[str, None], intermediate_output: bool) -> str:
    """
    Get the directory path based on the given parameters and create the directory if it does not exist.

    Args:
        dir_name (str): The directory name where the file will be saved.
        intermediate_output (bool): Flag indicating if it is an intermediate output.

    Returns:
        str: The directory path.
    """
    if dir_name is None:
        dir_name = ""
    if intermediate_output:
        dir_name = os.path.join(here(), os.getenv("INTERMEDIATE_OUTPUTS_DIR"), dir_name)
    else:
        dir_name = os.path.join(here(), os.getenv("FINAL_OUTPUTS_DIR"), dir_name)
    dir_name = os.path.normpath(dir_name)
    _create_directory(dir_name)

    return dir_name

def _get_file_path_without_extension(dir_name: str, file_name: str, add_intermediate_counter_prefix: bool) -> str:
    """
    Get the file path based on the given parameters.

    Args:
        dir_name (str): The directory name where the file will be saved.
        file_name (str): The name of the file (without extension).
        add_intermediate_counter_prefix (bool): Flag indicating if a counter prefix should be added to the file name.

    Returns:
        str: The file path.
    """
    if add_intermediate_counter_prefix:
        file_name = _prefix_str_with_global_counter(file_name)
    file_path_without_extension = os.path.join(dir_name, file_name)
    return file_path_without_extension

def _save_data_to_json(file_path_without_extension: str, data_to_be_saved: Any) -> None:
    """
    Save data to a JSON file.

    Args:
        file_path_without_extension (str): The path of the file.
        data_to_be_saved (Any): The data to be saved.

    Returns:
        None
    """
    with open(f'{file_path_without_extension}.json', "w") as file:
        json.dump(data_to_be_saved, file, ensure_ascii=False, indent=2)

def _save_data_to_txt(file_path_without_extension: str, data_to_be_saved: Any) -> None:
    """
    Save data to a text file.

    Args:
        file_path_without_extension (str): The path of the file.
        data_to_be_saved (Any): The data to be saved.

    Returns:
        None
    """
    with open(f'{file_path_without_extension}.txt', "w") as file:
        file.write(str(data_to_be_saved))

# TODO: prettify the HTML when saving to html file
def _save_data_to_html(file_path_without_extension: str, data_to_be_saved: Any) -> None:
    """
    Save data to an HTML file.

    Args:
        file_path_without_extension (str): The path of the file.
        data_to_be_saved (Any): The data to be saved.

    Returns:
        None
    """
    with open(f'{file_path_without_extension}.html', "w") as file:
        file.write(data_to_be_saved)

def _save_data_to_pkl(file_path_without_extension: str, data_to_be_saved: Any) -> None:
    """
    Save data to a pickle file.

    Args:
        file_path_without_extension (str): The path of the file.
        data_to_be_saved (Any): The data to be saved.

    Returns:
        None
    """
    with open(f'{file_path_without_extension}.pkl', "wb") as file:
        pickle.dump(data_to_be_saved, file)

def _save_data_to_pdf(file_path_without_extension: str, data_to_be_saved: Any) -> None:
    """
    Save data to a PDF file.

    Args:
        file_path_without_extension (str): The path of the file.
        data_to_be_saved (Any): The data to be saved.

    Returns:
        None
    """
    with open(f'{file_path_without_extension}.pdf', "wb") as file:
        file.write(data_to_be_saved)

def _save_data_based_on_extension(file_extension: Union[str, None], file_path_without_extension: str, data_to_be_saved: Any) -> None:
    """
    Choose the appropriate save function based on the file extension.

    Args:
        file_extension (str, optional): The file extension. Defaults to None.
        file_path_without_extension (str): The path of the file.
        data_to_be_saved (Any): The data to be saved.

    Returns:
        None
    """
    if file_extension == "txt":
        _save_data_to_txt(file_path_without_extension, data_to_be_saved)
    elif file_extension is "html":
        _save_data_to_html(file_path_without_extension, data_to_be_saved)
    elif file_extension == "pkl":
        _save_data_to_pkl(file_path_without_extension, data_to_be_saved)
    elif file_extension == "json":
        _save_data_to_json(file_path_without_extension, data_to_be_saved)
    elif file_extension == "pdf":
        _save_data_to_pdf(file_path_without_extension, data_to_be_saved)
    else:
        raise ValueError("Invalid file_extension. Supported file_extensions are 'txt', 'pkl', and 'json'.")

def save_data(data_to_be_saved: Any, 
            file_name: str, 
            dir_name: Union[str, None] = None, 
            file_extension: Union[str, None] = "txt",
            intermediate_output: bool = True,
            add_intermediate_counter_prefix: bool = True) -> None:
    """
    Save data to a file.

    Args:
        data_to_be_saved (Any): The data to be saved.
        file_name (str): The name of the file (without extension).
        dir_name (str, optional): The directory name where the file will be saved. Defaults to None.
        file_extension (str, optional): The file extension.
        intermediate_output (bool, optional): Flag indicating if it is an intermediate output. Defaults to True.
        add_intermediate_counter_prefix (bool, optional): Flag indicating if a counter prefix should be added to the file name. Defaults to False.

    Returns:
        None
    """
    dir_name = _get_directory(dir_name, intermediate_output)
    file_path_without_extension = _get_file_path_without_extension(dir_name, file_name, add_intermediate_counter_prefix)
    _save_data_based_on_extension(file_extension, file_path_without_extension, data_to_be_saved)

    log_level = "DEBUG" if os.getenv("DEBUG") == "1" else "INFO"
    logger.log(log_level, f"Data saved to {file_path_without_extension}.{file_extension}")