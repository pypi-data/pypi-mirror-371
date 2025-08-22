# Simple module to make your JSON files management easily

## Installing

```bash
pip install simplejsoner
```

## Import

```python
import simplejsoner as jsoner
```

## Usage

**Simple reading:**

```python
data = jsoner.read("path/to/json/file")  # Returns json data

data = jsoner.readBytes("path/to/json/file")  # Returns json data in bytes
```

**Simple writing:**

```python
data = jsoner.write("path/to/json/file", data)  # Writes data to json file
```

**With:**

```python
# The easiest data updating with with
with jsoner("config.json") as cfg:
    cfg["database"]["host"] = "localhost"
    cfg["database"]["port"] = 5432
    cfg["debug"] = False

# Json file auto update
```

```python
# Only reading is allowed too
with jsoner("config.json") as cfg:
    host = cfg["database"]["host"]
    print(host)
```
