# Selenium Website Archiver

This tool automates the process of capturing screenshots and HTML content from specified websites using Selenium WebDriver.

## Features

- Captures full-page screenshots
- Saves complete HTML content
- Supports both new and existing Chrome sessions
- Configurable delay between page loads
- Organized output with timestamps
- JSON summary of results

## Configuration

The tool uses `settings.yaml` for configuration with the following options:

```yaml
urls:
  - List of URLs to archive
output_dir: Directory for archived content
delay_between_pages: Delay in seconds between processing URLs
use_existing_chrome: Controls Chrome session behavior
```

### Chrome Session Control

The `use_existing_chrome` setting determines how Chrome is initialized:

- `false` (default): Starts a new Chrome instance for each run
- `true`: Connects to an existing Chrome session at 127.0.0.1:9222

To use an existing Chrome session:

1. Start Chrome with remote debugging enabled by running this command in PowerShell:
   ```powershell
   & 'C:\Program Files\Google\Chrome\Application\chrome.exe' --remote-debugging-port=9222
   ```
2. Set `use_existing_chrome: true` in settings.yaml

This is useful when you want to:
- Preserve browser state between runs
- Use existing login sessions
- Debug the automation process
- Reduce resource usage by reusing the same browser instance

## Requirements

- Python 3.x
- Selenium WebDriver
- Chrome WebDriver matching your Chrome version
- Chrome browser installed

## Chrome WebDriver Setup

1. Download ChromeDriver from https://sites.google.com/chromium.org/driver/
2. Extract to `~/Downloads/chromedriver-win64/chromedriver-win64/chromedriver.exe`

## Output Structure

```
website_archives/
└── YYYYMMDD_HHMMSS/
    ├── screenshots/
    │   └── domain_name_timestamp.png
    ├── html/
    │   └── domain_name_timestamp.html
    └── results.json
```

## Usage

1. First, decide if you want to use an existing Chrome session:
   - For a new session each time: Set `use_existing_chrome: false` in settings.yaml
   - For an existing session: 
     1. Run Chrome with debugging enabled:
        ```powershell
        & 'C:\Program Files\Google\Chrome\Application\chrome.exe' --remote-debugging-port=9222
        ```
     2. Set `use_existing_chrome: true` in settings.yaml

2. Run the script:
   ```bash
   python a1_test.py
   ```

The script will process each URL according to the settings and create a timestamped directory with all captured content.

## Troubleshooting

If you get an error about Chrome not being found when using `use_existing_chrome: true`, make sure:
1. Chrome is installed in the default location (C:\Program Files\Google\Chrome\Application\chrome.exe)
2. You've started Chrome with the remote debugging port using the command above
3. No other Chrome instances are running with the same debugging port
