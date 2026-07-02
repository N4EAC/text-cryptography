# EADC Text Crypt v1.2 Release Notes

## Highlights

- Custom BeOS/X11-style cyber terminal GUI.
- Fernet-based text encryption/decryption.
- New binary/scrambled `.eadc` file format.
- New binary/scrambled `.key` export/import format.
- Backward compatibility with earlier readable JSON `.eadc` files and raw Fernet key files.
- Includes Windows build script and Inno Setup installer script.

## Build

Run `build_exe.bat` from the project folder. The executable will be created at:

```text
dist\EADC_Text_Crypt.exe
```

## Installer

After building the EXE, open `EADC_Text_Crypt_Inno_Setup.iss` in Inno Setup Compiler and compile it.

The installer will be created in:

```text
installer_output\
```
