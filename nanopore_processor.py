#!/usr/bin/env python3
"""
Nanopore Sequencing Data Processing Script
==========================================

This script automates the processing of Nanopore sequencing data by monitoring
a specified experiment folder for the presence of "final_summary*.txt" files and performing
basecalling using the Dorado tool. It sends email notifications when a
"final_summary" file is detected and saves the basecalling output in the same folder.

Usage:
    python nanopore_processor.py --path "/path/to/experiment_folder"

Author: Your Name
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
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


def setup_logging():
    """Sets up the logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
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
        if file_name.endswith(".txt") and file_name.startswith("final_summary"):
            if event.src_path not in self.processed_files:
                logging.info(f"Final summary file detected: {event.src_path}")
                self.process_file(event.src_path)
                self.processed_files.add(event.src_path)

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
        Performs simplex basecalling.

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

        command = [
            "dorado",
            "basecaller",
            self.experiment_info["model"],
            "--simplex",
            "--kit",
            self.experiment_info["kit_name"],
            pod5_folder,
            "--output",
            output_file
        ]

        self.run_basecalling(command, output_file)

    def run_duplex_basecalling(self, file_path):
        """
        Performs duplex basecalling.

        Args:
            file_path (str): The path to the final summary file.
        """
        logging.info("Running duplex basecalling...")
        pod5_folder = self.find_pod5_folder(file_path)
        if not pod5_folder:
            logging.error("pod5 folder not found.")
            return
        output_folder = os.path.dirname(file_path)
        output_file = os.path.join(output_folder, "cL_inline_unaligned_duplexReads.bam")

        command = [
            "dorado",
            "basecaller",
            self.experiment_info["model"],
            "--duplex",
            "--kit",
            self.experiment_info["kit_name"],
            pod5_folder,
            "--output",
            output_file
        ]

        self.run_basecalling(command, output_file)

    def find_pod5_folder(self, file_path):
        """
        Finds the 'pod5' folder associated with the final summary file.

        Args:
            file_path (str): The path to the final summary file.

        Returns:
            str or None: Path to the pod5 folder or None if not found.
        """
        # Assuming 'pod5' folder is in the same directory as the final summary file or one level up
        possible_paths = [
            os.path.join(os.path.dirname(file_path), "pod5"),
            os.path.join(os.path.dirname(os.path.dirname(file_path)), "pod5")
        ]
        for path in possible_paths:
            if os.path.isdir(path):
                return path
        return None

    def run_basecalling(self, command, output_file):
        """
        Runs the basecalling command using subprocess.

        Args:
            command (list): The command and arguments to run.
            output_file (str): The path to the output file.
        """
        try:
            logging.info(f"Executing command: {' '.join(command)}")
            subprocess.run(command, check=True)
            logging.info(f"Basecalling completed. Output saved to {output_file}")
        except subprocess.CalledProcessError as e:
            logging.error(f"Basecalling failed with error: {e}")
        except Exception as e:
            logging.exception(f"An unexpected error occurred during basecalling: {e}")

    def stop(self):
        """Stops the observer."""
        self.observer.stop()


def get_experiment_info():
    """
    Parses command-line arguments and returns experiment information.

    Returns:
        dict: Experiment information.
    """
    parser = argparse.ArgumentParser(description='Nanopore Sequencing Data Processing')
    parser.add_argument('--path', required=True, help='Path to the experiment directory')
    parser.add_argument('--basecalling_method', default='duplex', choices=['simplex', 'duplex'],
                        help='Basecalling method (default: duplex)')
    parser.add_argument('--model', default='sup', help='Model for basecalling (default: sup)')
    parser.add_argument('--kit_name', default='SQK-NBD114-24', help='Kit name (default: SQK-NBD114-24)')
    parser.add_argument('--email_recipients', default='hgu1@uw.edu', help='Comma-separated email recipients')
    args = parser.parse_args()
    return vars(args)


def main():
    """Main function to start the file watcher."""
    setup_logging()
    experiment_info = get_experiment_info()

    data_path = experiment_info["path"]

    if os.path.isdir(data_path):
        logging.info(f"Monitoring path: {data_path} recursively")

        observer = Observer()
        event_handler = FileWatcher(experiment_info, observer)
        observer.schedule(event_handler, path=data_path, recursive=True)
        observer.start()
        logging.info("File watcher started.")

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
