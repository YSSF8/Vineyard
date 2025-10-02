# Vineyard

A comprehensive theming tool for customizing the appearance of Windows applications running on Linux through Wine. Vineyard provides an intuitive GUI to create, manage, and apply visual themes to your Wine environment.

## Features

### 🎨 Theme Management
- **Browse Available Themes**: View all `.reg` theme files in your themes directory
- **One-Click Application**: Apply themes with a single click
- **Theme Validation**: Automatic validation against known registry keys to prevent errors
- **Search & Filter**: Quickly find themes by name
- **Edit Existing Themes**: Modify and update your custom themes
- **Delete Themes**: Remove unwanted theme files

### 🔧 Theme Creation
- **Visual Theme Maker**: Create new themes with an intuitive color picker interface
- **Real-time Preview**: See color changes instantly
- **Advanced Registry Editor**: Direct REG file editing with syntax highlighting
- **Syntax Validation**: Automatic detection of syntax errors and warnings
- **RGB/Hex Support**: Support for both RGB values and hexadecimal color codes

### 💻 System Integration
- **Revert Functionality**: Quickly restore default Wine theme
- **Directory Management**: Easy access to themes folder
- **Wine Integration**: Seamless integration with Wine registry system
- **Live Console**: Real-time feedback and logging

## Installation

### Prerequisites
- Python 3.7+
- Wine installed and configured

### Quick Installation
```bash
# Clone or download the Vineyard files
git clone https://github.com/YSSF8/Vineyard.git
cd Vineyard

# Install dependencies from requirements.txt
pip install -r requirements.txt

# Run the application
python main.py
```

### Dependencies
The `requirements.txt` includes:
- **customtkinter==5.2.2**: Modern GUI framework for the interface
- **pathspec==0.12.1**: Path specification handling for file operations

### Setup
1. Ensure all Vineyard files are in the same directory:
   - `main.py`
   - `components/console.py`
   - `components/header.py`
   - `components/header_utilities.py`
   - `components/theme_list.py`
   - `theme_maker.py`
   - `components/reg_highlight.py`
   - `keys.json`
   - `requirements.txt`

2. Install dependencies using the command above

3. Run the application:
```bash
python main.py
```

## Usage

### Applying Themes
1. Launch Vineyard
2. Browse available themes in the main window
3. Click "Apply" on any theme to instantly change your Wine appearance
4. Use the search bar to filter themes by name

### Creating New Themes
1. Click "Theme Maker" in the header
2. Use the Basic tab for visual color selection
3. Or use the Advanced tab for direct REG file editing
4. Save your theme to the themes directory

### Managing Themes
- **Refresh**: Reload the theme list after adding files manually
- **Open Themes Path**: Open the themes directory in your file manager
- **Revert**: Restore default Wine theme settings

## Troubleshooting

### Common Issues
- **Themes not applying**: Ensure Wine is properly installed and the user has registry write permissions
- **Syntax errors**: Use the built-in validator in Theme Maker to check REG file syntax
- **Missing themes**: Click "Refresh" to reload the themes directory
- **Import errors**: Make sure all dependencies are installed using `requirements.txt`

### Console Output
Check the built-in console for detailed error messages and operation logs. The console provides real-time feedback on all operations.

## License

MIT License - see [LICENSE.md](LICENSE.md) for details.

## Contributing

Contributions are welcome! Feel free to submit pull requests or open issues for bugs and feature requests.

## Support

For issues and questions:
1. Check the console output for error details
2. Ensure all dependencies are installed using `requirements.txt`
3. Verify Wine is functioning correctly