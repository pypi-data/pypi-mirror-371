from .core import SimpleJsoner

def __call__(path, encoding="utf-8"):
    """
    Returns SimpleJsoner to use in "with"
    """
    return SimpleJsoner(path, encoding)

read = SimpleJsoner.read
write = SimpleJsoner.write

__all__ = ["SimpleJsoner", "read", "write"]