# DIMA Accounting

<p align="center">
  <img src="DIMA_Icon_2_Minimal.png" alt="DIMA Accounting icon" width="120">
</p>

<p align="center">
  <strong>A Persian-first desktop accounting application built with Python, PyQt6, and SQLite.</strong>
</p>

<p align="center">
  <a href="https://github.com/OmidDevAi/DIMA-Accounting/releases/latest">
    <img src="https://img.shields.io/github/v/release/OmidDevAi/DIMA-Accounting?label=Latest%20release" alt="Latest release">
  </a>
  <img src="https://img.shields.io/badge/platform-Windows%2010%20%7C%2011-blue" alt="Windows 10 and 11">
  <img src="https://img.shields.io/badge/Python-PyQt6-yellow" alt="Python and PyQt6">
</p>

<p align="center">
  <a href="https://github.com/OmidDevAi/DIMA-Accounting/releases/latest"><strong>Download for Windows</strong></a>
  ·
  <a href="https://github.com/OmidDevAi/DIMA-Accounting/issues">Report a problem</a>
</p>

DIMA Accounting is a Windows desktop project for common accounting and business workflows. It has a Persian right-to-left (RTL) user interface, a modular Python codebase, and a local SQLite database.

> **Project status:** Version 1.0.0 is the first public Windows release. The project is still evolving. Some integrations and workflows need further implementation, configuration, or testing. Read the security and integration notes before using it with real business data.

## Download

**Latest Windows release: [DIMA Accounting v1.0.0](https://github.com/OmidDevAi/DIMA-Accounting/releases/tag/v1.0.0)**

1. Open the [Releases page](https://github.com/OmidDevAi/DIMA-Accounting/releases).
2. Download `DIMA_Accounting_Setup.exe) from the release assets.
3. Run the installer on Windows 10 or Windows 11.
4. Follow the setup instructions and launch the application.

The installer is distributed as a GitHub Release asset. It is not stored in the source-code repository.

## Highlights

- Persian right-to-left (RTL) user interface.
- Desktop interface built with PyQt6.
- Local SQLite database.
- Modular structure separating core services, business modules, and UI.
- Login screen and password hashing.
- Windows packaging configuration using PyInstaller and Inno Setup.

## Main areas

The codebase is organized around these areas. The exact workflows available in each screen depend on the current implementation and configuration.

| Area | Purpose |
|---|---|
| Dashboard | Main application overview |
| Sales | Sales workflow |
| Purchase | Purchase workflow |
| Invoices | Invoice management |
| Inventory | Inventory-related operations |
| Customers | Customer records |
| Accounting | Accounting functions |
| Checks | Check management |
| Treasury | Cash and treasury operations |
| Barcode scanner | Barcode-scanning support |
| Application settings | Application configuration |
| SMS providers | SMS provider configuration and related functionality |
| Modian | Modian-related module; see integration notes |

## Technology stack

- **Python** — application language
- **PyQt6** — desktop user interface
- **SQLite** — local database
- **jdatetime** — Jalali date support
- **qtawesome** — optional UI icons
- **pyserial** — serial-port support for compatible devices
- **requests** — HTTP requests for integrations
- **PyInstaller** — Windows executable packaging
- **Inno Setup** — Windows installer creation

## Screenshots

Application screenshots will be added here. The repository currently includes the application icon, but not verified screenshots of the running application.

Suggested screenshots:
- Main dashboard
- Sales or invoice screen
- Inventory or customer screen

If you contribute screenshots, remove or hide all real customer names, phone numbers, financial records, and other private information first.

## Run from source

### Requirements

- Windows
- A supported Python version
- Git (optional, for cloning the repository)

### 1. Clone the repository

```powershell
git clone https://github.com/OmidDevAi/DIMA-Accounting.git
cd DIMA-Accounting
```

### 2. Create and activate a virtual environment

```powershell
py -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
```

If PowerShell blocks activation, review your local PowerShell execution policy or use another supported activation method.

### 3. Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Start the application

```powershell
python main.py
```

If the application does not start, check that all dependencies are installed and review the terminal output for the specific error.

## Build a Windows executable

The repository includes `DIMA_Accounting.spec` for PyInstaller.

```powershell
pip install pyinstaller
pyinstaller DIMA_Accounting.spec
```

Review the output and paths referenced by the spec file. The resulting build location depends on the PyInstaller configuration.

## Build the Windows installer

The repository includes `installer.iss`, intended for use with **Inno Setup**.

1. Install Inno Setup.
2. Open `installer.iss` in the Inno Setup Compiler.
3. Check that the source and output paths match your build.
4. Compile the installer.
5. Test the installer on a clean Windows environment.

## Project structure

```text
DIMA-Accounting/
├── core/                    # Core services, database, authentication, i18n
├── modules/                 # Business logic and feature modules
├── ui/                      # PyQt6 windows, pages, and styles
├── main.py                  # Application entry point
├── requirements.txt         # Python dependencies
├── DIMA_Accounting.spec     # PyInstaller build configuration
├── installer.iss            # Inno Setup installer script
├── DIMA_Icon_2_Minimal.png  # Application icon
├── .gitignore
└── README.md
```

## Data and security

- The application uses a local SQLite database.
- Back up business data regularly and store backups securely.
- Do not commit database files, credentials, private keys, or customer information to GitHub.
- The documented default demo login (`admin` / `admin123`) is insecure. Change it before any real-world use, and do not expose an installation using the default credentials.
- Test backup and recovery procedures before relying on the software for business-critical records.

## Integration notes

- **Modian:** Live submission to the Modian system is not implemented yet. Do not assume that live submission is available.
- **SMS and device support:** Availability depends on the selected provider, hardware, configuration, and the current implementation.
- **Language availability:** The project contains an internationalization module. Specific supported languages should be confirmed in the released build before being advertised.

## Contributing

Contributions, bug reports, and suggestions are welcome.

When reporting a bug, include:
- Windows version
- Python version (when running from source)
- Steps to reproduce the issue
- The exact error message, if one appears
- Screenshots with personal or business information removed

## Roadmap

- Add screenshots and a short demo.
- Expand automated tests.
- Document backup and restore procedures.
- Complete and test external integrations.
- Improve language translations and document supported languages.

These are possible improvements, not promises about current functionality.

## License

No license has been specified in this repository yet. Until a license is added, do not assume that the code is open for reuse, redistribution, or commercial use.

---

**DIMA Accounting** — a Persian-first desktop accounting project built with Python.
