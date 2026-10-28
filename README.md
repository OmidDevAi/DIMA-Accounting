# DIMA Accounting

**A multilingual desktop accounting application built with Python, PyQt6, and SQLite.**

DIMA Accounting is a Windows-oriented desktop application designed to bring common accounting and business workflows into one interface. The project uses a modular structure, a SQLite database, and a Persian right-to-left (RTL) user interface.

> **Project status:** This README describes the current project structure and documented functionality. Some integrations may require additional implementation or configuration. See the notes below before using the application with real business data.

## Highlights

- **Multilingual interface:** The project includes a language/internationalization module. Check the application's language settings and translation resources to confirm which languages are available in a given build.
- **Persian RTL interface:** Designed to support Persian text and right-to-left layouts.
- **Desktop application:** Built with PyQt6 for a native desktop-style user experience on Windows.
- **Local database:** Uses SQLite for application data.
- **Modular design:** Accounting features are separated into core logic, business modules, and UI pages.
- **Authentication:** Includes a login screen and password hashing.
- **Windows packaging:** Includes a PyInstaller specification and an Inno Setup installer script.

## Main features

The codebase is organized around the following areas:

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
| Modian | Modian-related module; see integration note below |

The exact workflows available in each screen depend on the current implementation and configuration.

## Technology stack

- **Python**
- **PyQt6** — desktop user interface
- **SQLite** — local database
- **jdatetime** — Jalali date support
- **qtawesome** — optional UI icons
- **pyserial** — serial-port support for compatible devices
- **requests** — HTTP requests for integrations
- **PyInstaller** — Windows executable packaging
- **Inno Setup** — Windows installer creation

## Screenshots

Screenshots can be added here to show the dashboard, invoice screens, and language settings.

```text
docs/
└── screenshots/
    ├── dashboard.png
    ├── invoices.png
    └── language-settings.png
```

Replace this example with real screenshots before publishing them.

## Download and install on Windows

If you have a released installer, download it from the project's **GitHub Releases** page and run it on Windows.

1. Download the installer from the release assets.
2. Run the installer.
3. Follow the setup instructions.
4. Launch DIMA Accounting from the installed application shortcut.

**Note:** A setup executable is not included in the source repository by default. Publish it as a GitHub Release asset if you want users to download it directly. Test the installer on a clean Windows account or machine before distributing it.

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

Replace the repository URL above if the repository uses a different name.

### 2. Create and activate a virtual environment

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, review your local PowerShell execution policy or activate the environment using another supported method.

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

Install the dependencies first, then install PyInstaller if it is not already available:

```powershell
pip install pyinstaller
pyinstaller DIMA_Accounting.spec
```

Review the output and the paths referenced by the spec file. The resulting build location depends on the PyInstaller configuration.

## Build the Windows installer

The repository includes `installer.iss`, intended for use with **Inno Setup**.

1. Install Inno Setup on your Windows machine.
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
- Use a strong, unique password before using the application with real data.
- Treat the default demo login (`admin` / `admin123`) as insecure. Change it before any real-world use if the application provides that option. Do not expose a live installation using the default credentials.
- Test backup and recovery procedures before relying on the software for business-critical records.

## Integration notes

- **Modian:** The current project documentation/code indicates that the real Modian API submission is not implemented yet. Do not assume that live submission is available.
- **SMS and device support:** Availability depends on the selected provider, hardware, configuration, and the current implementation.
- **Language availability:** The project contains an internationalization module. List specific languages only after verifying the language resources and testing the language selector in the released build.

## Contributing

Contributions, bug reports, and suggestions are welcome.

When reporting a bug, include:
- Windows version
- Python version (when running from source)
- Steps to reproduce the issue
- The exact error message, if one appears
- Screenshots with personal or business information removed

## Roadmap ideas

Potential future improvements include:
- Completing and testing all language translations
- Adding screenshots and a short demo
- Expanding automated tests
- Documenting backup and restore procedures
- Completing and testing external integrations
- Publishing versioned Windows releases

These are possible improvements, not promises about current functionality.

## License

No license has been specified in this repository yet. Until a license is added, do not assume that the code is open for reuse, redistribution, or commercial use. Choose and add a license before inviting others to reuse the project.

---

**DIMA Accounting** — a modular desktop accounting project built with Python.
