import re

def is_valid_uuid7(uuid_str: str) -> bool:
    """
    Validates whether the given string is a valid UUIDv7.
    Checks:
    - Standard UUID format (8-4-4-4-12 hex digits)
    - Version 7 in the correct position
    - RFC 4122 variant in the correct position
    """
    uuid_regex = re.compile(
        r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-7[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$"
    )
    return bool(uuid_regex.match(uuid_str))
