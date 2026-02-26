Param(
    [string]$EnvName = "venv"
)

# Creates a virtual environment, installs requirements, and runs a quick smoke test.
Write-Host "Creating virtual environment '$EnvName'..."
python -m venv $EnvName

Write-Host "Activating virtual environment..."
.\$EnvName\Scripts\Activate.ps1

Write-Host "Upgrading pip..."
python -m pip install --upgrade pip

Write-Host "Installing dependencies from requirements.txt..."
pip install -r requirements.txt

Write-Host "Running a quick smoke test (does not run the full server, just executes main.py)..."
python main.py

Write-Host "Build script finished. If you want to create a single executable, install PyInstaller and run:`n  pip install pyinstaller`n  pyinstaller --onefile main.py"
