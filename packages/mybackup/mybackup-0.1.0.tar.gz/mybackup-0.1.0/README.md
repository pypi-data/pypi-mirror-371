# MyBackup - Enhanced Website/IP Info & Backup Tool

## Project Overview

MyBackup is a terminal-based Python tool designed to provide comprehensive details about any website or IP address, along with the ability to create and manage HTML backups of websites. It features a retro-style, color-coded menu interface that is user-friendly and functional.

This tool is ideal for developers, security researchers, and hobbyists who need quick insights and backups from websites with minimal setup.

---

## Features

- **Detailed Website/IP Information**:
  - IP address lookup
  - Reverse DNS resolution
  - GeoIP location data (city, region, country, coordinates)
  - ASN (Autonomous System Number) and ISP details
  - DNS Nameserver (NS) records
  - HTTP and HTTPS status codes, headers, page titles, response time, and page size
  - SSL certificate details (issuer, subject, validity period)
  - robots.txt presence check (search engine crawl rules)
  - Basic port scan of common Internet ports (e.g., 80, 443, 8080)
  - WHOIS domain information (requires `python-whois` package)

- **Create Website Backup**: Save the full HTML content of a website’s homepage to a local file for offline viewing.

- **List and Delete Backup Files**: Manage saved backups with easy listing and deletion.

- **Session Logging**: Keeps a timestamped log of actions and results for auditing purposes.

- **Colorful, Intuitive Terminal UI**: Clean menu-driven interface with colored sections for easy navigation and readability.

---

## Installation

### Prerequisites

- Python 3.7 or higher installed on your system
- Recommended to use a virtual environment

### Recommended Packages

Install required packages via pip:

pip install requests python-whois


If you encounter issues installing or running these packages, ensure your Python and pip installations are correctly set up in your system PATH.

---

## Usage

Run the tool with the following command in your terminal:

python -m mybackup.cli


You will see a menu like this:

==========================================
BACKUP TOOL V2 - Enhanced
Get FULL Website/IP Info
Create Website Backup (HTML)
List Backup Files
Delete Backup File
View Session Log
Exit

==========================================
Enter choice:


### Menu Options Explained

1. **Get FULL Website/IP Info**:  
   Enter a domain or IP to receive comprehensive details as listed in features.

2. **Create Website Backup (HTML)**:  
   Saves the website’s homepage HTML to a file named `<domain>_backup.html`.

3. **List Backup Files**:  
   Displays all backup HTML files currently saved in the working directory.

4. **Delete Backup File**:  
   Allows you to delete a chosen backup file safely.

5. **View Session Log**:  
   Displays the last 20 lines of the session log file which records all actions.

6. **Exit**:  
   Closes the program.

---

## Example

Enter choice: 1
Enter website (no http/https) or IP: example.com
Fetching data for: example.com ...

IP Address:
93.184.216.34

Reverse DNS:
edgecastcdn.net

GeoIP:
{
"city": "Los Angeles",
"region": "California",
"country": "US",
...
}

... (additional detailed info)

---

## Project Structure

mybackup/
├── init.py
├── core.py # Core logic: data fetching, backup, scanning
├── ui.py # Terminal UI with menu & display functions
├── utils.py # Helper validation utilities
├── cli.py # Entry point for running the app
README.md # This file
LICENSE # License details


---

## Contributing

Feel free to fork, open issues, or submit pull requests!  
Improvements are welcome especially around:

- Adding more scanning features
- Enhancing error handling and UI
- Supporting more platforms robustly

---

## License

The project is licensed under the **MIT License**. See the LICENSE file for details.

---

## Support

If you encounter any bugs or have questions, please create an issue or contact me.

---

## Acknowledgments

Inspired by various terminal backup and security tools, and built with love for Python and open source.

