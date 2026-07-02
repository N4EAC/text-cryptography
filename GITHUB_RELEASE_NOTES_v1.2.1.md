# EADC Text Crypt v1.2.1 Release Notes

Maintenance patch for v1.2.

## Fixed

- Restores the Windows taskbar icon for the custom borderless BeOS/X11-style window, including when the app is launched from `C:\Program Files` after installation.
- Re-applies the Windows application-window style after startup so Windows Explorer does not treat the GUI as a tool window.
- Keeps the v1.2 binary/scrambled `.eadc` and `.key` format unchanged.

## Build

1. Run `build_exe.bat`.
2. Open `EADC_Text_Crypt_Inno_Setup.iss` in Inno Setup.
3. Compile the installer.
