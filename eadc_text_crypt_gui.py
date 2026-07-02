"""
EADC Text Crypt GUI
Based on N4EAC/text-cryptography Fernet encryption approach.
Creates and reads .eadc encrypted text files.

Retro cyan BeOS/X11-style secure terminal custom decorated interface.
"""

import json
import os
import zlib
import shutil
import sys
from datetime import datetime, timezone
import tkinter as tk
from tkinter import filedialog, messagebox
import tkinter.font as tkfont

try:
    import ctypes
except Exception:
    ctypes = None

try:
    from cryptography.fernet import Fernet, InvalidToken
except ImportError:
    Fernet = None
    InvalidToken = Exception

APP_NAME = "EADC Text Crypt"
APP_ID = "N4EAC.EADCTextCrypt.1_2"
APP_VERSION = "1.2.0"
KEY_FILE = "secret.key"
EADC_MAGIC = "EADC-TEXT-CRYPT"
EADC_VERSION = 2
EADC_LEGACY_VERSION = 1
EADC_FILE_MAGIC = b"EADC-BINARY-1\x1a\n"
EADC_KEY_MAGIC = b"EADC-KEY-1\x1a\n"
EADC_MASK = b"EADC-N4EAC-TEXT-CRYPT-BINARY-MASK"


def _scramble(data: bytes) -> bytes:
    return bytes(b ^ EADC_MASK[i % len(EADC_MASK)] for i, b in enumerate(data))


def encode_binary_container(container: dict) -> bytes:
    raw = json.dumps(container, separators=(",", ":")).encode("utf-8")
    return EADC_FILE_MAGIC + _scramble(zlib.compress(raw, 9))


def decode_binary_container(data: bytes) -> dict:
    if not data.startswith(EADC_FILE_MAGIC):
        raise ValueError("Not a binary EADC file")
    raw = zlib.decompress(_scramble(data[len(EADC_FILE_MAGIC):]))
    return json.loads(raw.decode("utf-8"))


def encode_key_file(key: bytes) -> bytes:
    return EADC_KEY_MAGIC + _scramble(key.strip())


def decode_key_file(data: bytes) -> bytes:
    data = data.strip()
    if data.startswith(EADC_KEY_MAGIC):
        return _scramble(data[len(EADC_KEY_MAGIC):]).strip()
    return data


def app_dir() -> str:
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def resource_path(name: str) -> str:
    base = getattr(sys, "_MEIPASS", app_dir())
    return os.path.join(base, name)


def key_path() -> str:
    return os.path.join(app_dir(), KEY_FILE)


def generate_key(overwrite: bool = False) -> bytes:
    if Fernet is None:
        raise RuntimeError("cryptography package is not installed")
    path = key_path()
    if os.path.exists(path) and not overwrite:
        with open(path, "rb") as f:
            return f.read().strip()
    key = Fernet.generate_key()
    with open(path, "wb") as f:
        f.write(encode_key_file(key))
    return key


def load_key() -> bytes:
    if Fernet is None:
        raise RuntimeError("cryptography package is not installed")
    path = key_path()
    if not os.path.exists(path):
        raise FileNotFoundError(f"Key file not found: {path}")
    with open(path, "rb") as f:
        key = decode_key_file(f.read())
    Fernet(key)
    return key


def encrypt_to_eadc(plain_text: str, key: bytes) -> dict:
    token = Fernet(key).encrypt(plain_text.encode("utf-8")).decode("ascii")
    return {
        "magic": EADC_MAGIC,
        "version": EADC_VERSION,
        "app": APP_NAME,
        "app_version": APP_VERSION,
        "algorithm": "Fernet",
        "encoding": "utf-8",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "ciphertext": token,
    }


def decrypt_eadc(container: dict, key: bytes) -> str:
    if not isinstance(container, dict) or container.get("magic") != EADC_MAGIC:
        raise ValueError("This is not a valid EADC text crypt file.")
    if container.get("version") not in (EADC_VERSION, EADC_LEGACY_VERSION):
        raise ValueError(f"Unsupported EADC version: {container.get('version')}")
    token = container.get("ciphertext")
    if not token:
        raise ValueError("The EADC file does not contain ciphertext.")
    return Fernet(key).decrypt(token.encode("ascii")).decode(container.get("encoding", "utf-8"))


class CyanScrollbar(tk.Canvas):
    """Small custom vertical scrollbar so the retro theme stays black/cyan on Windows."""
    def __init__(self, parent, command=None, width=18, **kwargs):
        super().__init__(parent, width=width, bg="#000000", highlightthickness=1,
                         highlightbackground="#00f6ff", bd=0, **kwargs)
        self.command = command
        self.first = 0.0
        self.last = 1.0
        self._dragging = False
        self._drag_offset = 0
        self.bind("<Configure>", lambda e: self._draw())
        self.bind("<ButtonPress-1>", self._press)
        self.bind("<B1-Motion>", self._drag)
        self.bind("<ButtonRelease-1>", lambda e: setattr(self, "_dragging", False))
        self.bind("<MouseWheel>", self._wheel)

    def set(self, first, last):
        try:
            self.first = max(0.0, min(1.0, float(first)))
            self.last = max(0.0, min(1.0, float(last)))
        except Exception:
            self.first, self.last = 0.0, 1.0
        self._draw()

    def _track(self):
        h = max(1, self.winfo_height())
        return 20, max(21, h - 20)

    def _thumb_coords(self):
        w = max(1, self.winfo_width())
        top, bottom = self._track()
        track = max(1, bottom - top)
        thumb_h = max(24, int(track * max(0.05, self.last - self.first)))
        y1 = top + int(track * self.first)
        y2 = min(bottom, y1 + thumb_h)
        if y2 - y1 < thumb_h:
            y1 = max(top, y2 - thumb_h)
        return 4, y1, w - 4, y2

    def _draw(self):
        self.delete("all")
        w = max(1, self.winfo_width())
        h = max(1, self.winfo_height())
        cyan = "#00f6ff"
        dim = "#007e86"
        self.create_rectangle(0, 0, w - 1, h - 1, outline=cyan, fill="#000000")
        self.create_polygon(w/2, 6, 5, 15, w-5, 15, outline=cyan, fill="#000000")
        self.create_polygon(5, h-15, w-5, h-15, w/2, h-6, outline=cyan, fill="#000000")
        x1, y1, x2, y2 = self._thumb_coords()
        if self.last - self.first < 0.999:
            self.create_rectangle(x1, y1, x2, y2, outline=cyan, fill="#001b1e")
            self.create_line(x1 + 3, y1 + 5, x2 - 3, y1 + 5, fill=dim)
            self.create_line(x1 + 3, y2 - 5, x2 - 3, y2 - 5, fill=dim)

    def _press(self, event):
        x1, y1, x2, y2 = self._thumb_coords()
        top, bottom = self._track()
        if event.y < top:
            if self.command:
                self.command("scroll", -1, "units")
        elif event.y > bottom:
            if self.command:
                self.command("scroll", 1, "units")
        elif y1 <= event.y <= y2:
            self._dragging = True
            self._drag_offset = event.y - y1
        else:
            if self.command:
                self.command("moveto", max(0.0, min(1.0, (event.y - top) / max(1, bottom - top))))

    def _drag(self, event):
        if not self._dragging or not self.command:
            return
        top, bottom = self._track()
        x1, y1, x2, y2 = self._thumb_coords()
        thumb_h = max(1, y2 - y1)
        track = max(1, bottom - top - thumb_h)
        fraction = (event.y - self._drag_offset - top) / track
        self.command("moveto", max(0.0, min(1.0, fraction)))

    def _wheel(self, event):
        if self.command:
            self.command("scroll", -1 if event.delta > 0 else 1, "units")


class EADCApp(tk.Tk):
    def __init__(self):
        self._set_windows_app_id()
        super().__init__()
        self.title(f"{APP_NAME} v{APP_VERSION}")
        self.geometry("1180x760")
        self.minsize(1080, 680)
        self.current_file = None
        self.output_eadc = None
        self._normal_geometry = None
        self._is_maximized = False
        self._drag = (0, 0)
        self._setup_theme()
        self._app_icon_image = None
        self._set_icon()
        self._build_chrome()
        self._build_ui()
        self._bind_shortcuts()
        self._update_key_status()
        if Fernet is None:
            messagebox.showerror("Missing dependency", "Install cryptography first:\n\npip install cryptography")

    def _set_windows_app_id(self):
        if sys.platform == "win32" and ctypes is not None:
            try:
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_ID)
            except Exception:
                pass

    def _setup_theme(self):
        self.c_bg = "#000000"
        self.c_panel = "#02090a"
        self.c_panel2 = "#041112"
        self.c_cyan = "#00f6ff"
        self.c_cyan_dim = "#39cfd6"
        self.c_hot = "#54fbff"
        self.c_entry = "#000607"
        self.c_select = "#004c52"
        self.c_green = "#00ff88"
        self.configure(bg=self.c_bg)
        self.terminal_font = self._choose_terminal_font(12)
        self.small_font = (self.terminal_font[0], 10)
        self.title_font = (self.terminal_font[0], 17, "bold")
        self.button_font = (self.terminal_font[0], 11, "bold")

    def _choose_terminal_font(self, size=11):
        try:
            available = set(tkfont.families(self))
        except Exception:
            available = set()
        for family in ("OCR A Extended", "OCR-A", "Cascadia Mono", "Lucida Console", "Consolas", "Courier New", "Fixedsys"):
            if family in available:
                return (family, size)
        return ("Courier New", size)

    def _set_icon(self):
        ico = resource_path("eadc_icon.ico")
        png = resource_path("eadc_icon.png")
        if os.path.exists(png):
            try:
                self._app_icon_image = tk.PhotoImage(file=png)
                self.iconphoto(True, self._app_icon_image)
            except Exception:
                self._app_icon_image = None
        if os.path.exists(ico):
            try:
                self.iconbitmap(ico)
            except Exception:
                pass

    def _build_chrome(self):
        self.overrideredirect(True)
        self.configure(bg=self.c_cyan)
        self.chrome = tk.Frame(self, bg=self.c_cyan, bd=0)
        self.chrome.pack(fill="both", expand=True, padx=1, pady=1)
        self.titlebar = tk.Frame(self.chrome, bg=self.c_bg, height=46, highlightthickness=1, highlightbackground=self.c_cyan)
        self.titlebar.pack(fill="x")
        self.titlebar.pack_propagate(False)
        self.title_label = tk.Label(
            self.titlebar,
            text=f"SECURE TEXT ENCRYPTION TERMINAL  //  {APP_NAME} v{APP_VERSION}",
            bg=self.c_bg, fg=self.c_cyan, font=self.title_font
        )
        self.title_label.pack(side="left", padx=(18, 8))
        self.controls = tk.Frame(self.titlebar, bg=self.c_bg)
        self.controls.pack(side="right", padx=10)
        self._title_button("—", self._minimize).pack(side="left", padx=4, pady=8)
        self._title_button("□", self._toggle_maximize).pack(side="left", padx=4, pady=8)
        self._title_button("X", self.destroy).pack(side="left", padx=4, pady=8)
        self.scanline = tk.Frame(self.chrome, bg=self.c_cyan, height=2)
        self.scanline.pack(fill="x")
        self.client = tk.Frame(self.chrome, bg=self.c_bg, highlightthickness=1, highlightbackground=self.c_cyan)
        self.client.pack(fill="both", expand=True)
        self.grip = tk.Label(self.client, text="▒", bg=self.c_bg, fg=self.c_cyan_dim, cursor="size_nw_se", font=self.small_font)
        self.grip.place(relx=1.0, rely=1.0, anchor="se")
        for w in (self.titlebar, self.title_label):
            w.bind("<ButtonPress-1>", self._start_move)
            w.bind("<B1-Motion>", self._do_move)
            w.bind("<Double-Button-1>", lambda e: self._toggle_maximize())
        self.grip.bind("<ButtonPress-1>", self._start_resize)
        self.grip.bind("<B1-Motion>", self._do_resize)
        self.bind("<Map>", lambda e: self.after(20, self._restore_borderless_and_taskbar))
        self.after(250, self._force_taskbar_icon)

    def _restore_borderless_and_taskbar(self):
        self.overrideredirect(True)
        self._force_taskbar_icon()

    def _force_taskbar_icon(self):
        # Borderless Tk windows can disappear from the Windows taskbar.
        # Force APPWINDOW style and refresh the shell frame.
        if sys.platform != "win32" or ctypes is None:
            return
        try:
            self.update_idletasks()
            user32 = ctypes.windll.user32
            hwnds = {self.winfo_id()}
            parent = user32.GetParent(self.winfo_id())
            if parent:
                hwnds.add(parent)
            GWL_EXSTYLE = -20
            WS_EX_APPWINDOW = 0x00040000
            WS_EX_TOOLWINDOW = 0x00000080
            SWP_NOMOVE = 0x0002
            SWP_NOSIZE = 0x0001
            SWP_NOZORDER = 0x0004
            SWP_FRAMECHANGED = 0x0020
            for hwnd in hwnds:
                style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
                style = (style | WS_EX_APPWINDOW) & ~WS_EX_TOOLWINDOW
                user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
                user32.SetWindowPos(hwnd, 0, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER | SWP_FRAMECHANGED)
            self.iconphoto(True, self._app_icon_image) if self._app_icon_image else None
            ico = resource_path("eadc_icon.ico")
            if os.path.exists(ico):
                self.iconbitmap(ico)
        except Exception:
            pass

    def _title_button(self, text, command):
        return tk.Button(self.controls, text=text, command=command, width=4, height=1, bg=self.c_bg, fg=self.c_cyan,
                         activebackground=self.c_select, activeforeground="#ffffff", relief="raised", bd=2,
                         highlightthickness=1, highlightbackground=self.c_cyan, font=(self.terminal_font[0], 12, "bold"), takefocus=False)

    def _start_move(self, event):
        if not self._is_maximized:
            self._drag = (event.x_root - self.winfo_x(), event.y_root - self.winfo_y())

    def _do_move(self, event):
        if not self._is_maximized:
            self.geometry(f"+{event.x_root - self._drag[0]}+{event.y_root - self._drag[1]}")

    def _start_resize(self, event):
        self._resize = (self.winfo_width(), self.winfo_height(), event.x_root, event.y_root)

    def _do_resize(self, event):
        if self._is_maximized:
            return
        w, h, x, y = self._resize
        self.geometry(f"{max(980, w + event.x_root - x)}x{max(640, h + event.y_root - y)}")

    def _minimize(self):
        self.overrideredirect(False)
        self.iconify()

    def _toggle_maximize(self):
        if self._is_maximized:
            self.geometry(self._normal_geometry or "1180x760")
            self._is_maximized = False
        else:
            self._normal_geometry = self.geometry()
            self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}+0+0")
            self._is_maximized = True

    def panel(self, parent, title=None, **grid):
        frame = tk.Frame(parent, bg=self.c_bg, highlightthickness=1, highlightbackground=self.c_cyan, bd=0)
        if grid:
            frame.grid(**grid)
        if title:
            lbl = tk.Label(frame, text=f" {title} ", bg=self.c_bg, fg=self.c_cyan, font=(self.terminal_font[0], 11, "bold"))
            lbl.place(x=14, y=-2)
        return frame

    def btn(self, parent, text, command, accent=False):
        b = tk.Button(parent, text=text, command=command, bg=(self.c_hot if accent else self.c_bg), fg=("#001014" if accent else self.c_cyan),
                      activebackground=self.c_select, activeforeground="#ffffff", relief="raised", bd=2,
                      highlightthickness=1, highlightbackground=self.c_cyan, font=self.button_font, padx=12, pady=7,
                      takefocus=False)
        if not accent:
            b.bind("<Enter>", lambda e: b.configure(bg="#001b1e"))
            b.bind("<Leave>", lambda e: b.configure(bg=self.c_bg))
        return b

    def _build_ui(self):
        root = tk.Frame(self.client, bg=self.c_bg)
        root.pack(fill="both", expand=True, padx=18, pady=18)
        root.columnconfigure(0, weight=0, minsize=310)
        root.columnconfigure(1, weight=1)
        root.rowconfigure(0, weight=1)

        # Left key management panel.
        left = self.panel(root, "KEY MANAGEMENT", row=0, column=0, sticky="nsew", padx=(0, 18))
        left.grid_propagate(False)
        left.columnconfigure(0, weight=1)
        left.rowconfigure(8, weight=1)
        tk.Label(left, text="Key loaded:", bg=self.c_bg, fg=self.c_cyan, font=self.terminal_font).grid(row=0, column=0, sticky="w", padx=20, pady=(38, 4))
        self.key_status = tk.Label(left, text="■ checking...", bg=self.c_bg, fg=self.c_green, font=self.terminal_font, anchor="w")
        self.key_status.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 16))
        self.btn(left, "⚿  Generate New Key", self.generate_key_ui).grid(row=2, column=0, sticky="ew", padx=18, pady=7)
        self.btn(left, "▰  Import Key", self.import_key).grid(row=3, column=0, sticky="ew", padx=18, pady=7)
        self.btn(left, "▣  Save Key As...", self.export_key).grid(row=4, column=0, sticky="ew", padx=18, pady=7)
        self.btn(left, "⊗  Clear Key", self.clear_key).grid(row=5, column=0, sticky="ew", padx=18, pady=7)

        info = self.panel(left, "KEY INFO")
        info.grid(row=6, column=0, sticky="ew", padx=18, pady=(14, 7))
        tk.Label(
            info,
            text="The key is used to encrypt and decrypt your files.\n\nKeep it secure and do not share it with others.",
            bg=self.c_bg,
            fg=self.c_cyan,
            justify="left",
            anchor="nw",
            wraplength=245,
            font=self.small_font,
        ).pack(anchor="w", fill="x", padx=16, pady=18)
        self.btn(left, "?  HELP / INSTRUCTIONS", self.show_help).grid(row=9, column=0, sticky="ew", padx=18, pady=(10, 18))

        # Main workspace.
        main = tk.Frame(root, bg=self.c_bg)
        main.grid(row=0, column=1, sticky="nsew")
        main.columnconfigure(0, weight=1)
        main.rowconfigure(0, weight=3)
        main.rowconfigure(2, weight=2)

        plain_panel = self.panel(main, "PLAINTEXT (ENTER OR LOAD TEXT TO ENCRYPT)", row=0, column=0, sticky="nsew")
        plain_panel.columnconfigure(0, weight=1)
        plain_panel.columnconfigure(1, weight=0)
        plain_panel.rowconfigure(0, weight=1)
        self.input_text = tk.Text(plain_panel, wrap="word", undo=True, bg=self.c_entry, fg=self.c_cyan, insertbackground=self.c_cyan,
                                  selectbackground=self.c_select, selectforeground="#ffffff", relief="flat", bd=0,
                                  highlightthickness=1, highlightbackground=self.c_cyan, padx=12, pady=12, font=(self.terminal_font[0], 13))
        self.input_text.grid(row=0, column=0, sticky="nsew", padx=(16, 8), pady=(28, 14))
        self.input_scroll = CyanScrollbar(plain_panel, command=self.input_text.yview)
        self.input_scroll.grid(row=0, column=0, sticky="nse", padx=(0, 8), pady=(28, 14))
        self.input_text.configure(yscrollcommand=self.input_scroll.set)
        pr = tk.Frame(plain_panel, bg=self.c_bg)
        pr.grid(row=0, column=1, sticky="ns", padx=(6, 16), pady=(38, 14))
        self.btn(pr, "▰ Load Text File...", self.load_text_file).pack(fill="x", pady=(0, 12))
        self.btn(pr, "▣ Paste from Clipboard", self.paste_clipboard).pack(fill="x")

        arrow = tk.Label(main, text="↓", bg=self.c_bg, fg=self.c_cyan, font=(self.terminal_font[0], 18, "bold"), relief="raised", bd=2, highlightthickness=1, highlightbackground=self.c_cyan)
        arrow.grid(row=1, column=0, pady=4)

        cipher_panel = self.panel(main, "CIPHERTEXT (ENCRYPTED OUTPUT)", row=2, column=0, sticky="nsew")
        cipher_panel.columnconfigure(0, weight=1)
        cipher_panel.columnconfigure(1, weight=0)
        cipher_panel.rowconfigure(0, weight=1)
        self.output_text = tk.Text(cipher_panel, wrap="word", bg=self.c_entry, fg=self.c_cyan, insertbackground=self.c_cyan,
                                   selectbackground=self.c_select, selectforeground="#ffffff", relief="flat", bd=0,
                                   highlightthickness=1, highlightbackground=self.c_cyan, padx=12, pady=12, font=(self.terminal_font[0], 12))
        self.output_text.grid(row=0, column=0, sticky="nsew", padx=(16, 8), pady=(28, 14))
        self.output_scroll = CyanScrollbar(cipher_panel, command=self.output_text.yview)
        self.output_scroll.grid(row=0, column=0, sticky="nse", padx=(0, 8), pady=(28, 14))
        self.output_text.configure(yscrollcommand=self.output_scroll.set)
        cr = tk.Frame(cipher_panel, bg=self.c_bg)
        cr.grid(row=0, column=1, sticky="ns", padx=(6, 16), pady=(38, 14))
        self.btn(cr, "▣ Save to .eadc File...", self.save_eadc).pack(fill="x", pady=(0, 12))
        self.btn(cr, "▤ Copy to Clipboard", self.copy_ciphertext).pack(fill="x", pady=(0, 12))
        self.btn(cr, "▰ Open .eadc File...", self.open_eadc).pack(fill="x")

        bottom = tk.Frame(main, bg=self.c_bg)
        bottom.grid(row=3, column=0, sticky="ew", pady=(12, 0))
        self.btn(bottom, "🔒  ENCRYPT", self.encrypt_ui).pack(side="left", padx=(0, 14))
        self.btn(bottom, "🔓  DECRYPT", self.decrypt_ui).pack(side="left", padx=(0, 14))
        self.btn(bottom, "🧹  CLEAR", self.clear_workspace).pack(side="left")

        statusbar = tk.Frame(self.client, bg=self.c_bg, highlightthickness=1, highlightbackground=self.c_cyan, height=42)
        statusbar.pack(fill="x", side="bottom")
        statusbar.pack_propagate(False)
        self.status = tk.Label(statusbar, text="SECURE STATUS:  Ready", bg=self.c_bg, fg=self.c_cyan, font=self.small_font, anchor="w")
        self.status.pack(side="left", padx=20)
        tk.Label(statusbar, text=f"{APP_NAME} v{APP_VERSION}", bg=self.c_bg, fg=self.c_cyan_dim, font=self.small_font).pack(side="right", padx=50)

    def _bind_shortcuts(self):
        self.bind_all("<Control-e>", lambda e: self.encrypt_ui())
        self.bind_all("<Control-d>", lambda e: self.decrypt_ui())
        self.bind_all("<Control-o>", lambda e: self.open_eadc())
        self.bind_all("<Control-n>", lambda e: self.clear_workspace())
        self.bind_all("<Control-k>", lambda e: self.import_key())

    def _update_key_status(self):
        if os.path.exists(key_path()):
            self.key_status.config(text="■ secret.key", fg=self.c_green)
        else:
            self.key_status.config(text="□ no key loaded", fg=self.c_cyan_dim)

    def set_status(self, msg):
        self.status.config(text=f"SECURE STATUS:  {msg}")

    def generate_key_ui(self):
        try:
            path = key_path()
            if os.path.exists(path):
                ok = messagebox.askyesno("Key already exists", "Overwrite secret.key?\n\nOlder .eadc files need the old key unless you kept a backup.")
                if not ok:
                    self.set_status("Existing key kept")
                    return
            generate_key(overwrite=True)
            self._update_key_status()
            self.set_status("New secret.key generated")
            messagebox.showinfo("Key generated", f"New key saved to:\n{path}")
        except Exception as exc:
            messagebox.showerror("Key error", str(exc))

    def import_key(self):
        src = filedialog.askopenfilename(title="Import Fernet secret.key", filetypes=[("Key files", "*.key"), ("All files", "*.*")])
        if not src:
            return
        try:
            with open(src, "rb") as f:
                key = decode_key_file(f.read())
            Fernet(key)
            with open(key_path(), "wb") as out:
                out.write(encode_key_file(key))
            self._update_key_status()
            self.set_status("Key imported")
        except Exception as exc:
            messagebox.showerror("Invalid key", f"This does not look like a valid Fernet key.\n\n{exc}")

    def export_key(self):
        try:
            key = load_key()
        except Exception as exc:
            messagebox.showerror("No key", str(exc))
            return
        dst = filedialog.asksaveasfilename(title="Save key as", defaultextension=".key", filetypes=[("Key files", "*.key"), ("All files", "*.*")])
        if dst:
            with open(dst, "wb") as f:
                f.write(encode_key_file(key))
            self.set_status("Scrambled key copy saved")

    def clear_key(self):
        if not os.path.exists(key_path()):
            self.set_status("No key to clear")
            return
        if messagebox.askyesno("Clear Key", "Remove secret.key from this program folder?\n\nThis does not affect backup copies."):
            os.remove(key_path())
            self._update_key_status()
            self.set_status("Key cleared")

    def load_text_file(self):
        src = filedialog.askopenfilename(
            title="Load text or EADC file",
            filetypes=[
                ("Text and EADC files", "*.txt *.md *.csv *.log *.eadc"),
                ("EADC encrypted files", "*.eadc"),
                ("Text files", "*.txt *.md *.csv *.log"),
                ("All files", "*.*"),
            ],
        )
        if not src:
            return

        # User-friendly safety: if an encrypted .eadc file is selected from
        # the Load Text button, route it to the encrypted-file workflow.
        # This prevents the EADC JSON from being loaded as plaintext and
        # accidentally encrypted again.
        if src.lower().endswith(".eadc"):
            self._load_eadc_path(src)
            return

        try:
            with open(src, "r", encoding="utf-8") as f:
                data = f.read()
        except UnicodeDecodeError:
            with open(src, "r", encoding="latin-1") as f:
                data = f.read()
        self.input_text.delete("1.0", "end")
        self.input_text.insert("1.0", data)
        self.output_eadc = None
        self.output_text.delete("1.0", "end")
        self.set_status(f"Loaded text: {os.path.basename(src)}")

    def paste_clipboard(self):
        try:
            self.input_text.insert("insert", self.clipboard_get())
            self.set_status("Clipboard pasted")
        except Exception:
            messagebox.showwarning("Clipboard", "No text clipboard content found.")

    def copy_ciphertext(self):
        data = self.output_text.get("1.0", "end-1c")
        if not data.strip():
            return
        self.clipboard_clear()
        self.clipboard_append(data)
        self.set_status("Ciphertext copied")

    def clear_workspace(self):
        self.current_file = None
        self.output_eadc = None
        self.input_text.delete("1.0", "end")
        self.output_text.delete("1.0", "end")
        self._update_key_status()
        self.set_status("Workspace cleared; loaded secret.key was kept")

    def encrypt_ui(self):
        try:
            key = load_key()
        except FileNotFoundError:
            if messagebox.askyesno("No key", "No secret.key was found. Generate one now?"):
                self.generate_key_ui()
                try:
                    key = load_key()
                except Exception:
                    return
            else:
                return
        except Exception as exc:
            messagebox.showerror("Key error", str(exc))
            return
        plain = self.input_text.get("1.0", "end-1c")
        if not plain.strip():
            messagebox.showwarning("Nothing to encrypt", "Enter or load text first.")
            return
        self.output_eadc = encrypt_to_eadc(plain, key)
        self.output_text.delete("1.0", "end")
        self.output_text.insert("1.0", self._eadc_display_summary(self.output_eadc, unsaved=True))
        self.set_status("Encrypted; save to binary .eadc when ready")

    def save_eadc(self):
        if self.output_eadc is None:
            self.encrypt_ui()
            if self.output_eadc is None:
                return
        dst = filedialog.asksaveasfilename(title="Save encrypted EADC file", defaultextension=".eadc", filetypes=[("EADC encrypted text", "*.eadc"), ("All files", "*.*")])
        if not dst:
            return
        if not dst.lower().endswith(".eadc"):
            dst += ".eadc"
        with open(dst, "wb") as f:
            f.write(encode_binary_container(self.output_eadc))
        self.current_file = dst
        self.set_status(f"Saved: {os.path.basename(dst)}")

    def _read_eadc_file(self, src):
        with open(src, "rb") as f:
            data = f.read()
        if data.startswith(EADC_FILE_MAGIC):
            return decode_binary_container(data), "binary"
        # Backward compatibility for v1.1 and earlier readable JSON .eadc files.
        try:
            container = json.loads(data.decode("utf-8"))
            return container, "legacy-json"
        except Exception as exc:
            raise ValueError(f"Could not decode EADC file as v1.2 binary or legacy JSON. {exc}")

    def _eadc_display_summary(self, container, unsaved=False, file_mode="binary"):
        cipher = container.get("ciphertext", "") if isinstance(container, dict) else ""
        created = container.get("created_utc", "unknown") if isinstance(container, dict) else "unknown"
        state = "NOT YET SAVED" if unsaved else "LOADED"
        return (
            f"EADC SECURE PACKAGE: {state}\n"
            f"FORMAT: binary/scrambled .eadc v1.2\n"
            f"ALGORITHM: Fernet\n"
            f"CREATED UTC: {created}\n"
            f"CIPHERTEXT BYTES: {len(cipher)}\n\n"
            "The saved .eadc file is intentionally binary/scrambled so Notepad will not show readable JSON.\n"
            "Use this program with the matching secret.key to decrypt it.\n"
        )

    def _load_eadc_path(self, src):
        try:
            container, mode = self._read_eadc_file(src)
            if container.get("magic") != EADC_MAGIC:
                raise ValueError("Not an EADC text crypt file")
        except Exception as exc:
            messagebox.showerror("Open failed", f"Could not read this .eadc file.\n\n{exc}")
            return False
        self.current_file = src
        self.output_eadc = container
        self.output_text.delete("1.0", "end")
        if mode == "legacy-json":
            self.output_text.insert("1.0", self._eadc_display_summary(container, file_mode=mode) + "\nLegacy JSON file loaded. Saving again will convert it to v1.2 binary format.\n")
        else:
            self.output_text.insert("1.0", self._eadc_display_summary(container, file_mode=mode))
        self.input_text.delete("1.0", "end")
        self.set_status(f"Opened: {os.path.basename(src)}; click DECRYPT")
        return True

    def open_eadc(self):
        src = filedialog.askopenfilename(
            title="Open EADC encrypted text",
            filetypes=[
                ("EADC encrypted files", "*.eadc"),
                ("All files", "*.*"),
            ],
        )
        if not src:
            return
        self._load_eadc_path(src)

    def decrypt_ui(self):
        if self.output_eadc is None:
            raw = self.output_text.get("1.0", "end-1c").strip()
            if not raw:
                messagebox.showwarning("No encrypted data", "Open a .eadc file first, or paste EADC JSON into the ciphertext box.")
                return
            try:
                self.output_eadc = json.loads(raw)
            except Exception as exc:
                messagebox.showerror("Invalid encrypted data", "Open a .eadc file with the Open button, or paste legacy EADC JSON.\n\n" + str(exc))
                return
        try:
            plain = decrypt_eadc(self.output_eadc, load_key())
        except InvalidToken:
            messagebox.showerror("Wrong key or corrupted file", "Decryption failed. This .eadc file may need a different secret.key, or it may be damaged.")
            return
        except Exception as exc:
            messagebox.showerror("Decryption failed", str(exc))
            return
        self.input_text.delete("1.0", "end")
        self.input_text.insert("1.0", plain)
        self.set_status("Decryption completed")

    def show_help(self):
        win = tk.Toplevel(self)
        win.title("EADC Text Crypt Help")
        win.geometry("760x620")
        win.configure(bg=self.c_bg)
        frame = tk.Frame(win, bg=self.c_bg, highlightthickness=1, highlightbackground=self.c_cyan)
        frame.pack(fill="both", expand=True, padx=12, pady=12)
        tk.Label(frame, text="HELP / INSTRUCTIONS", bg=self.c_bg, fg=self.c_cyan, font=self.title_font).pack(anchor="w", padx=16, pady=(14, 8))
        txt = tk.Text(frame, wrap="word", bg=self.c_entry, fg=self.c_cyan, insertbackground=self.c_cyan,
                      selectbackground=self.c_select, relief="flat", highlightthickness=1, highlightbackground=self.c_cyan,
                      padx=14, pady=14, font=self.terminal_font)
        txt.pack(fill="both", expand=True, padx=16, pady=(0, 12))
        txt.insert("1.0", f"""EADC Text Crypt v{APP_VERSION}\n\nKEYS\n\nGenerate New Key creates secret.key in the program folder. That key encrypts and decrypts your .eadc files. Keep a backup copy. If you lose the matching key, the encrypted files cannot be decrypted.\n\nImport Key copies an existing Fernet secret.key into the program folder. Use this when decrypting files created on another computer or with a previous key.\n\nSave Key As exports a backup copy of the current key.\n\nClear Key removes secret.key from the program folder only. It does not clear backup copies.\n\nENCRYPT\n\n1. Generate or import a key.\n2. Type, paste, or load text in the PLAINTEXT box.\n3. Click ENCRYPT.\n4. Click Save to .eadc File.\n\nDECRYPT\n\n1. Import or keep the exact key used to encrypt the file.\n2. Click Open .eadc File.\n3. Click DECRYPT.\n4. Read the decrypted text in the PLAINTEXT box.\n\nCLEAR\n\nThe CLEAR button resets the text boxes and current document state, but does not delete or unload secret.key.\n\nKEYBOARD SHORTCUTS\n\nCtrl+E Encrypt\nCtrl+D Decrypt\nCtrl+O Open .eadc\nCtrl+N Clear workspace\nCtrl+K Import key\n\nSECURITY NOTE\n\nAnyone with both the .eadc file and matching secret.key can decrypt the text. Share keys carefully and separately from encrypted files.\n""")
        txt.configure(state="disabled")
        self.btn(frame, "Close", win.destroy).pack(anchor="e", padx=16, pady=(0, 14))


if __name__ == "__main__":
    app = EADCApp()
    app.mainloop()
