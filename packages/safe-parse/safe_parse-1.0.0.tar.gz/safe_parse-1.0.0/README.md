# Problem

When working with deeply nested dictionaries or JSON data in Python, accessing fields using standard dict syntax (e.g., data["user"]["profile"]["name"]) can be verbose and error-prone. If any key in the chain is missing, a KeyError is raised, which can break your code or require lots of try/except or .get() calls. This makes code harder to read and maintain, especially when dealing with data from APIs or user input where fields may be missing or optional.

`safe_parse` solves this by allowing you to safely access any depth of nested data using dot notation. Missing fields automatically return None (even if you access attributes of None, it will still return None instead of raising an error), so your code stays clean, readable, and robust—no more KeyErrors or repetitive checks.

# safe_parse

A modern Python package for safe, intuitive dot notation access to dictionaries and JSON data. Gracefully returns None for missing fields, supports deep/nested access, and enables robust, error-free data handling—including safe chaining of attribute access at any depth.

## Installation

```bash
pip install safe-parse
```

## Usage

### Basic Example
```python
from safe_parse import SafeParse

payload = {"name": "Alice"}
obj = SafeParse(payload)
print(obj.name)  # Alice
print(obj.age)   # None
print(obj.age == None) # True
```

### Nested Access
```python
payload = {
	"user": {
		"profile": {
			"name": "Bob",
			"age": 30
		},
		"settings": {
			"theme": "dark"
		}
	}
}
obj = SafeParse(payload)
print(obj.user.profile.name)      # Bob
print(obj.user.profile.age)       # 30
print(obj.user.settings.theme)    # dark
print(obj.user.profile.gender)    # None
```

### Using get() with Default
```python
payload = {"x": 10}
obj = SafeParse(payload)
print(obj.get("x"))        # 10
print(obj.get("y", 42))    # 42
```

### Convert Back to dict
```python
payload = {"foo": "bar"}
obj = SafeParse(payload)
print(obj.to_dict())        # {'foo': 'bar'}
```

### Iterating Keys, Values, Items
```python
payload = {"a": 1, "b": 2}
obj = SafeParse(payload)
print(list(obj.keys()))     # ['a', 'b']
print(list(obj.values()))   # [1, 2]
print(list(obj.items()))    # [('a', 1), ('b', 2)]
```

### Boolean and Equality Checks
```python
obj = SafeParse({})
print(obj.missing_field)        # None
print(bool(obj.missing_field))  # False
print(obj.missing_field == None) # True
```

### Safe Chaining
```python
obj = SafeParse({})
print(obj.not_found.anything.deeply.nested)  # None
```

## License

MIT
