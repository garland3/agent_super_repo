import pathlib

def search_files(directory, patterns):
    """
    Search for files in a directory based on file extensions.
    
    Args:
        directory (str): Directory to search in
        patterns (str): Semicolon-separated list of file extensions to match (e.g., 'py;txt;md'). 
                       Use '' to match files without extension
    
    Returns:
        list: List of matching file paths as strings
    """
    files = []
    patterns = [pattern.lower() for pattern in patterns.split(';')]

    for path in pathlib.Path(directory).rglob('*'):
        if path.is_file():
            # Handle files with no extension
            if not path.suffix:
                if '' in patterns:
                    files.append(str(path))
                continue
            
            # Handle files with extensions
            ext = path.suffix.lstrip('.').lower()
            if ext in patterns:
                files.append(str(path))

    return files
