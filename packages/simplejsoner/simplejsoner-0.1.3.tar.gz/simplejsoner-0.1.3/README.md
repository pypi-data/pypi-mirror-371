# Simple module to make your JSON files management easily

## Installing

```bash
pip install simplejsoner
```

## Import

```python
from simplejsoner import SimpleJsoner
```

## Usage

**Simple reading:**

```python
from simplejsoner import SimpleJsoner

data = SimpleJsoner.read("path/to/json/file")  # Returns json data

data = SimpleJsoner.readBytes("path/to/json/file")  # Returns json data in bytes
```

or:

```python
import simplejsoner

data = simplejsoner.read("path/to/json/file")

data = simplejsoner.readBytes("path/to/json/file")
```

**Simple writing:**

```python
from simplejsoner import SimpleJsoner

data = SimpleJsoner.write("path/to/json/file", data)  # Writes data to json file
```

or:

```python
import simplejsoner

data = simplejsoner.write("path/to/json/file", data)  # Writes data to json file
```

**With:**

```python
from simplejsoner import SimpleJsoner

# The easiest data updating by with
with SimpleJsoner("config.json") as cfg:
    cfg["database"]["host"] = "localhost"
    cfg["database"]["port"] = 5432
    cfg["debug"] = False

# Json file is automatically updated by itself
```

```python
# Only reading is allowed too
with SimpleJsoner("config.json") as cfg:
    host = cfg["database"]["host"]
    print(host)
```
