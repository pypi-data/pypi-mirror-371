"""
The script serves aviation chart tiles over HTTP and checks for scheduled updates to process new (updated) charts.
When the program is first started it will check if today is the date for updates, if it is, the script will call
chartProcessor.py to download new charts and process them.

If charts chart_processor/charts or any of the subfolders ('sectional', 'terminal-area', 'ifr-enroute-low', 'ifr-enroute-high')
are missing, the script will start downloading charts, and when done will start the server.
The script will download tif file from the closest release date.

To invoke fresh download workflow, just delete charts folder and restart WebServer

The script will also check nightly (at 00:00) if the update is due.

For testing purposes, to run charts update for a particular date without WebServer, provide command argument and run python script:
python3 chartServer.py --test-date 12-26-2024

Optional parameters:
--zoom: Zoom level for tile generation (default: 8)
--chart-type: Specific chart types to process. Available types: helicopter, ifr-enroute-high, 
             ifr-enroute-low, sectional, terminal-area. If not specified, all types are processed.

Examples:
python3 chartServer.py --test-date 12-26-2024 --zoom 10
python3 chartServer.py --test-date 12-26-2024 --chart-type helicopter ifr-enroute-high
python3 chartServer.py --zoom 9 --chart-type sectional  # For initial download with specific settings

@Author: Roman Kozulia
"""
import os
import json
import threading
import argparse
from datetime import datetime, timedelta
from http.server import SimpleHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import subprocess
import logging
from logging.handlers import RotatingFileHandler
import signal
import sys
import platform

"""Configure logging. Log files will be rotating if the size will reach 10 MB"""""
log_file = "./aviation_chart_server/chart_server.log"
log_dir = os.path.dirname(log_file)

# Only create directory if log_dir is not empty (i.e., log file is in a subdirectory)
if log_dir:
    os.makedirs(log_dir, exist_ok=True)

if not os.path.isfile(log_file):
    with open(log_file, 'w') as f:
        f.write("")

max_log_file_size = 10 * 1024 * 1024  # 10 MB
backup_count = 2  # Number of backup files to keep

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        RotatingFileHandler(log_file, maxBytes=max_log_file_size, backupCount=backup_count),
        logging.StreamHandler()
    ]
)

stop_event = threading.Event()
def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Serve aviation chart tiles and check for updates.")
    parser.add_argument(
        "--host",
        type=str,
        help="Host to bind the server to",
        default="localhost"
    )
    parser.add_argument(
        "--port",
        type=int,
        help="Port to run the server on",
        default=8187
    )
    parser.add_argument(
        "--test-date",
        type=str,
        help="Run the script in test mode for a specific date (format: MM-DD-YYYY)."
    )
    parser.add_argument(
        "--zoom",
        type=int,
        help="Zoom level for tile generation (default: 8)",
        default=8
    )
    parser.add_argument(
        "--chart-type",
        nargs="*",
        choices=["helicopter", "ifr-enroute-high", "ifr-enroute-low", "sectional", "terminal-area"],
        help="Chart types to process. If not specified, all chart types will be processed.",
        default=None
    )
    return parser.parse_args()

def handle_exit_signal(signum, frame):
    logging.info("Received termination signal. Stopping update checker.")
    stop_event.set()
    sys.exit(0)

# Load configuration
def load_config(config_path):
    """Load configuration values from the JSON file."""
    if not os.path.exists(config_path):
        logging.error(f"Configuration file {config_path} not found.")
        raise FileNotFoundError(f"Configuration file {config_path} not found.")

    with open(config_path, "r") as f:
        try:
            data = json.load(f)
            logging.info("Configuration file loaded successfully.")
            return data
        except json.JSONDecodeError as e:
            logging.error(f"Error parsing JSON in {config_path}: {e}")
            raise ValueError(f"Error parsing JSON in {config_path}: {e}")

# Global variables that will be set in main()
CONFIG = None
PATHS = None
CHARTS_DIR = None


def initialize_config():
    """Initialize configuration and global variables."""
    global CONFIG, PATHS, CHARTS_DIR
    
    # Always use the default config file
    default_config_path = os.path.join(os.path.dirname(__file__), "config", "chart_service_config.default.json")
    CONFIG = load_config(default_config_path)
    PATHS = CONFIG.get("paths", {})

    # Extract paths from config
    try:
        CHARTS_DIR = os.path.abspath(PATHS["charts"])
    except KeyError as e:
        logging.error(f"Missing required path in configuration: {e}")
        raise ValueError(f"Missing required path in configuration: {e}")



def free_port(port):
    if platform.system() == "Windows":
        logging.info("Port freeing not implemented on Windows.")
        return
    """Free up the port if it is currently in use."""
    try:
        # Find the PID using the port
        result = subprocess.run(
            ["lsof", "-i", f":{port}"],
            capture_output=True,
            text=True,
            check=True
        )
        lines = result.stdout.splitlines()
        if len(lines) > 1:
            # Skip the header and extract PIDs
            for line in lines[1:]:
                pid = int(line.split()[1])
                # Kill the process
                logging.info(f"Killing process {pid} using port {port}")
                subprocess.run(["kill", "-9", str(pid)], check=True)
    except subprocess.CalledProcessError:
        logging.info(f"Port {port} is already free.")

def load_schedule():
    """
    Load the update schedule from the configuration file.
    Ensures that the schedule is sorted in the ascending order.
    Dates are expected in "%m-%d-%Y" format. e.g 12-26-2024
    :return: array of dates
    """
    try:
        # Extract and flatten the update_schedule
        schedule = []
        for year_entry in CONFIG.get("update_schedule", []):
            schedule.extend(year_entry["dates"])
        sorted_schedule = sorted(schedule, key=lambda date: datetime.strptime(date, "%m-%d-%Y"))
        logging.info("Update schedule loaded and sorted successfully.")
        return sorted_schedule

    except Exception as e:
        logging.error(f"Error loading schedule: {e}")
        return []

def is_update_due(schedule, today):
    """Check if the current date matches an update date."""
    return today in schedule

def run_chart_processor(date, zoom_level=None, chart_types=None):
    """
    Run the chart_processor.py script with the given date.
    :param date: date of tif file release.
    :param zoom_level: zoom level for tile generation (optional)
    :param chart_types: list of chart types to process (optional)
    :return:
    """

    try:
        # Get the path to the chart_processor module in the same package
        chart_processor_path = os.path.join(os.path.dirname(__file__), "chart_processor.py")
        
        # Build command
        cmd = ["python3", chart_processor_path, "--chart_date", date]
        
        # Add zoom level if provided
        if zoom_level is not None:
            cmd.extend(["--zoom", str(zoom_level)])
        
        # Add chart types if provided
        if chart_types:
            cmd.append("--chart-type")
            cmd.extend(chart_types)
            
        logging.info(f"Running chart_processor.py with {' '.join(cmd[2:])}")
        result = subprocess.run(
            cmd,
            text=True,
            check=True
        )
        logging.info(f"ChartProcessor output:\n{result.stdout}")
    except subprocess.CalledProcessError as e:
        logging.error(f"ChartProcessor failed with exit code {e.returncode}.")
        logging.error(f"Error output: {e.stderr}")
    except FileNotFoundError as e:
        logging.error(f"ChartProcessor script not found: {e}")
    except Exception as e:
        logging.error(f"Unexpected error running chartProcessor: {e}")

def get_next_update_date(schedule, today_date):
    """
    Find the next update date after today.
    :param schedule: List of update dates in MM-DD-YYYY format
    :param today_date: Today's date as a datetime object or string
    :return: The next update date as a string or None if not found
    """
    # Convert today_date to datetime if it's a string
    if isinstance(today_date, str):
        today_date = datetime.strptime(today_date, "%m-%d-%Y")

    for date_str in schedule:
        update_date = datetime.strptime(date_str, "%m-%d-%Y")
        if update_date > today_date:
            return date_str

    return None  # No future update dates found


def start_update_checker():
    def checker():
        schedule = load_schedule()
        isFirstUpdate = True

        while not stop_event.is_set():
            try:
                now = datetime.now()
                today = now.strftime("%m-%d-%Y")
                logging.info(f"Checking update schedule at: {now.strftime('%Y-%m-%d %H:%M:%S')}")

                # Perform update only at midnight
                if isFirstUpdate or now.hour == 0:
                    if isFirstUpdate:
                        logging.info("Performing initial update update check.")
                        isFirstUpdate = False
                    else:
                        logging.info("Performing scheduled update check.")

                    if is_update_due(schedule, today):
                        logging.info(f"Update due for today: {today}. Running chart processor.")
                        run_chart_processor(today)
                    else:
                        logging.info(f"No update due today: {today}.")
                        nextUpdate = get_next_update_date(schedule,today)
                        logging.info(f"Next update is due: {nextUpdate}")

                # Sleep for 1 hour until the next check
                stop_event.wait(timeout=3600)

            except Exception as e:
                logging.error(f"Unexpected error in update checker loop: {e}", exc_info=True)

    thread = threading.Thread(target=checker, daemon=True)
    thread.start()


class TileRequestHandler(SimpleHTTPRequestHandler):
    """
    Custom handler to serve tiles from the charts directory.
    """

    @property
    def BASE_DIR(self):
        """Get the base directory for serving files."""
        return os.path.abspath(CHARTS_DIR) if CHARTS_DIR else ""

    def translate_path(self, path):
        """Translate the path to serve files from the BASE_DIR."""
        # Strip the leading slash and join the path with the BASE_DIR
        relative_path = path.lstrip("/")
        full_path = os.path.join(self.BASE_DIR, relative_path)
        logging.info(f"Serving file: {full_path}")
        return full_path

class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread for concurrency."""
    pass

def run_server(host=None, port=None):
    """Run the HTTP server to serve tiles."""
    # Use provided arguments or fall back to config
    if host is None or port is None:
        server_config = CONFIG.get("server_config", {})
        if not server_config:
            logging.error("'server_config' is missing in the configuration file.")
            raise ValueError("Error: 'server_config' is missing in the configuration file.")
        
        if host is None:
            host = server_config.get("host", "localhost")
        if port is None:
            port = server_config.get("port", 8187)

    free_port(port)

    # Create and start the server
    server_address = (host, port)
    http = ThreadingHTTPServer(server_address, TileRequestHandler)

    # Print the served addresses
    base_url = f"http://{host}:{port}"
    logging.info("\nServing the following tile directories:")
    logging.info(f"  - Sectional Charts: {base_url}/sectional/{{z}}/{{x}}/{{-y}}.png")
    logging.info(f"  - Terminal Area Charts: {base_url}/terminal-area/{{z}}/{{x}}/{{-y}}.png")
    logging.info(f"  - IFR Enroute Low Charts: {base_url}/ifr-enroute-low/{{z}}/{{x}}/{{-y}}.png")
    logging.info(f"  - IFR Enroute High Charts: {base_url}/ifr-enroute-high/{{z}}/{{x}}/{{-y}}.png")
    logging.info(f"  - Helicopter Charts: {base_url}/helicopter/{{z}}/{{x}}/{{-y}}.png")
    logging.info(f"\nTiles are being served on: {base_url}\n")

    try:
        http.serve_forever()
    except KeyboardInterrupt:
        logging.info("Server stopped.")


def initial_download(zoom_level=None, chart_types=None):
    """
    Perform the initial download of charts if the charts directory is empty, missing specific subdirectories,
    or does not exist.
    :param zoom_level: zoom level for tile generation (optional)
    :param chart_types: list of chart types to process (optional)
    """
    charts_dir = CHARTS_DIR
    required_subdirs = ["sectional", "terminal-area", "ifr-enroute-low", "ifr-enroute-high","helicopter"]

    # Check if the charts directory exists
    if not os.path.exists(charts_dir):
        logging.info(f"Charts directory does not exist. Proceeding with initial download.")
        os.makedirs(charts_dir, exist_ok=True)
        missing_subdirs = required_subdirs  # All subdirectories are missing if the main directory doesn't exist
    else:

        # Check for the presence of required subdirectories
        existing_subdirs = [
            subdir for subdir in os.listdir(charts_dir)
            if os.path.isdir(os.path.join(charts_dir, subdir))
        ]
        missing_subdirs = [subdir for subdir in required_subdirs if subdir not in existing_subdirs]

    if not missing_subdirs:
        logging.info("All required chart subdirectories are present. Skipping initial download.")
        return

    logging.info(f"Missing subdirectories: {missing_subdirs}. Proceeding with initial download.")

    # Get today's date in MM-DD-YYYY format
    today_date = datetime.now().strftime("%m-%d-%Y")
    logging.info(f"Today's date: {today_date}")

    all_dates = load_schedule()
    # Find the closest date
    target_date = None
    today_datetime = datetime.strptime(today_date, "%m-%d-%Y")
    for  schedule_date in all_dates:
        schedule_datetime = datetime.strptime(schedule_date, "%m-%d-%Y")
        if schedule_datetime <= today_datetime:
            target_date = schedule_date  # Keep updating until we pass today
        else:
            break

    if not target_date:
        logging.error("No valid update date found in the schedule.")
        return

    logging.info(f"Determined date for initial download: {target_date}")
    run_chart_processor(target_date, zoom_level, chart_types)


def main():
    """Main entry point for the chart server."""
    
    # Initialize configuration first
    initialize_config()
    
    args = parse_arguments()
    test_date = args.test_date
    zoom_level = args.zoom if args.zoom != 8 else None  # Only pass if different from default
    chart_types = getattr(args, 'chart_type', None)

    signal.signal(signal.SIGINT, handle_exit_signal)
    signal.signal(signal.SIGTERM, handle_exit_signal)

    try:
        if test_date:
            # If a test date is provided, run in test mode
            logging.info(f"Running in test mode for date: {test_date}")
            if zoom_level is not None:
                logging.info(f"Using zoom level: 0-{args.zoom}")
            if chart_types:
                logging.info(f"Processing chart types: {chart_types}")
            run_chart_processor(test_date, args.zoom, chart_types)
        else:
            # Perform initial download if chart folders are missing.
            logging.info("Checking for initial download...")
            if zoom_level is not None:
                logging.info(f"Using zoom level: 0-{args.zoom}")
            if chart_types:
                logging.info(f"Processing chart types: {chart_types}")
            initial_download(args.zoom, chart_types)

            # Start the update checker and HTTP server
            logging.info("Starting the update checker thread.")
            start_update_checker()

            logging.info("Starting the HTTP chart server.")
            run_server(host=args.host, port=args.port)
    finally:
        logging.info("Shutting down the update checker thread.")
        stop_event.set()


if __name__ == "__main__":
    main()
