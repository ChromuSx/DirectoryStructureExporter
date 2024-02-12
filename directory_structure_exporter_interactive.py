from pathlib import Path

# Defines a function to print the directory structure into a file
def print_directory_structure_to_file(root_dir, file_handle, prefix=''):
    # Sets of directories and file extensions to exclude/include
    excluded_dirs = {'.git', '.vs', 'bin', 'obj', 'Debug', 'Release', 'packages'}
    included_file_extensions = {'.sln', '.csproj', '.vbproj', '.cs', '.html', '.cshtml', '.css', '.js'}

    # Converts root_dir to a Path object for easy path manipulation
    root_path = Path(root_dir)
    # Skip the directory if it's in the excluded list
    if root_path.name in excluded_dirs:
        return

    # Writes the directory name to the file
    file_handle.write(f"{prefix}{root_path.name}/\n")
    # Increases the prefix for nested items
    prefix += '    '

    # Iterates through each item in the directory
    for entry in root_path.iterdir():
        if entry.is_dir():
            # Recursively prints the structure of subdirectories
            print_directory_structure_to_file(entry, file_handle, prefix)
        elif entry.suffix in included_file_extensions:
            # Writes the file name if it has a relevant extension
            file_handle.write(f"{prefix}{entry.name}\n")

# Prompts the user to enter the project folder path
project_folder_path = input("Enter the project folder path: ")

# Prompts the user to enter the output file path or folder
output_file_path = input("Enter the output file path or folder: ").strip('"')
output_path = Path(output_file_path)

# Checks if the provided output path is a directory or needs modification
if output_path.is_dir():
    file_name = input("Enter the name of the output txt file: ")
    if not file_name.endswith('.txt'):
        file_name += '.txt'
    output_file_path = output_path.joinpath(file_name)
elif not output_path.suffix:
    file_name = "project_structure.txt"
    output_file_path = output_path.joinpath(file_name)
elif not output_path.name.endswith('.txt'):
    output_file_path = output_path.with_suffix('.txt')

# Attempts to write the directory structure to the specified file
try:
    with open(output_file_path, 'w') as output_file:
        print_directory_structure_to_file(project_folder_path, output_file)
    print(f"The project structure has been written to '{output_file_path}'.")
except Exception as e:
    print(f"Failed to write the file: {e}")