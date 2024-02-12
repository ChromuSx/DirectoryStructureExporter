from pathlib import Path

# Defines a function to print the directory structure into a file. This function recursively traverses the directory structure of a given root directory and writes the structure to a file, filtering based on specified criteria.
def print_directory_structure_to_file(root_dir, file_handle, prefix=''):
    # A set of directory names to exclude from the output. Common directories not relevant to the project structure, such as version control directories and build output directories, are excluded.
    excluded_dirs = {'.git', '.vs', 'bin', 'obj', 'Debug', 'Release', 'packages'}
    # A set of file extensions to include in the output. This filters the files to only include those relevant to the project, such as source code and project files.
    included_file_extensions = {'.sln', '.csproj', '.vbproj', '.cs', '.html', '.cshtml', '.css', '.js'}

    # Converts the root directory path string to a Path object for easy manipulation and checks.
    root_path = Path(root_dir)
    # Checks if the current directory is in the list of excluded directories and returns early if so.
    if root_path.name in excluded_dirs:
        return

    # Writes the current directory name to the file, prefixed by the current indentation level to reflect the structure depth.
    file_handle.write(f"{prefix}{root_path.name}/\n")
    # Increases the indentation for the contents of this directory.
    prefix += '    '

    # Iterates over each item (file or directory) in the current directory.
    for entry in root_path.iterdir():
        if entry.is_dir():
            # If the item is a directory, recursively call this function to print its structure.
            print_directory_structure_to_file(entry, file_handle, prefix)
        elif entry.suffix in included_file_extensions:
            # If the item is a file with an included extension, write its name to the file.
            file_handle.write(f"{prefix}{entry.name}\n")

# Hardcoded paths for the project directory and output file. These should be replaced or made configurable for different projects or environments.
project_folder_path = 'C:/Project'
output_file_path = 'C:/Users/Public/Desktop/project_structure.txt'

# Attempts to open the output file and write the directory structure to it. Error handling is included to catch and report any issues that occur during this process.
try:
    with open(output_file_path, 'w') as output_file:
        print_directory_structure_to_file(project_folder_path, output_file)
    print(f"The project structure has been written to '{output_file_path}'.")
except Exception as e:
    print(f"Failed to write the file: {e}")