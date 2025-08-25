"""File utilities: read, write, line count, file size, backup, and more."""
import os
import shutil

def read_file(path):
    """Read the contents of a file as text."""
    with open(path, encoding='utf-8') as f:
        return f.read()

def write_file(path, text):
    """Write text to a file."""
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)

def line_count(path):
    """Return the number of lines in a file."""
    with open(path, encoding='utf-8') as f:
        return sum(1 for _ in f)

def file_size(path, human=True):
    """Return the file size in bytes or human-readable format."""
    size = os.path.getsize(path)
    if not human:
        return size
    for unit in ['B','KB','MB','GB','TB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} PB"

def backup(path):
    """Create a backup copy of the file."""
    base, ext = os.path.splitext(path)
    backup_path = f"{base}.bak{ext}"
    shutil.copy2(path, backup_path)
    return backup_path
