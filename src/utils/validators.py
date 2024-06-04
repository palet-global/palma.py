# Function to evaluate if the messages are valid
# Return True if its valid
def is_valid_messages(messages):
    for index, item in enumerate(messages):
        if "role" not in item:
            return False
        if "content" not in item:
            return False
    return True

# Function to evaluate if a value is empty
# Return True if its empty
def is_empty(value):
    if value is None:
        return True
    if isinstance(value, (str, list, dict, set, tuple)):
        return len(value) == 0
    return False

# Function to evaluate if a value is numeric
# Return True if its numeric
def is_numeric(value):
    return isinstance(value, (int, float))

# Function to evaluate if a value is bool
# Return True if its bool
def is_bool(value):
    return isinstance(value, bool)