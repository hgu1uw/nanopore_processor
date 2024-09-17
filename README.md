# Nanopore Sequencing Data Processing Script

This script automates the processing of Nanopore sequencing data by monitoring a specified experiment folder for the presence of `final_summary*.txt` files and performing basecalling using the Dorado tool. It sends email notifications when a `final_summary` file is detected and saves the basecalling output in the same folder.

## Features

- Processes existing `final_summary*.txt` files upon startup.
- Detects new `final_summary*.txt` files created after the script starts.
- Provides detailed logging for debugging purposes.
- Uses a configuration file for easy parameter adjustments.

## Requirements

- **Python 3.6** or higher.
- **Dorado**: Install the Dorado tool and ensure it is accessible.
- **Watchdog** Python package:
  ```bash
  pip install watchdog
  ```
- **SMTP Credentials**: For sending email notifications, set environment variables for SMTP credentials.

## Setup

### 1. Install Dorado

- **Linux**:
  - Download the Linux version of Dorado from the [Dorado GitHub releases page](https://github.com/nanoporetech/dorado/releases).
  - Extract the tarball:
    ```bash
    tar -xzf dorado-<version>-linux-x64.tar.gz
    ```
  - Add Dorado to your PATH by updating `~/.bashrc` or `~/.profile`.

- **Windows**:
  - Download the Windows version of Dorado from the [Dorado GitHub releases page](https://github.com/nanoporetech/dorado/releases).
  - Ensure the path to `dorado.exe` is specified in the configuration file.

### 2. Set SMTP Credentials

Set the following environment variables:

**Windows (PowerShell)**:

```powershell
[System.Environment]::SetEnvironmentVariable('SMTP_USER', 'your_email@example.com', [System.EnvironmentVariableTarget]::Machine)
[System.Environment]::SetEnvironmentVariable('SMTP_PASSWORD', 'your_smtp_password', [System.EnvironmentVariableTarget]::Machine)
```

**Linux/macOS**:

```bash
export SMTP_USER='your_email@example.com'
export SMTP_PASSWORD='your_smtp_password'
```

### 3. Create Configuration File

Create a `config.ini` file with the necessary settings. Refer to the provided `config.ini` template.

### 4. Run the Script

```bash
python nanopore_processor.py --config "config.ini"
```

## Usage

- The script monitors the experiment folder specified in the `config.ini` file.
- When a `final_summary*.txt` file is detected, it performs simplex or duplex basecalling based on the `basecalling_method` specified in the configuration file.
- The output is saved in the same directory as the `final_summary` file.
- Email notifications are sent to the recipients specified in the configuration file.

## Notes on Differences Between Windows and Linux

- **Dorado Executable Path**:
  - On **Linux**, if Dorado is added to the system PATH, you can set `dorado_executable = dorado` in the `config.ini` file.
  - On **Windows**, you must provide the full path to `dorado.exe`, e.g., `dorado_executable = C:\Program Files\Dorado\dorado.exe`.

- **File Paths**:
  - Use appropriate path formats for your operating system.
  - On Windows, use paths like `C:\path\to\folder`.
  - On Linux, use paths like `/path/to/folder`.

- **Environment Variables**:
  - Setting environment variables differs between Windows and Linux. Follow the instructions in the **Setup** section.

## Troubleshooting

- **Email Sending Issues**:
  - Ensure that SMTP credentials are correctly set.
  - Check for any special characters or spaces in the environment variables.

- **Dorado Not Found**:
  - Verify that the path to the Dorado executable is correct in the `config.ini` file.
  - Ensure that Dorado is installed and accessible.

- **Permissions**:
  - Ensure that the user running the script has read and write permissions for the experiment folder.

## License

This script is released under the MIT License.

