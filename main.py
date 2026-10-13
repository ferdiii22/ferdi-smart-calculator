"""Application entry point for Ferdi Smart Calculator."""

import sys
import ctypes
from tkinter import messagebox

import customtkinter as ctk

from app.storage.store import Store, StoreError
from app.ui.main_window import CalculatorWindow


def enable_dpi_awareness():
    if sys.platform != "win32":
        return
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except AttributeError:
        ctypes.windll.user32.SetProcessDPIAware()


def main():
    enable_dpi_awareness()
    root = ctk.CTk()
    try:
        store = Store()
        settings = store.load_settings()
        history = store.load_history()
    except StoreError as error:
        messagebox.showerror("Data aplikasi bermasalah", str(error), parent=root)
        root.destroy()
        return
    CalculatorWindow(root, store, settings, history)
    root.mainloop()


if __name__ == "__main__":
    main()
