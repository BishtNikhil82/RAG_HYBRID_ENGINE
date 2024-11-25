import os

def list_files(directory: str, extensions: list[str], recursive: bool = False) -> list[str]:
    """
    Lists all files in a given directory with specific extensions, returning full paths.

    Parameters:
    - directory (str): The directory to search in.
    - extensions (list[str]): List of file extensions to look for (e.g., ['.pdf', '.png']).
    - recursive (bool): Whether to search in subdirectories.

    Returns:
    - list[str]: List of complete paths to files matching the specified extensions.
    """
    matching_files = []
    
    # Normalize extensions to ensure each has a leading dot
    extensions = [ext if ext.startswith('.') else f'.{ext}' for ext in extensions]

    # Walk through directory (with recursion if specified)
    for root, _, files in os.walk(directory):
        for file in files:
            if any(file.lower().endswith(ext) for ext in extensions):
                full_path = os.path.join(root, file)
                matching_files.append(full_path)
                
        # Break the loop if not recursive
        if not recursive:
            break

    return matching_files

def get_file_name_and_extension(file_path: str) -> tuple[str, str]:
    """
    Returns the file name and extension from a given file path.

    Parameters:
    - file_path (str): The path of the file.

    Returns:
    - tuple[str, str]: A tuple containing the file name and extension.
    """
    file_name = os.path.basename(file_path)  # Get the file name with extension
    name, extension = os.path.splitext(file_name)  # Split into name and extension
    return name, extension[1:]
