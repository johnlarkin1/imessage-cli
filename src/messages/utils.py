"""Helpful utils for message parsing"""

from typing import Optional
from random import shuffle


def cleanse_message(message_text: Optional[str], cleanse_emojis: bool = False) -> str:
    """This will return a message with no newlines and carriage returns.
    If the cleanse_emoji param is passed in, we will ensure it's all in ascii charset."""
    if message_text is None:
        return ""

    if cleanse_emojis:
        string_unicode = message_text.strip().replace("\r", "").replace("\n", "")
        string_encode = string_unicode.encode("ascii", "ignore")
        string_decode = string_encode.decode()
        return string_decode

    return message_text.strip().replace("\r", "").replace("\n", "")

# name
def mask_name(name_str: str) -> str:
    """If should_mask is enabled, masks the given name string. 
    
    If the name is Thomas for example, we'll only show Th****"""
    if len(name_str) < 2:
        return name_str

    return name_str[:2] + len(name_str[2:]) * '*'

def maybe_mask_name(name_str: str, should_mask: bool) -> str:
    if not should_mask or not name_str:
        return name_str
    return mask_name(name_str)

# phone number
def mask_phone_number(phone_str: str) -> str:
    """If should_mask is enabled, masks the given phone number string (only keeping
    area code). 
    
    e.g. 5131234567 would only show 513******"""
    if len(phone_str) < 2:
        return phone_str

    keep_length = 3
    if phone_str.startswith("+"):
        # Assume only texting us numbers and 
        keep_length += 2

    return phone_str[:keep_length] + len(phone_str[keep_length:]) * '*'

def maybe_mask_phone_number(phone_str: str, should_mask: bool) -> str:
    """Checks the bool if we should mask, then masks accordingly."""
    if not should_mask or not phone_str:
        return phone_str
    return mask_phone_number(phone_str)

# scramble
def scramble_string(input_str: str) -> str:
    input_str_list = list(input_str)
    shuffle(input_str_list)
    return ''.join(input_str_list)

def maybe_scramble_string(input_str: str, should_scramble: bool) -> str:
    """Checks the bool if we should mask, then masks accordingly."""
    if not should_scramble:
        return input_str
    return scramble_string(input_str)

if __name__ == '__main__':
    print(maybe_mask_name("Thomas", True))
    print(maybe_mask_phone_number("5131234567", True))
    print(maybe_mask_phone_number("+15131234567", True))
    print(scramble_string("Sydney Larkin"))
