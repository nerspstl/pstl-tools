import json
from typing import Any, Callable, Iterable


def load_json(file,*args, **kwargs):
    """
    wrapper to with open() as f: format for JSON files such that it is one call.
    Returns a dictionary of JSON data. 
    """
    with open(file) as f:
        json_data = json.load(f)
    return json_data


def load_build_and_get_parameters(
        settings:dict[Any, Any], 
        builders: dict[str,Callable],
        *args, **kwargs) -> Any:
    """
    The 'settings' argument contains the dictionary of the imported JSON
    now check for sub-dictionaries that are length=1 and posses either 
    key words "BUILD", "BUILD_FROM_FILE", or "FROM_FILE".

    If "BUILD" or "BUILD_FROM_FILE":
        then takes either the following dictionary or read-in dictionary 
        from JSON file, respectivly, and creates the object using the 
        matching builder. The builders are limited to known objects that
        are required for the setup file that this function is being called
        to make. Thus, 'builders' arguments are passed into this function 
        from the previous setup function. 
    IF "FROM_FILE":
        then the dictionary from the file is placed under the keyword 
        requesting the file be brought in
    
    Returns:
        output  : dict[Any] -> A dictionary of parameters (arguments) 
        using the keywords defined from the input argument 'settings' of 
        this function as the keywords of the returned dictionary with the
        values now of this new dictionary being either a sub-dictionary(ies)
       (if "FROM_FILE") or an object (if "BUILD" or "BUILD_FROM_FILE")
        
    Note:  
        The retured object of this function is no longer a dictionary of 
        settings, but a dictionary of parameters (arguments) for the 
        setup function to pass in as keyword arguments to initiate the
        object.

    """
    # first step is loop through dictionary layer by layer looking for a
    # pair of a key with a value element that is a dictionary of length=1
    # Once found, send that value element that is a dictionay to <func>
    # That function will either build and return an object --or-- iterate
    # through sub-layers till all "FROM_FILE"s have been resolved and a
    # complete dictionary can be returned.
            
    # key words to look for
    BUILD = "BUILD"
    BUILD_FROM_FILE = "BUILD_FROM_FILE"
    FROM_FILE = "FROM_FILE"
    # create raise key error function
    def key_error(key):
        raise KeyError("'%s' is not a valid key in builders"%(key))
    
    # loop through settings
    parameters: dict[str, Any] = dict(settings)
    for key in settings:
        # Check if dictionary and length of dictionary is 1
        subsettings = settings[key]
        isdict = isinstance(subsettings, dict)
        # Check if length if dictionary is 1 if subsettings is dictionary
        isdictlen1 = (True if len(subsettings) == 1 else False) if isdict is True else False
        # Check if passed and move on if true
        if isdictlen1 is True:
            # get subkey to check
            subkey = [*settings[key]][0]
            # If "BUILD", then check if key in builders, then build 
            if subkey == BUILD:
                subsettings = subsettings[BUILD]
                parameters[key] = builders[key](subsettings) if key in builders else key_error(key) 
            # if "BUILD_FROM_FILE", then check if key in builders, read in JSON, then build 
            elif subkey == BUILD_FROM_FILE:
                # here subsettings is a dictionary of length=1 with only a key being "BUILD_FROM_FILE" and
                # the value element being a file path. This file path is to a JSON file that is loaded
                # and saved as subsettings. Subsettings is a dictionary of settings that is then passed
                # to the builder setup file which returns parameters saved under the original key. This
                # value element is now an object created by the builder instead of a dictionary
                subsettings = load_json(subsettings[BUILD_FROM_FILE])
                parameters[key] = builders[key](subsettings) if key in builders else key_error(key) 
            # if "FROM_FILE", read in JSON and save the new dictionary under the key
            elif subkey == FROM_FILE:
                # here subsettings is a dictionary of length=1 with only a key being "FROM_FILE" and
                # the value element being a file path. This file path is to a JSON file that is loaded
                # and saved as subsettings. Subsettings is a dictionary of settings that This
                # value element is now a new dictionary of subsettings loaded in from the JSON file.
                # The original lenght of 1 dictionary is now a new dictionary of new subsettings
                subsettings = load_json(subsettings[FROM_FILE])
                subsettings = load_build_and_get_parameters(settings=subsettings,builders=builders,*args, **kwargs)
                parameters[key] = subsettings
            # if it doesnt match any expression, just keep parameters[key] = settings[key] and move on
            else:
                pass
        elif isdict is True:
            subsettings = load_build_and_get_parameters(settings=subsettings,builders=builders,*args, **kwargs)
            parameters[key] = subsettings
                


    return parameters