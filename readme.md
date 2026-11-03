# CSV Merger

A simple desktop application built with Python and Tkinter that allows users to merge multiple CSV and Excel files into a single file.

## Features

* Add multiple CSV or Excel files
* View file name, total columns, and total rows
* Merge multiple files into one
* Remove duplicate rows automatically
* Select specific common columns to merge
* Merge all available columns
* Export merged data as CSV or Excel
* Shows merging time and estimated remaining time
* Displays final file size and merged row count
* Dark-themed graphical user interface
* Optional custom background image

## Technologies Used
* 
* Python
* Tkinter
* Pandas
* Pillow
* OpenPyXL

## Supported Files

Input:

* `.csv`
* `.xlsx`
* `.xls`

Output:

* `.csv`
* `.xlsx`

## Installation

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

### 2. Open the project folder

```bash
cd CSV-Merger
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

## Run the Application

```bash
python main.py
```

## How to Use

1. Click **Add +**.
2. Select one or more CSV/Excel files.
3. The application displays the file name, number of columns, and number of rows.
4. Choose **Remove duplicate rows** if required.
5. Choose **Select specific columns** to select common columns.
6. Choose **Merge all columns** to merge all columns.
7. Click **Merge and save**.
8. Select the output location and file format.
9. The application saves the merged file.

## Project Structure

```text
CSV-Merger/
│
├── main.py
├── background.png
├── README.md
├── requirements.txt
└── .gitignore
```

## Important Notes

If you want to use a custom background image, place the image in the project directory and make sure the filename matches the `BG_IMAGE_PATH` value in the Python file.

For example:

```python
BG_IMAGE_PATH = "background.png"
```

You can also disable the background image by changing:

```python
USE_BG_IMAGE = False
```

## Future Improvements

* Drag and drop file support
* CSV encoding detection
* Large-file processing optimization
* Better error handling
* Excel sheet selection
* Dark/light theme switch
* Export statistics
* Standalone Windows `.exe` release

## Author

**Somendra Dixit**

GitHub: `https://github.com/somendra-dixit1120`

## License

This project is open source and available for personal and educational use.
