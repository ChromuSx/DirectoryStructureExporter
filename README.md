# Directory Structure Exporter

This repository houses a collection of Python scripts designed to create a tree-like structure of a project directory. Initially inspired by the need to document the structure of an ASP.NET Core project, these scripts are highly versatile and can be adapted for various types of directories/projects by adjusting the folders and file types to include or exclude.

## Scripts Overview

- `directory_structure_exporter_interactive.py`: This script interacts with the user to specify both the project folder path and the output file path, offering a highly customizable experience.
- `directory_structure_exporter_hardcoded.py`: Uses predefined paths for both the project directory and the output file, eliminating the need for user input and streamlining the process for consistent usage scenarios.
- `directory_structure_exporter_autopath.py`: Determines the output file path based on the script's current location, simplifying execution by removing the need for manual path specification.

## Key Features

- **Flexibility in Customization**: Tailor the script to your project by specifying which directories to ignore (e.g., `.git`, `.vs`, `bin`) and which file extensions to include (e.g., `.cs`, `.html`, `.css`), among others.
- **Adaptable Output Options**: Depending on the script variant used, the project structure can be output to a user-defined location, a hardcoded path, or a path relative to the script itself.
- **User-friendly Design**: With clear instructions and error handling, the scripts are designed to be accessible to users of varying skill levels.

## Usage Instructions

### For the Interactive Script

1. Execute the script using a terminal or command prompt.
2. Follow the prompts to enter the path of your project folder and the desired output file location. If a directory is specified for the output, you will be asked to name the output `.txt` file.
3. The script will then generate a text file at the chosen location, detailing your project's directory structure.

### For Hardcoded or Autopath Scripts

Execute the desired script directly. There's no need for user input; the output path is either predetermined or calculated automatically.

## Customization

Adjust the `excluded_dirs` and `included_file_extensions` sets within the script to change which directories are skipped and which file types are included in the output.

## System Requirements

- Python 3.6 or later
- No external dependencies are required.

## Example Output

The scripts produce a text file that visually represents your project's directory structure in a hierarchical format, akin to a tree view.

## Contribution Guidelines

Contributions to improve or enhance the scripts are welcome. Feel free to fork this repository and submit pull requests with your suggested changes or fixes.

## License

This project is released under the MIT License. For more details, see the LICENSE file included in the repository.
