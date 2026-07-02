@echo off
setlocal
cd /d "%~dp0"

echo Building EADC Text Crypt...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

python -m PyInstaller --onefile --windowed ^
  --name "EADC_Text_Crypt" ^
  --icon "eadc_icon.ico" ^
  --add-data "eadc_icon.ico;." ^
  --add-data "eadc_icon.png;." ^
  eadc_text_crypt_gui.py

if exist "dist\EADC_Text_Crypt.exe" (
  copy "eadc_icon.ico" "dist\eadc_icon.ico" >nul
  copy "eadc_icon.png" "dist\eadc_icon.png" >nul
  copy "README.md" "dist\README.md" >nul
  copy "LICENSE" "dist\LICENSE" >nul
  echo.
  echo Build complete: dist\EADC_Text_Crypt.exe
) else (
  echo.
  echo ERROR: dist\EADC_Text_Crypt.exe was not created.
)
pause
