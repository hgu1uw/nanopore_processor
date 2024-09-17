# Nanopore Sequencing Data Processing Script

This script automates the processing of Nanopore sequencing data by monitoring a specified folder for the presence of a `final_summary` file and performing basecalling using the Dorado tool. It sends email notifications when a `final_summary` file is detected and saves the basecalling output in the same folder.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Command-Line Arguments](#command-line-arguments)
  - [Environment Variables](#environment-variables)
  - [Example Usage](#example-usage)
- [Logging](#logging)
- [Error Handling](#error-handling)
- [Folder Structure](#folder-structure)
- [Notes](#notes)
- [Troubleshooting](#troubleshooting)
- [License](#license)

## Overview

The script continuously monitors a specified experiment folder for the creation of a `final_summary` file. Upon detecting the file, it performs basecalling using the Dorado tool (supports both simplex and duplex methods) and sends email notifications with experiment details.

## Features

- **Continuous Monitoring**: Watches for new `final_summary` files without manual intervention.
- **Basecalling Automation**: Automates basecalling using the Dorado tool for both simplex and duplex methods.
- **Email Notifications**: Sends detailed email notifications upon processing.
- **Configurable**: Allows configuration via command-line arguments and environment variables.
- **Logging**: Provides detailed logs for monitoring and debugging.
- **Cross-Platform Compatibility**: Uses standard libraries to ensure compatibility across different operating systems.

## Requirements

- **Operating System**: Windows, macOS, or Linux
- **Python**: Version 3.6 or higher
- **Python Packages**:
  - `watchdog`
- **Dorado Tool**: Installed and accessible from the command line

## Installation

1. **Clone or Download the Repository**:

   ```bash
   git clone https://github.com/hgu1uw/nanopore_processor.git
   cd nanopore_processor
   ```

2. **Install Python Packages**:

   Use `pip` to install the required Python packages:

   ```bash
   pip install watchdog
   ```

3. **Install Dorado Tool**:

   Ensure that the Dorado tool is installed and added to your system's PATH. Refer to the [Dorado documentation](https://github.com/nanoporetech/dorado) for installation instructions.

## Configuration

### Environment Variables

Set the following environment variables for SMTP credentials:

- `SMTP_USER`: Your SMTP username (email address).
- `SMTP_PASSWORD`: Your SMTP password or an app-specific password.

**Unix/Linux/macOS**:

```bash
export SMTP_USER='your_email@example.com'
export SMTP_PASSWORD='your_password_or_app_specific_password'
```

**Windows Command Prompt**:

```cmd
set SMTP_USER=your_email@example.com
set SMTP_PASSWORD=your_password_or_app_specific_password
```

**Windows PowerShell**:

```powershell
$env:SMTP_USER = "your_email@example.com"
$env:SMTP_PASSWORD = "your_password_or_app_specific_password"
```

### SMTP Configuration

The script is configured to use Gmail's SMTP server. If you're using a different email provider, update the `smtp_server` and `smtp_port` variables in the script accordingly.

## Usage

Run the script using command-line arguments to specify the configuration options.

### Command-Line Arguments

- `--path` (Required): Path to the experiment data folder.
- `--date` (Required): Experiment date in `YYYYMMDD` format.
- `--basecalling_method`: Basecalling method (`simplex` or `duplex`). Default is `duplex`.
- `--model`: Model for basecalling. Default is `sup`.
- `--kit_name`: Kit name. Default is `SQK-NBD114-24`.
- `--input_type`: Input type (`DNA` or `RNA`). Default is `DNA`.
- `--sample_type`: Sample type (`Human`, `Synthetic`, etc.). Default is `Human`.
- `--amplification_method`: Amplification method (`PCR`, `LAMP`, etc.). Default is `LAMP`.
- `--email_recipients`: Comma-separated list of email recipients. Default is `hgu1@uw.edu`.

**Example**:

```bash
python nanopore_processor.py --path "/path/to/data" --date "20240401" --basecalling_method "duplex" --model "sup" --kit_name "SQK-NBD114-24" --email_recipients "hgu1@uw.edu,jrupp1@uw.edu"
```

### Environment Variables

Ensure that `SMTP_USER` and `SMTP_PASSWORD` environment variables are set as described in the [Environment Variables](#environment-variables) section.

### Example Usage

1. **Navigate to the Script Directory**:

   ```bash
   cd /path/to/nanopore_processor
   ```

2. **Set Environment Variables** (if not already set):

   ```bash
   export SMTP_USER='your_email@example.com'
   export SMTP_PASSWORD='your_password_or_app_specific_password'
   ```

3. **Run the Script**:

   ```bash
   python nanopore_processor.py --path "/path/to/experiment/data" --date "20240401"
   ```

4. **Monitor the Output**:

   The script will log its actions to the console. You can monitor the output to ensure it's working correctly.

## Logging

The script uses Python's `logging` module to provide detailed logs.

- **Log Levels**: INFO, WARNING, ERROR
- **Log Format**: Timestamp, Log Level, Message
- **Log Output**: Console (stdout)

You can modify the logging configuration in the `setup_logging` function within the script if you wish to change log levels or output destinations.

## Error Handling

The script includes comprehensive error handling:

- **SMTP Errors**: Logs exceptions related to email sending.
- **File Processing Errors**: Catches and logs exceptions during file processing.
- **Basecalling Errors**: Logs errors from the Dorado basecalling subprocess.
- **Unexpected Errors**: Catches and logs any unexpected exceptions.

In case of errors, check the console output for detailed log messages.

## Folder Structure

The script expects the following folder structure for the Nanopore sequencing data:

```
<data_path>/
└── <YearMonthDay_experimentDescription>/
    └── <experiment_subfolder>/
        └── <YearMonthDay_timestamp_deviceID_flowcellID_experimentID>/
            ├── final_summary_Description.txt
            └── pod5/
                └── ...
```

- `<data_path>`: The root folder containing all the experiment data.
- `<YearMonthDay_experimentDescription>`: Folder representing an experiment, named with the date and a brief description.
- `<experiment_subfolder>`: A subfolder within the experiment folder.
- `<YearMonthDay_timestamp_deviceID_flowcellID_experimentID>`: Folder containing the `final_summary` file and the `pod5` folder.
- `final_summary_Description.txt`: The `final_summary` file that triggers the processing.
- `pod5/`: Folder containing the pod5 files required for basecalling.

**Note**: The script searches for the most recent folder matching the provided date. Ensure that your folder structure aligns with this expectation.

## Notes

- **Dorado Tool**: Ensure that the Dorado tool is installed and accessible from the command line. Add it to your system's PATH if necessary.
- **Permissions**: Make sure you have the necessary permissions to access the experiment data folder and write output files.
- **SMTP Server**: The script is configured to use Gmail's SMTP server. Update `smtp_server` and `smtp_port` in the script if using a different provider.
- **Email Security**: If using Gmail and you have two-factor authentication enabled, you need to use an app-specific password.

## Troubleshooting

- **No Experiment Folder Found**:
  - **Cause**: The script cannot find a folder matching the specified date.
  - **Solution**: Verify the `--path` and `--date` arguments. Ensure the folder structure matches the expected format.

- **SMTP Authentication Error**:
  - **Cause**: Incorrect SMTP credentials or server settings.
  - **Solution**: Verify `SMTP_USER` and `SMTP_PASSWORD` environment variables. Check your email provider's SMTP settings.

- **Dorado Command Not Found**:
  - **Cause**: Dorado tool is not installed or not in PATH.
  - **Solution**: Install Dorado and ensure it's accessible from the command line.

- **Permission Denied Errors**:
  - **Cause**: Insufficient permissions to read/write files.
  - **Solution**: Run the script with appropriate permissions or adjust file/folder permissions.

- **Script Exits Immediately**:
  - **Cause**: An unhandled exception or incorrect configuration.
  - **Solution**: Run the script with logging enabled and check console output for errors.

## License

This script is released under the MIT License.

## Contact

If you encounter any issues or have questions, please contact the script administrator at `hgu1@uw.edu`.

