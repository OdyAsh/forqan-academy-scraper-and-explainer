import sys
import os
from dotenv import load_dotenv
load_dotenv(override=True)
from datetime import datetime
import functools
from typing import Union, Any
import pandas as pd

import pyprojroot
from loguru import logger
from varname import argname

# the code below should ensure that each file which calls `logger` from this file (not `loguru`) 
# will have have the same handler configuration

# Remove default handler
logger.remove()
lvl = 'DEBUG' if os.environ['DEBUG']=='1' else 'INFO'

# Log to stdout
# DEBUGGING NOTE: enqueue=False means that the logging calls are processed in the same thread 
#   and so the application will wait for the logging to complete before continuing execution.
#   This is done to avoid an ipykernel-related issue where the logging messages are all displayed in the first cell which logs a message.
logger.add(sys.stdout, level=lvl, enqueue=False)  

# all scripts' (i.e., sub-processes') logs will be stored 
# in the same file of the i^th 10 minute range in today's date and hour
# so the files will have a structure like this in case it was created in the 9:30am/9:40am range:
# "PROJECT_ROOT_DIR/logs/run_log_2024-05-09_09h-30m.log"
mm_interval = str((datetime.now().minute // 10) * 10)
log_file_name = 'run_log_{time:YYYY-MM-DD_HH}h-' + mm_interval + 'm.log'
log_file_path = os.path.join(str(pyprojroot.here()), 'logs', 'detailed_logs', log_file_name) 

# Rotate log file every 100 MB in case the log is too large even in the span of these 10 minutes
logger.add(log_file_path, rotation="100 MB")  


def _get_level(level: Union[str, int]) -> Union[str, int]:
    """
    Returns the level of the logger.

    This function takes a string or integer representing a log level and returns the corresponding log level in uppercase. 
    If the input is a string, it checks the first character to determine the log level. If the input is an integer, it is 
    returned as is. If the input is not a valid log level, a ValueError is raised.

    Parameters
    ----------
    level : Union[str, int]
        The log level to convert.

    Returns
    -------
    Union[str, int]
        The converted log level.

    Raises
    ------
    ValueError
        If the input is not a valid log level.
    """
    if isinstance(level, str):
        level = level.lower()
        if level.startswith("d"):
            level = "DEBUG"
        elif level.startswith("i"):
            level = "INFO"
        elif level.startswith("w"):
            level = "WARNING"
        elif level.startswith("e"):
            level = "ERROR"
        elif level.startswith("c"):
            level = "CRITICAL"
        else:
            raise ValueError("Invalid log level")
        
    return level


def _get_var_names_passed_to_args_or_kwargs(data:Union[tuple, dict]) -> str:
    """
    Returns the variable names passed to the function arguments or keyword arguments.

    This function takes a variable which either represents the function arguments or the keyword arguments,
    then returns a string containing the variable names passed to these arguments. 
    This input "variable" can be:
    * a tuple -> returns a list of string representations of the arguments. 
    * a dictionary -> returns a list of string representations of the keyword arguments. 

    Parameters
    ----------
    data : Union[tuple, dict]
        The function arguments or keyword arguments to get the variable names from.

    Returns
    -------
    str
        The variable names passed to the function arguments or keyword arguments.
    """
    if isinstance(data, tuple):
        data_list = [f'args[{i}]' for i in range(len(data))]
    else:
        data_list = [f'kwargs[{key}]' for key in data.keys()]

    if len(data_list) == 0:
        return ''

    func_depth = 2
    try:
        if len(data_list) == 1:
            data_names = argname(data_list[0], vars_only=False, frame=func_depth)
        else:
            data_names = ', '.join(argname(*data_list, vars_only=False, frame=func_depth))

        if not data_names:
            raise
        return f'{data_names}'
    except:
        func_depth += 1
        if func_depth == 5:
            return ''


def _convert_pd_to_str(obj:Union[dict, list, tuple, Any]) -> Union[dict, list, tuple, Any]:
    """
    Recursively converts all pandas objects in the input to string representations.

    This function takes an object and recursively converts all pandas DataFrames and Series in the object to string 
    representations. If the object is a dictionary, list, or tuple, it recursively applies this function to each element. 
    If the object is a pandas DataFrame, it returns a string representation of the DataFrame's columns. If the object is a 
    pandas Series, it returns a string representation of the Series' name. Otherwise, it returns the object as is.

    Parameters
    ----------
    obj : Union[dict, list, tuple, Any]
        The object to convert.

    Returns
    -------
    Union[dict, list, tuple, Any]
        The converted object.

    Notes
    -----
    Assumption: If the string has this format yyyy-mm-dd, 
        we assume that IF there were ever any shared 
        gregorian date strings in the object, they would be after the year 1599.

    """
    if isinstance(obj, dict):
        return {k: _convert_pd_to_str(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_convert_pd_to_str(elem) for elem in obj]
    if isinstance(obj, tuple):
        return tuple([_convert_pd_to_str(elem) for elem in obj])
    if isinstance(obj, pd.DataFrame):
        return f"pd.DataFrame with cols: {', '.join(obj.columns)}"
    if isinstance(obj, pd.Series):
        # year, month, day = map(int, obj.split('-'))
        return f"pd.Series with name: {obj.name}"
        
    return obj

def _get_first_and_last_pairs(my_dict:dict) -> tuple:
    first_key = next(iter(my_dict))
    last_key = next(reversed(my_dict))
    return {first_key: my_dict[first_key], last_key: my_dict[last_key]}

def _convert_pandas_objects(args:Union[tuple, dict, Any]=None, 
                            kwargs:Union[tuple, dict, Any]=None, 
                            obj:Union[dict, list, tuple, Any]=None, 
                            get_empty_res_as_str:bool=False
                            ) -> Union[tuple, str]:
    """
    Converts pandas objects to string representations.

    This function takes function arguments, keyword arguments, or an object and converts all pandas DataFrames and Series 
    in these inputs to string representations. If 'args' or 'kwargs' is provided, it converts the pandas objects in these 
    inputs and returns the converted arguments and keyword arguments. If 'obj' is provided, it converts the pandas objects 
    in 'obj' and returns the converted object. If 'get_empty_res_as_str' is True, it returns the converted object as a string. Otherwise, 
    it returns the converted object as is.

    Parameters
    ----------
    args : tuple, optional
        The function arguments to convert.
    kwargs : dict, optional
        The function keyword arguments to convert.
    obj : Any, optional
        The object to convert.
    get_empty_res_as_str : bool, optional
        If True, return the converted object as a string. Otherwise, return the converted object as is.

    Returns
    -------
    Union[str, tuple, dict, Any]
        The converted inputs.
    """    
    if obj is not None:
        obj_conv = _convert_pd_to_str(obj)
        try:
            if isinstance(obj_conv, dict) and len(obj_conv) > 30:
                return 'Too many keys to log.. first and last key, value pairs are: ' + str(_get_first_and_last_pairs(obj_conv))
        except:
            pass
        return obj_conv
           
    if not (args or kwargs):
        return ('', '') if not get_empty_res_as_str else ''

    arg_values = _convert_pd_to_str(args)

    kwarg_values = _convert_pd_to_str(kwargs)

    return arg_values, kwarg_values


# source: https://loguru.readthedocs.io/en/stable/resources/recipes.html#logging-entry-and-exit-of-functions-with-a-decorator
def log_decorator(*, entry:bool=True, exit:bool=False, level:str="INFO"):
    """
    Decorator for logging function entry and exit.

    This decorator logs the entry and exit of a function. It takes a boolean indicating whether to log the entry and exit of 
    the function, and a string representing the log level. It logs the function name, arguments, keyword arguments, and 
    return value at the specified log level. If 'entry' is True, it logs the function entry. If 'exit' is True, it logs the 
    function exit.

    Parameters
    ----------
    entry : bool, optional
        If True, log the function entry. Default is True.
    exit : bool, optional
        If True, log the function exit. Default is False.
    level : str, optional
        The log level. Default is "INFO".

    Returns
    -------
    function
        The decorated function.

    Notes
    -----
    The function uses the `loguru.logger` object to log the messages.

    If entry/exit booleans are False, then the function's entry/exit details 
    will still be logged, but at the DEBUG level.
    
    Source: https://loguru.readthedocs.io/en/stable/resources/recipes.html#logging-entry-and-exit-of-functions-with-a-decorator
    Other sources for understanding decorators:
    - https://www.youtube.com/watch?v=swU3c34d2NQ
    - https://www.youtube.com/watch?v=FsAPt_9Bf3U
    - https://www.youtube.com/watch?v=KlBPCzcQNU8
    """
    level = _get_level(level)

    def wrapper(func):
        func_name = func.__name__

        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            # Create a logger with specific options
            logger_ = logger.opt(depth=1, colors=True)

            # Set entry and exit log levels
            entry_level = level if entry else 'DEBUG'
            exit_level = level if exit else 'DEBUG'

            # Get the names of the variables passed to args and kwargs
            arg_names, kwarg_names = map(_get_var_names_passed_to_args_or_kwargs, [args, kwargs])

            # Convert pandas objects in args and kwargs to a more log-friendly format
            arg_values, kwarg_values = _convert_pandas_objects(args, kwargs)

            # Filter out any functions that passes sensitive info 
            # so that it doesn't log the values in the passed arguments
            # TODO (in the future): Add more functions to this list whenever needed
            sensitive_functions = ['login']

            # Construct the strings for the log message
            strs = ['\nArg-Var-Names = ({})', '\nKwarg-Var-Names = ({})', 
                    '\nArg-Var-Values = ({})' if func_name not in sensitive_functions else '', 
                    '\nKwarg-Var-Values = ({})' if func_name not in sensitive_functions else '']

            # Get the values to be logged
            all_vals = [arg_names, kwarg_names, arg_values, kwarg_values]
            # Implementation note: Get each value only if the corresponding string is not empty
            vals = [val for val, strr in zip(all_vals, strs) if strr]

            # Construct the final string for the log message
            str_final = '<magenta>Entering \"{}\"' + ''.join(strs) + '</>'

            # Log the function entry details (args, kwargs, etc.)
            # Implementation note: we don't use f strings here as they don't get color-formatted by loguru
            logger_.log(entry_level, str_final, func_name, *vals)

            # Run the function
            result = func(*args, **kwargs)

            # Convert the result to a more log-friendly format
            log_result = _convert_pandas_objects(obj=result, get_empty_res_as_str=True)

            # Construct the string for the log message
            str_res = '\nResults = {}' if log_result else ''
            str_final = '<magenta>Exiting "{}"' + str_res + '</>'

            # Log the function exit details (return value(s))
            logger_.log(exit_level, str_final, func_name, *[log_result] if str_res else [])

            # Return the result of the function
            return result
        
        return wrapped

    return wrapper