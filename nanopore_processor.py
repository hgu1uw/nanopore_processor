#!/usr/bin/env python3
"""
Nanopore Sequencing Data Processing Script
==========================================

This script automates the processing of Nanopore sequencing data by monitoring
a specified experiment folder for the presence of "final_summary*.txt" files and performing
basecalling using the Dorado tool. It sends email notifications when a
"final_summary" file is detected and saves the basecalling output in the same folder.

Features:
- Processes existing "final_summary*.txt" files upon startup.
- Detects new "final_summary*.txt" files created after the script starts.
- Provides detailed logging for debugging purposes.
- Uses a configuration file for easy parameter adjustments.

Usage:
    python nanopore_processor.py --config "config.ini"

Author: Nello
License: MIT
"""

import os
import sys
import subprocess
import time
import smtplib
import logging
import argparse
import signal
import configparser  # For reading the config file
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

#If you want to use the environment variables, uncomment the following code for windows, and windows only
'''
import os

smtp_user = os.getenv('SMTP_USER')
smtp_password = os.getenv('SMTP_PASSWORD')

print(smtp_user, smtp_password)'''

def setup_logging():
    """Sets up the logging configuration."""
    logging.basicConfig(
        level=logging.DEBUG,  # Set logging level to DEBUG for detailed output
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


class FileWatcher(FileSystemEventHandler):
    """
    Watches for the creation of 'final_summary*.txt' files and triggers processing.
    """

    def __init__(self, experiment_info, observer):
        self.experiment_info = experiment_info
        self.processed_files = set()
        self.observer = observer

    def on_created(self, event):
        """Called when a file or directory is created."""
        if event.is_directory:
            return
        file_name = os.path.basename(event.src_path)
        logging.info(f"File created: {event.src_path}")  # Log every created file
        if file_name.endswith(".txt") and file_name.startswith("final_summary"):
            if event.src_path not in self.processed_files:
                logging.info(f"Final summary file detected: {event.src_path}")
                self.process_file(event.src_path)
                self.processed_files.add(event.src_path)
            else:
                logging.debug(f"File {event.src_path} has already been processed.")

    def process_file(self, file_path):
        """Processes the detected 'final_summary' file."""
        try:
            logging.info("Processing file...")
            self.send_email_notification(file_path)
            logging.info("Email notification sent.")

            # Perform basecalling based on the experiment type
            if self.experiment_info["basecalling_method"] == "simplex":
                self.run_simplex_basecalling(file_path)
            elif self.experiment_info["basecalling_method"] == "duplex":
                self.run_duplex_basecalling(file_path)
            else:
                logging.warning(f"Unknown basecalling method: {self.experiment_info['basecalling_method']}")

            logging.info("File processing completed.")

        except Exception as e:
            logging.exception(f"An error occurred while processing the file: {e}")

    def send_email_notification(self, file_path):
        """
        Sends an email notification when the final summary file is generated.

        Args:
            file_path (str): The path to the final summary file.
        """
        logging.info("Sending email notification...")
        subject = "Experiment Summary File Generated"
        body = f"""The final summary file for the experiment has been generated:

File Path: {file_path}

Please check the final summary file for further details.
"""

        msg = MIMEMultipart()
        msg["Subject"] = subject
        smtp_user = os.environ.get('SMTP_USER')
        smtp_password = os.environ.get('SMTP_PASSWORD')
        if not smtp_user or not smtp_password:
            logging.error("SMTP credentials not found in environment variables.")
            return

        msg["From"] = smtp_user
        recipients = [email.strip() for email in self.experiment_info["email_recipients"].split(",")]
        msg["To"] = ", ".join(recipients)
        msg.attach(MIMEText(body, 'plain'))

        smtp_server = "smtp.gmail.com"
        smtp_port = 587

        try:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.sendmail(msg["From"], recipients, msg.as_string())
            logging.info("Email notification sent successfully.")
        except Exception as e:
            logging.exception(f"Failed to send email: {e}")

    def run_simplex_basecalling(self, file_path):
        """
        Performs simplex basecalling using 'dorado basecaller'.

        Args:
            file_path (str): The path to the final summary file.
        """
        logging.info("Running simplex basecalling...")
        pod5_folder = self.find_pod5_folder(file_path)
        if not pod5_folder:
            logging.error("pod5 folder not found.")
            return
        output_folder = os.path.dirname(file_path)
        output_file = os.path.join(output_folder, "simplex_basecalled.bam")

        # Use the model from the config
        model = self.experiment_info["model"]

        # Use the Dorado executable path from the config
        dorado_executable = self.experiment_info["dorado_executable"]

        command = [
            dorado_executable,
            "basecaller",
            model,
            pod5_folder
        ]

        try:
            logging.info(f"Executing command: {' '.join(command)} > {output_file}")
            with open(output_file, 'w') as outfile:
                subprocess.run(command, check=True, stdout=outfile)
            logging.info(f"Simplex basecalling completed. Output saved to {output_file}")
        except subprocess.CalledProcessError as e:
            logging.error(f"Simplex basecalling failed with error: {e}")
        except Exception as e:
            logging.exception(f"An unexpected error occurred during simplex basecalling: {e}")

    def run_duplex_basecalling(self, file_path):
        """
        Performs duplex basecalling using 'dorado duplex'.

        Args:
            file_path (str): The path to the final summary file.
        """
        logging.info("Running duplex basecalling...")
        pod5_folder = self.find_pod5_folder(file_path)
        if not pod5_folder:
            logging.error("pod5 folder not found.")
            return
        output_folder = os.path.dirname(file_path)
        output_file = os.path.join(output_folder, "duplex_basecalled.bam")

        # Use the model from the config
        model = self.experiment_info["model"]

        # Use the Dorado executable path from the config
        dorado_executable = self.experiment_info["dorado_executable"]

        command = [
            dorado_executable,
            "duplex",
            model,
            pod5_folder
        ]

        try:
            logging.info(f"Executing command: {' '.join(command)} > {output_file}")
            with open(output_file, 'w') as outfile:
                subprocess.run(command, check=True, stdout=outfile)
            logging.info(f"Duplex basecalling completed. Output saved to {output_file}")
        except subprocess.CalledProcessError as e:
            logging.error(f"Duplex basecalling failed with error: {e}")
        except Exception as e:
            logging.exception(f"An unexpected error occurred during duplex basecalling: {e}")

    def find_pod5_folder(self, file_path):
        """
        Finds the 'pod5' folder associated with the final summary file.

        Args:
            file_path (str): The path to the final summary file.

        Returns:
            str or None: Path to the pod5 folder or None if not found.
        """
        # Assuming 'pod5' folder is in the same directory or up to two levels up
        current_dir = os.path.dirname(file_path)
        for _ in range(3):  # Check current dir and two levels up
            pod5_path = os.path.join(current_dir, "pod5")
            logging.debug(f"Checking for pod5 folder at: {pod5_path}")
            if os.path.isdir(pod5_path):
                logging.info(f"Found pod5 folder at: {pod5_path}")
                return pod5_path
            current_dir = os.path.dirname(current_dir)
        logging.error("pod5 folder not found.")
        return None

    def stop(self):
        """Stops the observer."""
        self.observer.stop()


def get_experiment_info():
    """
    Parses the configuration file and returns experiment information.

    Returns:
        dict: Experiment information.
    """
    parser = argparse.ArgumentParser(description='Nanopore Sequencing Data Processing')
    parser.add_argument('--config', required=True, help='Path to the configuration file')
    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.read(args.config)

    experiment_info = {
        "path": config.get("Settings", "path"),
        "basecalling_method": config.get("Settings", "basecalling_method", fallback="simplex"),
        "model": config.get("Settings", "model", fallback="hac"),
        "email_recipients": config.get("Settings", "email_recipients"),
        "dorado_executable": config.get("Settings", "dorado_executable", fallback="dorado")
    }

    return experiment_info


def main():
    """Main function to start the file watcher."""
    setup_logging()
    experiment_info = get_experiment_info()

    data_path = experiment_info["path"]

    if os.path.isdir(data_path):
        logging.info(f"Monitoring path: {data_path} recursively")

        # Use PollingObserver for environments where file system events are unreliable
        from watchdog.observers.polling import PollingObserver
        observer = PollingObserver()

        event_handler = FileWatcher(experiment_info, observer)
        observer.schedule(event_handler, path=data_path, recursive=True)
        observer.start()
        logging.info("File watcher started.")

        # Process existing final_summary files upon startup
        logging.info("Checking for existing final_summary files...")
        try:
            for root, dirs, files in os.walk(data_path, followlinks=True):
                logging.debug(f"Entering directory: {root}")
                for file_name in files:
                    logging.debug(f"Found file: {file_name}")
                    if file_name.endswith(".txt") and file_name.startswith("final_summary"):
                        file_path = os.path.join(root, file_name)
                        if file_path not in event_handler.processed_files:
                            logging.info(f"Processing existing final summary file: {file_path}")
                            event_handler.process_file(file_path)
                            event_handler.processed_files.add(file_path)
                        else:
                            logging.debug(f"File {file_path} has already been processed.")
        except Exception as e:
            logging.exception(f"An error occurred while traversing directories: {e}")

        def signal_handler(sig, frame):
            logging.info('Script terminated by user.')
            event_handler.stop()
            observer.join()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)

        try:
            while True:
                time.sleep(1)
        except Exception as e:
            logging.exception(f"An unexpected error occurred: {e}")
        finally:
            observer.stop()
            observer.join()
            logging.info("File watcher stopped.")
    else:
        logging.error(f"Data path does not exist: {data_path}")


if __name__ == "__main__":
    main()
