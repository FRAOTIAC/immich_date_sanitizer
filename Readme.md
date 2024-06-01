# DateSanitizer 

## Overview
The `DateSanitizer` is a Python tool designed to fetch asset data from a specified API endpoint, evaluate and update date fields to ensure they reflect the most reasonable dates based on a set of rules, and then push these updates back to the server. This tool is particularly useful for maintaining the integrity of asset records in databases where date fields may have inaccuracies.

## Features
- Fetch asset data from a RESTful API.
- Evaluate the dates associated with each asset to determine the most reasonable date.
- Update asset records with the most reasonable date and maintain other data integrity.
- Push updates back to the API.
- Utilize local caching to avoid unnecessary API calls.

## Requirements
- Python 3.6 or higher
- `requests` library
- `tqdm` library

## Installation

To get started with the `DateSanitizer`, you need to install the required Python libraries if you haven't already:

```bash
pip install requests tqdm
```

## Configuration

### Command Line Arguments

- `--host`: Host IP and port (e.g., `192.168.2.3:8080`) (required).
- `--api_key`: API key for authentication.
- `--reset_to_exif_original`: Reset all dates to `exifInfo.dateTimeOriginal`. **Warning: This is a potentially dangerous operation. Only use this option if you are certain that you want to reset all modification dates to the creation date.**

### Examples

#### Fix Incorrect Dates (Future Dates and Dates Before 1970)

```bash
python date_sanitizer.py --host 192.168.2.3:8080 --api_key YOUR_API_KEY
```
#### Reset All Dates to Creation Date

```bash
python date_sanitizer.py --host 192.168.2.3:8080 --api_key YOUR_API_KEY --reset_to_exif_original
```
#### Explanation
The --reset_to_exif_original flag, when set, will reset all date fields (fileCreatedAt, localDateTime, fileModifiedAt, and exifInfo.modifyDate) to the value of exifInfo.dateTimeOriginal. Use this option with caution, as it will overwrite all modification dates with the creation date.

If the --reset_to_exif_original flag is not set, the script will only correct dates that are in the future or before 1970 based on the most reasonable date found in the record.

### Environment Setup
Ensure your environment is set up with the necessary Python version and libraries. This project does not require any additional environment setup beyond the Python libraries listed in the requirements.

## Usage

To use the `DateSanitizer`, run the script from the command line, providing necessary arguments. Here's an example command:

```bash
python main.py --host 192.168.2.3:8080 --api_key your_api_key_here 
```

This command initializes the updater, fetches data from the specified API, evaluates dates, updates them as necessary, and pushes the updates back to the API.

## Functionality

1. **Fetching Data**: Checks for cached data before fetching data from the API. If cached data is not found, it fetches fresh data and stores it locally.
2. **Updating Records**: Reads the local data, corrects the dates if they are unrealistic (e.g., future dates, dates before 1970), and updates the records.

## Error Handling
The script includes basic error handling for network issues, API errors, and data format problems. Errors are logged to the console.

## Contributing
Contributions to the `DateSanitizer` are welcome. Please ensure that you write clean code and follow the existing style. Pull requests are the best way to propose changes.

---

This README provides a basic template. Depending on your project's complexity and specific requirements, you might need to expand sections, add more detailed usage examples, or provide additional documentation regarding the logic or architecture.