# EADC Text Crypt v1.2.1

EADC Text Crypt is a small offline GUI utility for encrypting and decrypting text files using the Fernet encryption approach from the original `text-cryptography` project.

## What is new in v1.2.1

- Maintenance patch for the Windows taskbar icon when using the custom borderless BeOS/X11-style title bar.
- Improved Windows application-window registration when launched from `C:\Program Files`.
- Keeps all v1.2 features: binary/scrambled `.eadc` files, binary/scrambled `.key` exports, and backward compatibility with earlier readable JSON `.eadc` files.

## Important security note

The v1.2.1 binary format is intended to make `.eadc` and `.key` files unreadable in normal text editors and harder to casually inspect. The actual encryption remains Fernet. Anyone who has both the `.eadc` file and the matching `secret.key` can decrypt the text.

Keep the key secure and separate from encrypted files.

## How to use

### Generate a key

Click **Generate New Key**. This creates `secret.key` in the program folder.

Keep this key safe. If you lose the key, encrypted `.eadc` files made with that key cannot be decrypted.

### Import a key

Click **Import Key** and choose an existing `.key` file. The program accepts both v1.2.1 scrambled key files and older raw Fernet key files, then stores the loaded key as `secret.key` in the program folder.

Use this when decrypting files created on another computer or with an older key.

### Encrypt text

1. Generate or import a key.
2. Type, paste, or load text into the **PLAINTEXT** box.
3. Click **ENCRYPT**.
4. Click **Save to .eadc File...**.

### Decrypt a file

1. Make sure the matching `secret.key` is loaded.
2. Click **Open .eadc File...**.
3. Click **DECRYPT**.
4. The decrypted text appears in the **PLAINTEXT** box.

### Clear

The **CLEAR** button clears the current text and file state, but it does **not** delete or unload `secret.key`.

## Build EXE on Windows

Run:

```bat
build_exe.bat
```

The compiled program will be created in the `dist` folder.

## Requirements

- Python 3.10+
- cryptography
- pyinstaller, only needed for building the EXE

Install manually with:

```bash
pip install -r requirements.txt
```

## License

GNU GPL. See `LICENSE`.
