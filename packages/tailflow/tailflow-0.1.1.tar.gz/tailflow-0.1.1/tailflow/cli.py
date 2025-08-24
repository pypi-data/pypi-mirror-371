#!/usr/bin/env python3

import re
import sys
import time

import click

# --- Configuration ---

# Defines the numerical hierarchy for log levels for filtering.
LOG_LEVELS = {
    "DEBUG": 10,
    "INFO": 20,
    "WARNING": 30,
    "ERROR": 40,
    "CRITICAL": 50,
}

# Defines the ANSI escape codes for coloring the output in the terminal.
LOG_COLORS = {
    "DEBUG": "\033[94m",  # Blue
    "INFO": "\033[92m",  # Green
    "WARNING": "\033[93m",  # Yellow
    "ERROR": "\033[91m",  # Red
    "CRITICAL": "\033[95m",  # Magenta
    "RESET": "\033[0m",  # Reset color
}

# Regex to parse key=value pairs. Handles quoted values (with escaped quotes) and unquoted values.
# - Group 1: (\w+) - The key
# - Group 2: ("(?:\\.|[^"\\])*"|\S+) - The value, which is either:
#   - "(?:\\.|[^"\\])*" - A quoted string that allows for escaped characters (e.g., \").
#   - | - OR
#   - \S+ - An unquoted string (any non-whitespace characters).
LOGFMT_REGEX = re.compile(r'(\w+)=("(?:\\.|[^"\\])*"|\S+)')

# --- Core Functions ---


def parse_line(line):
    """
    Parses a single line of logfmt-formatted text into a dictionary.
    Handles both quoted (with escaped quotes) and unquoted values.

    Args:
        line (str): The raw log line.

    Returns:
        dict: A dictionary containing the parsed key-value pairs.
              Returns None if the line is empty or cannot be parsed.
    """
    if not line.strip():
        return None

    matches = LOGFMT_REGEX.findall(line)
    log_data = {}
    for key, value in matches:
        # If the value is quoted, remove the surrounding quotes and unescape internal quotes.
        if value.startswith('"') and value.endswith('"'):
            log_data[key] = value[1:-1].replace('\\"', '"')
        else:
            log_data[key] = value

    # Ensure standard fields exist to prevent KeyErrors later.
    log_data.setdefault("time", "N/A")
    log_data.setdefault("level", "UNKNOWN")
    log_data.setdefault("logger", "N/A")
    log_data.setdefault("msg", "")

    return log_data


def apply_filters(log_data, min_level_val, include_loggers, exclude_loggers):
    """
    Checks if a log entry should be displayed based on the current filters.

    Args:
        log_data (dict): The parsed log entry.
        min_level_val (int): The minimum numerical value for the log level.
        include_loggers (set): A set of logger names to exclusively show.
        exclude_loggers (set): A set of logger names to hide.

    Returns:
        bool: True if the log should be displayed, False otherwise.
    """
    # 1. Filter by Level
    log_level = log_data.get("level", "UNKNOWN").upper()
    current_level_val = LOG_LEVELS.get(log_level, 0)
    if current_level_val < min_level_val:
        return False

    # 2. Filter by Logger
    logger_name = log_data.get("logger")
    if logger_name:
        # Check for exclusion first (highest priority)
        # An entry is excluded if its logger_name starts with any of the excluded prefixes.
        if any(
            logger_name == excl_name or logger_name.startswith(f"{excl_name}.")
            for excl_name in exclude_loggers
        ):
            return False

        # If there's an inclusion list, the logger must match one of the included prefixes.
        if include_loggers and not any(
            logger_name == incl_name or logger_name.startswith(f"{incl_name}.")
            for incl_name in include_loggers
        ):
            return False

    return True


def format_and_print(log_data):
    """
    Formats a parsed log entry into a colored, tabular string and prints it.

    Args:
        log_data (dict): The parsed log entry to print.
    """
    level = log_data.get("level", "UNKNOWN").upper()
    color = LOG_COLORS.get(level, "")
    reset = LOG_COLORS["RESET"]

    # Pad the level string so that the color codes don't misalign the columns.
    # A standard level is max 8 chars (CRITICAL). We add padding.
    colored_level = f"{color}{level:<8}{reset}"

    # Format the output with fixed-width columns for a clean table view.
    # Adjust the padding values (e.g., :<24) as needed for your logs.
    print(
        f"{log_data['time']:<24} | "
        f"{colored_level} | "
        f"{log_data['logger']:<25} | "
        f"{log_data['msg']}"
    )


@click.command(
    help="A simple, colorful log viewer for logfmt-formatted logs.\n\n"
    "It parses, filters, and displays log entries, supporting input from files "
    "or stdin. Use `-f` or `--follow` to continuously watch a file for new entries.\n\n"
    "Examples:\n"
    "  logfmtview.py app.log\n"
    "  logfmtview.py -f app.log\n"
    "  cat app.log | logfmtview.py -l WARNING\n"
    "  logfmtview.py -e app.log\n"
    "  logfmtview.py --level ERROR --logger main -g -requests app.log"
)
@click.argument("file", type=click.File("r"), default=sys.stdin)
@click.option(
    "-l",
    "--level",
    type=click.Choice(list(LOG_LEVELS.keys()), case_sensitive=False),
    default="INFO",
    show_default=True,
    help="Set the minimum log level to display (e.g., INFO, WARNING).",
)
@click.option(
    "-d",
    "--debug",
    is_flag=True,
    help="Enable debug level (shortcut for -l DEBUG).",
)
@click.option(
    "-e",
    "--error",
    is_flag=True,
    help="Enable error level (shortcut for -l ERROR).",
)
@click.option(
    "-f",
    "--follow",
    is_flag=True,
    help="Continuously watch the input file (like tail -F).",
)
@click.option(
    "-g",
    "--logger",
    "loggers",  # This renames the argument passed to the function
    multiple=True,
    help="Filter by logger name. Can be used multiple times.\n"
    "Prefix with '-' to exclude a logger (e.g., -api.access).\n"
    "Example: --logger main --logger tasks -g -requests",
)
def main(file, level, loggers, debug, error, follow):
    """
    Main function to parse arguments and process the log stream.
    """
    # Process logger filters
    include_loggers = {name for name in loggers if not name.startswith("-")}
    exclude_loggers = {name[1:] for name in loggers if name.startswith("-")}

    if debug:
        min_level_val = LOG_LEVELS.get("DEBUG", 0)
    elif error:
        min_level_val = LOG_LEVELS.get("ERROR", 0)
    else:
        min_level_val = LOG_LEVELS.get(level.upper(), 0)

    # Using --follow with stdin is not supported as it's a non-seekable stream.
    if follow and file.name == "<stdin>":
        click.echo(
            "Error: --follow is not supported when reading from stdin.", err=True
        )
        sys.exit(1)

    # Print header
    header_level = "LEVEL"
    print(f"{'TIME':<24} | {header_level:<8} | {'LOGGER':<25} | {'MESSAGE'}")
    print(f"{'-' * 24}-+-{'-' * 8}-+-{'-' * 25}-+-{'-' * 40}")

    def _process_and_print_line(line):
        log_data = parse_line(line)
        if log_data and apply_filters(
            log_data, min_level_val, include_loggers, exclude_loggers
        ):
            format_and_print(log_data)

    try:
        # First, process all existing lines in the file
        for line in file:
            _process_and_print_line(line)

        # If --follow is not enabled, we are done.
        if not follow:
            return

        # In follow mode, continuously read for new lines
        while True:
            line = file.readline()
            if line:
                _process_and_print_line(line)
            else:
                # No new content, sleep briefly to avoid busy-waiting
                time.sleep(0.1)
    except KeyboardInterrupt:
        # Allow clean exit with Ctrl+C when tailing a file
        click.echo("\nExiting.")
        sys.exit(0)
    except Exception as e:
        click.echo(f"An error occurred: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
