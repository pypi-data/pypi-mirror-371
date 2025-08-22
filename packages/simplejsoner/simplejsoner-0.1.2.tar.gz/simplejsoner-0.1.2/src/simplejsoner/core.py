import json
from pathlib import Path
from typing import Any, Dict


class SimpleJsoner:
    def __init__(self, path: str | Path, encoding: str = "utf-8"):
        self.path = Path(path)
        self.encoding = encoding
        self.data = {}
        self._modified = False
    
    def read(path, encoding="utf-8"):
        """
        Returns json data like python object
        """
        try:
            with open(path, "r", encoding=encoding) as file:
                return json.load(file)
        except Exception as e:
            print(e)
    

    def readBytes(path, encoding="utf-8"):
        """
        Returns json data like python object
        """
        try:
            with open(path, "rb", encoding=encoding) as file:
                return file
        except Exception as e:
            print(e)
        

    def write(path, data, encoding="utf-8", indent=4):
        """
        Writes data to json file
        """
        try:
            with open(path, "w", encoding=encoding) as file:
                json.dump(data, file, indent=indent)
        except Exception as e:
            print(e)

    def __enter__(self) -> Dict[str, Any]:
        """
        Вход в with
        """
        try:
            with open(self.path, "r", encoding=self.encoding) as file:
                self.data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            self.data = {}
        self._modified = False
        return self.data

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Выход из with
        """
        if exc_type is None and self._modified:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.path, "w", encoding=self.encoding) as file:
                json.dump(self.data, file, indent=4, ensure_ascii=False)
