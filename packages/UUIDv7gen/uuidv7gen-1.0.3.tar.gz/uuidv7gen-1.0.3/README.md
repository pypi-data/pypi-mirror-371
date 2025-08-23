# Meet my UUIDv7 Generator

## How To Install
```bash
pip install UUIDv7gen
# or uv add
uv add UUIDv7gen

# or to upgrade
pip install uuid7 --upgrade

```

## Example Usage
```python

from uuid7 import UUIDv7, is_valid_uuid7

# To Generate a UUID
uuid = UUIDv7()
print(uuid)
# Should return a UUIDv7 Value for example "0198d4cf-6591-7fc7-9f93-1a30ef460fba"

# To Validate a UUID
print(is_valid_uuid7(uuid))
# should return a bool value
```
