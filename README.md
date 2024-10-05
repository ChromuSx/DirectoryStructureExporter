# 🏠 Directory Structure Exporter

Welcome to **Directory Structure Exporter**, a collection of Python scripts designed to create a tree-like structure of a project directory. These scripts were originally inspired by the need to document the structure of an ASP.NET Core project but are highly versatile and can be adapted for various types of directories and projects by customizing the folders and file types to include or exclude.

## 📖 Scripts Overview

- **`directory_structure_exporter_interactive.py`**: Interacts with the user to specify the project folder path and output file path, offering a highly customizable experience.
- **`directory_structure_exporter_hardcoded.py`**: Uses predefined paths for both the project directory and the output file, eliminating the need for user input and simplifying the process for recurring usage scenarios.
- **`directory_structure_exporter_autopath.py`**: Determines the output file path based on the script's current location, making execution easier without needing to manually specify the path.

## 🛠 Key Features

- **🌱 Customization Flexibility**: Customize the script by specifying which directories to ignore (e.g., `.git`, `.vs`, `bin`) and which file extensions to include (e.g., `.cs`, `.html`, `.css`).
- **🗂 Adaptable Output Options**: Depending on the chosen script, the project structure can be exported to a user-defined location, a predefined path, or a path relative to the script itself.
- **💻 User-Friendly Design**: With clear instructions and error handling, the scripts are designed to be accessible to users of varying experience levels.

## 🔗 Usage Instructions

### 🤖 Interactive Script
1. Run the script using a terminal or command prompt.
2. Follow the prompts to enter the project folder path and the desired output file location. If a directory is specified as the output, you will be asked to name the output `.txt` file.
3. The script will generate a text file at the chosen location, detailing the project's directory structure.

### 🧑‍💻 Hardcoded or Autopath Scripts
- Run the desired script directly. No user input is needed; the output path is either predetermined or calculated automatically.

## 💪 Customization
You can modify the `excluded_dirs` and `included_file_extensions` variables within the scripts to specify which directories to exclude and which file types to include in the output.

## 🛠 System Requirements
- **Python 3.6 or higher**
- No external dependencies required.

## 📝 Example Output
The scripts produce a text file that visually represents your project's directory structure in a hierarchical format, similar to a tree view.

## 📚 Contribution Guidelines
Contributions to improve or extend the scripts are welcome! Feel free to fork this repository and submit pull requests with your suggested changes or fixes.

## ❤️ License
This project is licensed under the MIT License. For more details, see the LICENSE file included in the repository.
