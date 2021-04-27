import json


def load_json(json_message, max_recursion_depth: int = 100, recursion_depth: int = 0):
    """
    tries to load a json formatted string and removes offending characters if present
    https://stackoverflow.com/questions/37805751/simplejson-scanner-jsondecodeerror-invalid-x-escape-sequence-us-line-1-colu

    :param json_message:
    :param max_recursion_depth:
    :param recursion_depth:
    :return:
    """
    try:
        result = json.loads(json_message)
    except Exception as e:
        if recursion_depth >= max_recursion_depth:
            raise ValueError("Max Recursion depth is reached. JSON can´t be parsed!")
        # Find the offending character index:
        idx_to_replace = int(e.pos)
        # Remove the offending character:
        if isinstance(json_message, bytes):
            json_message.decode("utf-8")
        json_message = list(json_message)
        json_message[idx_to_replace] = ' '
        new_message = ''.join(str(m) for m in json_message)
        return load_json(json_message=new_message, max_recursion_depth=max_recursion_depth,
                         recursion_depth=recursion_depth+1)
    return result
