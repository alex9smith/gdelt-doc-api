import json

def load_json(json_message, max_recursion_depth: int = 100, recursion_depth: int = 0):
    """
    tries to load a JSON formatted string and removes offending characters if present.

    :param json_message: The JSON string to load.
    :param max_recursion_depth: The maximum recursion depth allowed.
    :param recursion_depth: The current recursion depth.
    :return: The parsed JSON object.
    """
    try:
        if isinstance(json_message, bytes):
            json_message = json_message.decode()  
        
        result = json.loads(json_message)
        
    except ValueError as e:
        if recursion_depth >= max_recursion_depth:
            raise ValueError("Max recursion depth is reached.")

        idx_to_replace = int(e.args[0].split(" ")[-1][:-1])
        json_message = json_message[:idx_to_replace] + ' ' + json_message[idx_to_replace+1:]
        return load_json(json_message, max_recursion_depth, recursion_depth+1)
	
    return result
