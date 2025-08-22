# kurs_dolara

[![PyPI version](https://img.shields.io/pypi/v/kurs-dolara)](https://pypi.org/project/kurs-dolara/)

A simple CLI/TUI application to check the current USD exchange rate from the Central Bank of Bosnia and Herzegovina.

## Screenshot

![Application Screenshot](app_screenshot.png)

## Installation

```bash
pip install kurs_dolara
```

## Usage

To run the application, simply type:

```bash
kurs_dolara
```

### Options

*   `--light`: Use a light theme for the application.
*   `--version`: Show the version of the application.
*   `--cli`: Display the rate in the console and exit.

## Development

This project uses `rye` for project management.

1. Install `rye`:
   ```bash
   curl -sSf https://rye-up.com/get | bash
   ```
2. Install dependencies:
   ```bash
   rye sync
   ```
3. Run the application:
   ```bash
   rye run kurs_dolara
   ```
4. Run tests:
   ```bash
   rye test
   ```