from .core import SimpleJsoner

jsoner = SimpleJsoner
read = SimpleJsoner.read
write = SimpleJsoner.write

__all__ = ["SimpleJsoner", "read", "write", "jsoner"]