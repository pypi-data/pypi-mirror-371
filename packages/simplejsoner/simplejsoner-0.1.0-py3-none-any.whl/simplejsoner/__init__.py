from .core import SimpleJsoner

read = SimpleJsoner.read
write = SimpleJsoner.write

__all__ = ["SimpleJsoner", "read", "write"]
