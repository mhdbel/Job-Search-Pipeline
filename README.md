# Job Scraper and Notification Pipeline

[![Python](https://img.shields.io/badge/Python-3.8%20 |%203.9%20|%203.10-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

A Python-based pipeline to automate scraping job listings from various online sources. The pipeline processes this data, identifies potentially interesting job offers based on defined criteria, and notifies users via email and/or a generated PDF report.

---

## Features

- **Scraping**: Extracts job data from multiple configurable job boards.
- **Data Processing**: Cleans and deduplicates scraped data using normalization techniques.
- **Analysis**: Identifies interesting job offers (e.g., based on applicant numbers, though this logic is a placeholder).
- **Notification**: Sends results via email and generates a PDF report.
- **Logging**: Comprehensive logging of pipeline activities and errors to `logs/pipeline.log`.
- **Testing**: Includes a suite of unit tests for core modules.

---

## Table of Contents

1.  [Project Structure](#project-structure)
2.  [Prerequisites](#prerequisites)
3.  [Installation](#installation)
4.  [Configuration](#configuration)
5.  [Usage](#usage)
    *   [Running the Pipeline](#running-the-pipeline)
    *   [Running Tests](#running-tests)
6.  [Security Considerations](#security-considerations)
7.  [Contributing](#contributing)
8.  [License](#license)

---

## Project Structure

Job Search/ ├── config/ # Configuration files │ └── config.yaml # YAML file for URLs, API keys (if any), email settings, etc. ├── logs/ # Log files (created automatically) │ └── pipeline.log # Pipeline activity log ├── output/ # Output files (PDFs, created automatically if path is default) │ └── jobs_report.pdf # Example PDF report name ├── src/ # Source code │ ├── init.py │ ├── analyzer.py # Analysis module │ ├── logger.py # Logging setup module │ ├── main.py # Main script to run the pipeline │ ├── notifier.py # Notification/publishing module │ ├── processor.py # Data processing module │ └── scraper.py # Data scraping module ├── tests/ # Unit tests │ ├── init.py │ ├── test_analyzer.py │ ├── test_notifier.py │ ├── test_processor.py │ └── test_scraper.py ├── .gitignore # Specifies intentionally untracked files that Git should ignore ├── LICENSE # Project license file ├── README.md # This file └── requirements.txt # Python dependencies


---

## Prerequisites

- Python 3.8 or higher installed.
- Pip (Python package installer).
- Access to job boards (the scraper currently uses generic selectors; specific site compatibility may vary).
- For email notifications: A sending email account (e.g., Gmail) with SMTP access details.

---

## Installation

1.  **Clone the repository** (if you haven't already):
    ```bash
    git clone https://github.com/yourusername/job-scraper-pipeline.git # Replace with your repo URL
    cd Job-Search 
    ```

2.  **Create a virtual environment** (recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up configuration**: Copy or rename `config/config.yaml.example` to `config/config.yaml` if an example file is provided, or create `config/config.yaml` manually. See the [Configuration](#configuration) section below for details on required fields.

---

## Configuration

Configuration is managed via the `Job Search/config/config.yaml` file.

Key sections:

-   **`scraping`**: Defines job boards to scrape.
    ```yaml
    scraping:
      job_boards:
        - url: "https://www.indeed.com/jobs"
          query_params:
            q: "software engineer"
            l: "New York"
        # Add more boards as needed
    ```

-   **`cloud`**: Settings related to cloud storage (currently, `storage_bucket` is not actively used by the pipeline).
    ```yaml
    cloud:
      storage_bucket: "gs://your-bucket-name" # Placeholder, not currently used
      pdf_destination: "output/jobs_report.pdf" # Relative path from project root for the PDF report
    ```
    The `output/` directory will be created by the manual test script if it doesn't exist. When running `main.py`, ensure this path is writable.

-   **`email`**: Settings for email notifications.
    ```yaml
    email:
      sender: "your-email@gmail.com" # Your actual sending email address
      recipients:
        - "recipient1@example.com"   # List of recipient email addresses
      smtp_server: "smtp.gmail.com"     # SMTP server for your email provider
      smtp_port: 587                    # SMTP port (usually 587 for TLS, 465 for SSL)
      smtp_password: "your-email-password-or-app-password" # Your email password or App Password
    ```
    *   **Important for Gmail**: If you use Gmail and have 2-Factor Authentication (2FA) enabled, you **must** generate an "App Password" for this pipeline and use it as the `smtp_password`. Using your regular Gmail password might not work and is less secure.
    *   See [Security Considerations](#security-considerations) for advice on handling `smtp_password`.

---

## Usage

### Running the Pipeline

To run the full job scraping and notification pipeline:

1.  Ensure your `config/config.yaml` is correctly set up, especially the `email` section if you want notifications.
2.  From the `Job-Search` project root directory, run:
    ```bash
    python src/main.py
    ```
    Logs will be written to `Job Search/logs/pipeline.log`.
    If configured, a PDF report will be generated at the path specified by `pdf_destination` in your config.

### Running Tests

Unit tests are provided for core modules. To run the tests:

1.  Ensure you have installed dependencies (including any test-specific ones, though current tests rely on built-ins and main requirements).
2.  From the `Job-Search` project root directory, run:
    ```bash
    python -m unittest discover -s tests -p "test_*.py"
    ```
    Or, from the parent directory of `Job-Search`:
    ```bash
    python -m unittest discover -s Job-Search/tests -p "test_*.py"
    ```

---

## Security Considerations

-   **Email Password**: The `smtp_password` in `config.yaml` is highly sensitive.
    -   **DO NOT commit `config.yaml` to version control (e.g., Git) if it contains your real password.**
    -   Add `config.yaml` to your `.gitignore` file: `echo "config/config.yaml" >> .gitignore`
    -   For better security, especially in production or shared environments, avoid storing passwords directly in configuration files. Instead, use environment variables or a secrets management system. The application code would then need to be modified to read the password from these sources.
        *Example (conceptual modification to `notifier.py` to use an environment variable)*:
        ```python
        # In notifier.py, instead of config["email"]["smtp_password"]
        # import os
        # smtp_password = os.environ.get('SMTP_PASSWORD')
        # if not smtp_password:
        #     logger.error("SMTP_PASSWORD environment variable not set.")
        #     # Handle error: skip email or raise exception
        # server.login(msg['From'], smtp_password)
        ```

---

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs, feature requests, or improvements.

(Further details on contribution guidelines can be added here if needed.)

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
