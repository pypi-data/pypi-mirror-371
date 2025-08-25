# Create a JSON to JSONL converter and vice versa
# This will read a JSONL file and convert it to a JSON file
# The JSONL file will have one JSON object per line
# The user will specify the input and output file names
# The user will also specify how the JSONL lines will be stored in the data array of the JSON file

"""
Author: dja322

This script provides functions to convert JSONL files to JSON format and vice versa.
It includes options for sorting, filtering, and validating JSONL data.
It also includes utility functions for jsonl files.
"""


import json

def convert_jsonl_to_json(input_file: str, output_file: str, 
                            json_indent: int = 4,
                            jsonl_start_index: int = 0,
                            jsonl_end_index: int=-1,
                            print_error_logs: bool = False,
                            verbose: bool = False,
                            return_json_dict: bool = True,
                            sort_data : bool = False,
                            sort_data_key = None,
                            sort_descending : bool = True):
    r"""
    Take in a JSONL file and convert it to a JSON file and output it to the specified output file
    return the json dictionary object
    Parameters:
    input_file: str - the path to the input JSONL file
    output_file: str - the path to the output JSON file
    json_indent: int - the number of spaces to use for indentation in the output JSON file
    jsonl_start_index: int - the starting index of the JSONL lines to include in the output JSON file
    jsonl_end_index: int - the ending index of the JSONL lines to include in the output JSON file
    print_error_logs: bool - whether to print error logs for invalid JSON lines in the input file
    print_conversion_summary: bool - whether to print a summary of the conversion process
    return_json_dict: bool - whether to return the JSON dictionary object
    sort_data: bool - whether to sort the data array in the output JSON file
    sort_data_key: str - the key to sort the data array by if sort_data is True
    sort_descending: bool - whether to sort the data array in descending order if sort_data is

    Expected output format returned and/or written to file:
    {
        "config": {
            "name": "Converted Dataset",
            "Original_Data_set_filename": "input.jsonl",
            "number_of_objects": "100",
            "number_of_objects_in_original_file": "150"
        },
        "data": [
            {...}, 
            {...}
        ]
    }
    """
    
    json_list = []
    input_file_position = 0

    #check if file exists
    try:
        file = open(input_file, "r", encoding="utf-8")
    except FileNotFoundError:
        print(f"File {input_file} not found")
        return -1

    #open the input file and read line by line
    with open(input_file, 'r', encoding='utf-8') as infile:
        for line in infile:
            input_file_position += 1
            try:
                json_obj = json.loads(line)
                json_list.append(json_obj)
                if verbose:
                    print(f"Read valid JSON line at line number {input_file_position}")
            except json.JSONDecodeError:
                if print_error_logs:
                    print(f"Skipping invalid JSON line: {line.strip()} at line number {input_file_position}")
                    print(f"Error details: {json.JSONDecodeError}")


    #get number of lines that were valid json objects
    length_of_file_list = len(json_list)

    #bound checking for start and end index
    if jsonl_end_index < 0 or jsonl_end_index > length_of_file_list:
        jsonl_end_index = length_of_file_list
    
    if jsonl_start_index < 0 or jsonl_start_index >= length_of_file_list or jsonl_start_index >= jsonl_end_index:
        jsonl_start_index = 0

    #sort the data if specified
    if sort_data:
        if sort_data_key not in json_list[0]:#.keys():
            raise ValueError(f"sort_data_key {sort_data_key} not found in JSON objects")
        try:
            json_list = sorted(json_list, key=lambda x: x[sort_data_key], reverse=sort_descending)
        except TypeError as e:
            print(f"Error sorting JSON objects by key {sort_data_key}: {e}")

    #think if there is anything else useful to add to the config section
    json_dict = {
        "config":
        {
            "name": f"Converted {output_file} Dataset",
            "Original_Data_set_filename": output_file,
            "number_of_objects": str(jsonl_end_index - jsonl_start_index),
            "number_of_objects_in_original_file": str(length_of_file_list)
        },
        "data": json_list[jsonl_start_index:jsonl_end_index]
    }

    #print out summary of conversion
    if verbose:
        print(f"Converted {length_of_file_list} lines from {input_file} to {output_file}")
        print(f"Output JSON contains {jsonl_end_index - jsonl_start_index} objects from index {jsonl_start_index} to {jsonl_end_index - 1}")
        print(f"Converted {length_of_file_list} lines from {input_file} to {output_file}")

    #perhaps have an option for how results should be outputted(direct to file, return as object, etc)
    file = open(output_file, "w", encoding="utf-8")

    #dump the json dictionary to the output file
    json.dump(json_dict, file, indent=json_indent)

    if verbose:
        print(f"Wrote output JSON to {output_file} with indent level {json_indent}")

    file.close()

    if return_json_dict:
        return json_dict


def check_jsonl_is_consistent(input_file, 
                              print_error_messages: bool = False) -> bool:
    r"""
    Checks if all JSON objects in a JSONL file have the same keys, and that every line is valid JSON
    Parameters:
    input_file: str - the path to the input JSONL file
    print_error_messages: bool - whether to print error messages for inconsistent keys or invalid JSON lines
    """
    
    with open(input_file, 'r', encoding='utf-8') as infile:
        first_line = infile.readline()
        try:
            first_json_obj = json.loads(first_line)
        except json.JSONDecodeError:
            if print_error_messages:
                print(f"First line is not valid JSON: {first_line.strip()}")
            return False

        #get the keys of the first json object
        first_keys = set(first_json_obj.keys())
        line_number = 1

        #loop through the rest of the lines and check if the keys are the same
        for line in infile:
            line_number += 1
            try:
                json_obj = json.loads(line)
                if set(json_obj.keys()) != first_keys:
                    if print_error_messages:
                        print(f"Inconsistent keys found at line {line_number}: {json_obj.keys()}")
                    return False
            except json.JSONDecodeError:
                if print_error_messages:
                    print(f"Skipping invalid JSON line at line {line_number}: {line.strip()}")
                continue
    return True


def find_all_jsonl_keys(input_file, 
                        print_error_message: bool = False,
                        verbose: bool = False) -> set:
    r"""
    Goes through a JSONL file and finds all unique keys in the JSON objects
    Parameters:
    input_file: str - the path to the input JSONL file
    print_error_message: bool - whether to print error messages for invalid JSON lines

    returns: set - set of all unique keys found in the JSON objects
    """
    key_set = set()
    line_number = 0
    with open(input_file, 'r', encoding='utf-8') as infile:
        for line in infile:
            line_number += 1
            try:
                json_obj = json.loads(line)
                key_set.update(json_obj.keys())
                if verbose:
                    print(f"Line {line_number} keys: {json_obj.keys()}")
            except json.JSONDecodeError:
                if print_error_message:
                    print(f"Skipping invalid JSON at line {line_number}, line: {line.strip()}")
                continue

    return key_set

def get_json_objects_from_jsonl_yield(input_file, 
                                      print_error_messages: bool = False):
    """
    Reads a JSONL file and yields JSON objects
    Parameters:
    input_file: str - the path to the input JSONL file

    Yields: dict - the next JSON object in the file
    """
    line_number = 0
    with open(input_file, 'r', encoding='utf-8') as infile:
        for line in infile:
            line_number += 1
            try:
                json_obj = json.loads(line)
                yield json_obj
            except json.JSONDecodeError:
                if (print_error_messages):
                    print(f"Skipping invalid JSON line {line_number} line: {line.strip()}")
                continue

def get_list_of_json_objects_from_jsonl(input_file, print_error_messages: bool = False) -> list:
    r"""
    Reads a JSONL file and returns a list of JSON objects
    Parameters:
    input_file: str - the path to the input JSONL file

    Returns: list - a list of JSON objects in the file
    """
    json_list = []
    line_number = 0
    with open(input_file, 'r', encoding='utf-8') as infile:
        for line in infile:
            line_number += 1
            try:
                json_obj = json.loads(line)
                json_list.append(json_obj)
            except json.JSONDecodeError:
                if (print_error_messages):
                    print(f"Skipping invalid JSON line {line_number} line: {line.strip()}")
                continue
    return json_list


def get_average_value_of_jsonl_value(input_file, key, 
                                     print_error_messages: bool = False,
                                     verbose: bool = False) -> float:
    r"""
    Reads a JSONL file and returns the average value of a specified key
    Parameters:
    input_file: str - the path to the input JSONL file
    key: str - the key to calculate the average value for, needs to be numeric
    print_error_messages: bool - whether to print error messages for invalid JSON lines or non-n

    Returns: float - the average value of the specified key
    """
    total = 0
    count = 0
    line_number = 0
    with open(input_file, 'r', encoding='utf-8') as infile:
        for line in infile:
            line_number += 1
            try:
                json_obj = json.loads(line)
                if key in json_obj and isinstance(json_obj[key], (int, float)):
                    total += json_obj[key]
                    count += 1
                    if verbose:
                        print(f"Line {line_number} key {key} value: {json_obj[key]}")
                else:
                    if print_error_messages:
                        print(f"Line {line_number} does not contain key {key} or value is not numeric")
                        continue
            except json.JSONDecodeError:
                if print_error_messages:
                    print(f"Skipping invalid JSON line {line_number} line: {line.strip()}")
                continue

    if count == 0:
        return 0.0
    return total / count

def get_number_of_json_objects_in_jsonl(input_file, 
                                        print_error_messages: bool = False,
                                        verbose: bool = False):
    r"""
    Reads a jsonl object and returns number of valid json and total lines in the file
    parameters:
    input_file - file to read
    
    returns int, int - returns number of objects and then total lines
    """

    number_of_obj = 0
    line_numer = 0

    with open(input_file, 'r', encoding='utf-8') as infile:
        for line in infile:
            line_numer += 1
            #check if line is valid json object
            try:
                json_obj = json.loads(line)
                number_of_obj += 1
            except json.JSONDecodeError:
                if (print_error_messages):
                    print(f"Skipping invalid JSON line {line_numer} line: {line.strip()}")
                continue
    
    return number_of_obj, line_numer

def convert_json_to_jsonl(input_file, output_file, data_key,
                          print_error_messages: bool = False,
                          verbose: bool = False) -> bool:
    r"""
    Takes a json objects and converts it to a jsonl file by taking an array of keys from the json object
    and then writing each object in the data array to a new line in the jsonl file with all other keys being consistent
    Parameters:
    input_file: str - the path to the input JSON file
    output_file: str - the path to the output JSONL file
    data_key_array: list - the keys to extract from each object in the data array and write to the jsonl file
    
    Returns: bool - True if the conversion was successful, False otherwise
    """

    #check if file exists
    try:
        file = open(input_file, "r", encoding="utf-8")
    except FileNotFoundError:
        print(f"File {input_file} not found")
        return False
    
    #open the input file and read the json object
    with open(input_file, 'r', encoding='utf-8') as infile:
        try:
            json_dict = json.load(infile)
        except json.JSONDecodeError:
            if print_error_messages:
                print(f"Input file {input_file} is not valid JSON")
            return False

    #get the data array from the json object
    try:
        data_list = json_dict.get(data_key, [])
    except AttributeError:
        if print_error_messages:
            print(f"Data key {data_key} not found in JSON file")
        return False

    #Read through the data array and write each object to a new line in the jsonl file
    with open(output_file, 'w', encoding='utf-8') as outfile:
        line_numeber = 0
        for item in data_list:
            line_numeber += 1
            json_line = json.dumps(item)
            outfile.write(json_line + '\n')
            if verbose:
                print(f"Wrote JSON on line {line_numeber}, line: {json_line}")

    return True

