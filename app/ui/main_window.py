import re
import tkinter as tk
from datetime import date, datetime
from decimal import Decimal
from tkinter import messagebox

import customtkinter as ctk

from app.engine.evaluator import CalculationError, evaluate
from app.engine.formatter import format_editable, format_result
from app.storage.store import Store, StoreError
from app.theme import get_theme
from app.ui.converter_view import ConverterView
from app.ui.display import CalculatorDisplay
from app.ui.history_panel import HistoryPanel
from app.ui.keypad import Keypad


MODE_LABELS = {
    "standard": "Standar", "scientific": "Ilmiah",
    "converter": "Satuan", "date": "Tanggal",
    "programmer": "Prog.",
}
OPERATORS = "+-−×÷*/^"


class CalculatorWindow:
    def __init__(self, root, store, settings, history):
        self.root = root
        self.store = store
        self.settings = settings
        self.history = history
        self.theme_name = settings.get("theme", "dark")
        self.colors = get_theme(self.theme_name)
        self.mode = settings.get("mode", "standard")
        if self.mode not in MODE_LABELS:
            self.mode = "standard"
        self.expression = tk.StringVar()
        self.memory = Decimal(0)
        self.last_value = None
        self.just_calculated = False
        self.preview_value = None
        self._history_window = None
        self._history_popup_panel = None
        self._resize_job = None
        self._save_job = None
        self._configure_root()
        self._build_shell()
        self._render_mode()
        self._bind_keyboard()
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.bind("<Configure>", self._on_resize, add="+")

    def _configure_root(self):
        ctk.set_appearance_mode(self.theme_name)
        self.root.title("Ferdi Smart Calculator")
        self.root.geometry("{}x{}".format(
            max(320, int(self.settings.get("window", {}).get("width", 430))),
            max(480, int(self.settings.get("window", {}).get("height", 700))),
        ))
        self.root.minsize(320, 480)
        self.root.configure(fg_color=self.colors["bg"])
        self.root.attributes("-topmost", bool(self.settings.get("always_on_top", False)))
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(2, weight=1)

    def _build_shell(self):
        self.header = ctk.CTkFrame(self.root, fg_color="transparent")
        self.header.grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 4))
        self.header.grid_columnconfigure(0, weight=1)
        self.title_label = ctk.CTkLabel(
            self.header, text="Ferdi Smart Calculator", anchor="w",
            font=("Segoe UI", 17, "bold"), text_color=self.colors["text"],
        )
        self.title_label.grid(row=0, column=0, sticky="w", padx=(3, 8))
        self.history_button = self._header_button(
            self.header, "Riwayat", self.toggle_history,
        )
        self.history_button.grid(row=0, column=1, padx=3)
        self.topmost_button = self._header_button(
            self.header, "Di atas", self.toggle_topmost,
        )
        self.topmost_button.grid(row=0, column=2, padx=3)
        self.theme_button = self._header_button(
            self.header, "☼", self.toggle_theme,
        )
        self.theme_button.grid(row=0, column=3, padx=(3, 0))
        if self.settings.get("always_on_top", False):
            self.topmost_button.configure(text="Di atas ✓")

        self.mode_bar = ctk.CTkFrame(self.root, fg_color="transparent")
        self.mode_bar.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 8))
        self.mode_buttons = {}
        for column, (mode, label) in enumerate(MODE_LABELS.items()):
            self.mode_bar.grid_columnconfigure(column, weight=1, uniform="mode")
            button = ctk.CTkButton(
                self.mode_bar, text=label, height=34, corner_radius=10,
                font=("Segoe UI", 12), command=lambda selected=mode: self.set_mode(selected),
            )
            button.grid(row=0, column=column, sticky="ew", padx=2)
            self.mode_buttons[mode] = button

        self.body = ctk.CTkFrame(self.root, fg_color="transparent")
        self.body.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.body.grid_rowconfigure(0, weight=1)
        self.body.grid_columnconfigure(0, weight=1)
        self.calculator_panel = ctk.CTkFrame(self.body, fg_color="transparent")
        self.calculator_panel.grid(row=0, column=0, sticky="nsew")
        self.calculator_panel.grid_columnconfigure(0, weight=1)
        self.calculator_panel.grid_rowconfigure(0, weight=1)
        self.history_panel = HistoryPanel(
            self.body, self.colors, self._load_history_item, self.clear_history,
        )
        self.history_panel.refresh(self.history)
        self._update_mode_buttons()

    def _header_button(self, parent, text, command):
        return ctk.CTkButton(
            parent, text=text,
            width=60 if text in ("Riwayat", "Di atas") else 40,
            height=32, corner_radius=10, fg_color=self.colors["key_op"],
            hover_color=self.colors["hover"], text_color=self.colors["text"],
            font=("Segoe UI", 11), command=command,
        )

    def _render_mode(self):
        for child in self.calculator_panel.winfo_children():
            child.destroy()
        if self.mode == "converter":
            self.converter_view = ConverterView(self.calculator_panel, self.colors)
            self.converter_view.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        elif self.mode == "date":
            self._build_date_view()
        elif self.mode == "programmer":
            self._build_programmer_view()
        else:
            self._build_calculator_view(self.mode == "scientific")
        self._update_mode_buttons()
        self._update_responsive_layout()

    def _build_calculator_view(self, scientific):
        self.calculator_panel.grid_rowconfigure(0, weight=3)
        self.calculator_panel.grid_rowconfigure(1, weight=0)
        self.calculator_panel.grid_rowconfigure(2, weight=5)
        self.display = CalculatorDisplay(
            self.calculator_panel, self.colors, self.expression, self._update_preview,
        )
        self.display.grid(row=0, column=0, sticky="nsew", padx=3, pady=(2, 6))
        self.memory_bar = ctk.CTkFrame(self.calculator_panel, fg_color="transparent")
        self.memory_bar.grid(row=1, column=0, sticky="ew", padx=1, pady=(0, 4))
        self.memory_buttons = []
        for column, (label, action) in enumerate((
                ("MC", self.memory_clear), ("MR", self.memory_recall),
                ("M+", lambda: self.memory_add(1)),
                ("M−", lambda: self.memory_add(-1)))):
            button = ctk.CTkButton(
                self.memory_bar, text=label, height=34, corner_radius=9,
                fg_color=self.colors["surface"], hover_color=self.colors["hover"],
                text_color=self.colors["muted"], font=("Segoe UI", 12),
                command=action,
            )
            button.grid(row=0, column=column, sticky="ew", padx=3)
            self.memory_bar.grid_columnconfigure(column, weight=1, uniform="memory")
            self.memory_buttons.append(button)
        self.keypad = Keypad(
            self.calculator_panel, self.colors, self.press_key, scientific,
        )
        self.keypad.grid(row=2, column=0, sticky="nsew", padx=0, pady=(0, 1))
        self.display.result.bind("<Button-1>", self.copy_result)
        self._update_preview(self.expression.get())

    def _build_date_view(self):
        self.calculator_panel.grid_rowconfigure(0, weight=1)
        self.calculator_panel.grid_rowconfigure(1, weight=0)
        form = ctk.CTkFrame(
            self.calculator_panel, fg_color=self.colors["surface"], corner_radius=16,
        )
        form.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        form.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            form, text="Kalkulator Selisih Hari", text_color=self.colors["text"],
            font=("Segoe UI", 19, "bold"),
        ).pack(anchor="w", padx=18, pady=(22, 14))
        self.date_from = ctk.CTkEntry(
            form, height=46, placeholder_text="Tanggal awal (YYYY-MM-DD)",
            fg_color=self.colors["key"], text_color=self.colors["text"],
        )
        self.date_from.pack(fill="x", padx=16, pady=7)
        self.date_from.insert(0, date.today().isoformat())
        self.date_to = ctk.CTkEntry(
            form, height=46, placeholder_text="Tanggal akhir (YYYY-MM-DD)",
            fg_color=self.colors["key"], text_color=self.colors["text"],
        )
        self.date_to.pack(fill="x", padx=16, pady=7)
        self.date_to.insert(0, date.today().isoformat())
        ctk.CTkButton(
            form, text="Hitung selisih", height=44,
            fg_color=self.colors["accent"], command=self._calculate_date_difference,
        ).pack(fill="x", padx=16, pady=12)
        self.date_result = ctk.CTkLabel(
            form, text="Masukkan tanggal dengan format YYYY-MM-DD",
            text_color=self.colors["muted"], font=("Segoe UI", 15),
        )
        self.date_result.pack(pady=(8, 18))

    def _build_programmer_view(self):
        self.calculator_panel.grid_rowconfigure(0, weight=1)
        form = ctk.CTkFrame(
            self.calculator_panel, fg_color=self.colors["surface"], corner_radius=16,
        )
        form.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        ctk.CTkLabel(
            form, text="Konversi Bilangan", text_color=self.colors["text"],
            font=("Segoe UI", 19, "bold"),
        ).pack(anchor="w", padx=18, pady=(20, 10))
        self.programmer_input = ctk.CTkEntry(
            form, height=48, placeholder_text="Bilangan desimal",
            fg_color=self.colors["key"], text_color=self.colors["text"],
            font=("Segoe UI", 18),
        )
        self.programmer_input.pack(fill="x", padx=16, pady=8)
        self.programmer_input.bind("<KeyRelease>", self._update_programmer)
        self.programmer_result = ctk.CTkLabel(
            form, text="DEC  0\nBIN  0b0\nOCT  0o0\nHEX  0x0",
            justify="left", anchor="w", text_color=self.colors["text"],
            font=("Consolas", 16),
        )
        self.programmer_result.pack(fill="x", padx=20, pady=14)
        ctk.CTkLabel(
            form, text="Maksimum 64-bit unsigned (0–2⁶⁴−1)",
            text_color=self.colors["muted"], font=("Segoe UI", 12),
        ).pack(anchor="w", padx=18, pady=(0, 12))

    def _update_programmer(self, _event=None):
        text = self.programmer_input.get().strip()
        try:
            number = int(text, 0) if text.lower().startswith(("0x", "0b", "0o")) else int(text or "0")
            if number < 0 or number > 0xFFFFFFFFFFFFFFFF:
                raise ValueError()
            self.programmer_result.configure(
                text="DEC  {}\nBIN  {}\nOCT  {}\nHEX  {}".format(
                    number, bin(number), oct(number), hex(number),
                ),
                text_color=self.colors["text"],
            )
        except ValueError:
            self.programmer_result.configure(
                text="Masukkan bilangan bulat 0–2⁶⁴−1",
                text_color=self.colors["danger"],
            )

    def _calculate_date_difference(self):
        try:
            start = datetime.strptime(self.date_from.get().strip(), "%Y-%m-%d").date()
            end = datetime.strptime(self.date_to.get().strip(), "%Y-%m-%d").date()
            days = (end - start).days
            self.date_result.configure(
                text="Selisih {} hari{}".format(
                    abs(days), " (mundur)" if days < 0 else "",
                ),
                text_color=self.colors["accent"],
            )
        except ValueError:
            self.date_result.configure(
                text="Tanggal tidak valid. Gunakan YYYY-MM-DD.",
                text_color=self.colors["danger"],
            )

    def _bind_keyboard(self):
        self.root.bind_all("<KeyPress>", self._on_key, add="+")
        self.root.bind_all("<Control-c>", self.copy_result, add="+")
        self.root.bind_all("<Control-C>", self.copy_result, add="+")
        self._bind_shortcut("<Control-h>", self.toggle_history)
        self._bind_shortcut("<Control-H>", self.toggle_history)
        self._bind_shortcut("<Control-t>", self.toggle_theme)
        self._bind_shortcut("<Control-T>", self.toggle_theme)
        for number, mode in enumerate(("standard", "scientific", "converter"), 1):
            self._bind_shortcut(
                "<Control-{}>".format(number),
                lambda selected=mode: self.set_mode(selected),
            )

    def _bind_shortcut(self, sequence, command):
        def invoke(_event):
            command()
            return "break"
        self.root.bind_all(sequence, invoke, add="+")

    def _on_key(self, event):
        if event.state & 0x4:
            return None
        if self.mode not in ("standard", "scientific"):
            return None
        if event.keysym in ("Return", "KP_Enter"):
            self.calculate()
            return "break"
        if event.keysym == "Escape":
            self.press_key("AC")
            return "break"
        if event.keysym == "BackSpace":
            self.press_key("⌫")
            return "break"
        if event.char and event.char in "0123456789":
            self.press_key(event.char)
            return "break"
        key_map = {
            ".": ",", "+": "+", "-": "−", "*": "×", "/": "÷",
            "=": "=", "%": "%", "(": "(", ")": ")",
        }
        if event.char in key_map:
            self.press_key(key_map[event.char])
            return "break"
        return None

    def press_key(self, key):
        if self.mode not in ("standard", "scientific"):
            return
        current = self.expression.get()
        if key == "AC":
            self.expression.set("")
            self.just_calculated = False
            return
        if key == "⌫":
            self.expression.set(current[:-1])
            self.just_calculated = False
            return
        if key == "=":
            self.calculate()
            return
        if key == "±":
            self._toggle_sign()
            return
        if key in ("MC", "MR", "M+", "M−"):
            {"MC": self.memory_clear, "MR": self.memory_recall,
             "M+": lambda: self.memory_add(1),
             "M−": lambda: self.memory_add(-1)}[key]()
            return
        if key in ("sin", "cos", "tan", "√"):
            function = "sqrt" if key == "√" else key
            self._insert_text(function + "(")
            return
        if key in ("log", "ln"):
            self._insert_text(key + "(")
            return
        if key == "π":
            self._insert_text("π")
            return
        if key == "e":
            self._insert_text("e")
            return
        if key == "(":
            self._insert_text("(")
            return
        if key == "x²":
            self._insert_text("^2")
            return
        if key == "xʸ":
            self._insert_text("^")
            return
        if key == "n!":
            self._insert_text("!")
            return
        if key in OPERATORS:
            self._insert_operator(key)
            return
        if key == "%":
            if current and (current[-1].isdigit() or current[-1] == ")"):
                self.expression.set(current + "%")
            return
        if key in "0123456789,":
            if self.just_calculated and key in "0123456789,":
                current = ""
            self.just_calculated = False
            if key == "," and current and current[-1] == ",":
                return
            self.expression.set(current + key)
            return
        self._insert_text(key)

    def _insert_text(self, text):
        current = self.expression.get()
        if self.just_calculated:
            if text in ("π", "e", "sin(", "cos(", "tan(", "log(", "ln(", "sqrt("):
                current = ""
            else:
                current = format_editable(self.last_value) if self.last_value is not None else ""
            self.just_calculated = False
        self.expression.set(current + text)

    def _insert_operator(self, operator_text):
        current = self.expression.get().rstrip()
        if not current:
            if operator_text == "−":
                self.expression.set("-")
            return
        if self.just_calculated and self.last_value is not None:
            current = format_editable(self.last_value)
        self.just_calculated = False
        if current[-1] in OPERATORS:
            current = current[:-1]
        self.expression.set(current + operator_text)

    def _toggle_sign(self):
        current = self.expression.get()
        match = re.search(r"(\d+(?:[.,]\d*)?|[.,]\d+)$", current)
        if not match:
            self._insert_operator("−")
            return
        start, _ = match.span(1)
        if start > 0 and current[start - 1] == "-":
            current = current[:start - 1] + current[start:]
        else:
            current = current[:start] + "-" + current[start:]
        self.expression.set(current)

    def _update_preview(self, expression):
        if not hasattr(self, "display"):
            return
        try:
            if not expression.strip():
                self.display.set_preview("")
                self.display.set_result("0")
                self.preview_value = None
                return
            result = evaluate(expression)
            self.preview_value = result
            self.display.set_preview("Pratinjau  =  {}".format(format_result(result)))
            self.display.set_result(format_result(result))
        except CalculationError:
            self.preview_value = None
            self.display.set_preview("")
            self.display.set_result("")

    def calculate(self):
        expression = self.expression.get().strip()
        if not expression:
            return
        try:
            result = evaluate(expression)
        except CalculationError as error:
            self.display.set_preview("")
            self.display.set_result(str(error), is_error=True)
            self.preview_value = None
            return
        shown = format_result(result)
        self.display.set_preview(expression)
        self.display.set_result(shown)
        self.preview_value = result
        self.last_value = result
        self.just_calculated = True
        try:
            self.store.add_history(expression, shown)
            self.history = self.store.load_history()
            self.history_panel.refresh(self.history)
            if self._history_popup_panel and self._history_popup_panel.winfo_exists():
                self._history_popup_panel.refresh(self.history)
        except StoreError as error:
            messagebox.showerror("Penyimpanan gagal", str(error), parent=self.root)

    def memory_clear(self):
        self.memory = Decimal(0)

    def memory_recall(self):
        self.expression.set(format_editable(self.memory))

    def memory_add(self, sign):
        if self.preview_value is not None:
            self.memory += self.preview_value * sign

    def copy_result(self, _event=None):
        if self.mode not in ("standard", "scientific"):
            return None
        if self.preview_value is not None:
            self.root.clipboard_clear()
            self.root.clipboard_append(format_result(self.preview_value))
            self.root.update_idletasks()
        return "break"

    def set_mode(self, mode):
        if mode not in MODE_LABELS:
            return
        self.mode = mode
        self.settings["mode"] = mode
        self._persist_settings()
        self._render_mode()

    def toggle_theme(self):
        self.theme_name = "light" if self.theme_name == "dark" else "dark"
        self.settings["theme"] = self.theme_name
        self._persist_settings()
        ctk.set_appearance_mode(self.theme_name)
        self.colors = get_theme(self.theme_name)
        self.root.configure(fg_color=self.colors["bg"])
        self.title_label.configure(text_color=self.colors["text"])
        self._configure_header_theme()
        self.history_panel.set_theme(self.colors)
        self.history_panel.refresh(self.history)
        if hasattr(self, "display"):
            self.display.set_theme(self.colors)
        if hasattr(self, "keypad"):
            self.keypad.set_theme(self.colors)
        for button in self.memory_buttons if hasattr(self, "memory_buttons") else ():
            button.configure(
                fg_color=self.colors["surface"], hover_color=self.colors["hover"],
                text_color=self.colors["muted"],
            )
        self._render_mode()
        self._update_mode_buttons()
        if self._history_popup_panel and self._history_popup_panel.winfo_exists():
            self._history_popup_panel.set_theme(self.colors)
            self._history_popup_panel.refresh(self.history)

    def _configure_header_theme(self):
        for button in (self.history_button, self.topmost_button, self.theme_button):
            button.configure(
                fg_color=self.colors["key_op"], hover_color=self.colors["hover"],
                text_color=self.colors["text"],
            )

    def toggle_topmost(self):
        enabled = not bool(self.settings.get("always_on_top", False))
        self.settings["always_on_top"] = enabled
        self.root.attributes("-topmost", enabled)
        self.topmost_button.configure(text="Di atas ✓" if enabled else "Di atas")
        self._persist_settings()

    def toggle_history(self):
        width = self.root.winfo_width()
        if width >= 720:
            if self.history_panel.winfo_manager():
                self.history_panel.grid_remove()
            else:
                self.history_panel.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
            return
        if self._history_window and self._history_window.winfo_exists():
            self._history_window.destroy()
            self._history_window = None
            self._history_popup_panel = None
            return
        self._history_window = ctk.CTkToplevel(self.root)
        self._history_window.title("Riwayat - Ferdi Smart Calculator")
        self._history_window.geometry("340x540")
        self._history_window.configure(fg_color=self.colors["bg"])
        popup_panel = HistoryPanel(
            self._history_window, self.colors, self._load_history_item,
            self.clear_history,
        )
        popup_panel.pack(fill="both", expand=True, padx=12, pady=12)
        popup_panel.refresh(self.history)
        self._history_popup_panel = popup_panel

    def _load_history_item(self, item):
        self.set_mode("standard")
        self.expression.set(item.get("expr", ""))
        if self._history_window and self._history_window.winfo_exists():
            self._history_window.destroy()
            self._history_window = None

    def clear_history(self):
        if not self.history:
            return
        if not messagebox.askyesno(
                "Hapus riwayat", "Hapus seluruh riwayat perhitungan?",
                parent=self.root):
            return
        try:
            self.store.clear_history()
            self.history = []
            self.history_panel.refresh([])
            if self._history_popup_panel and self._history_popup_panel.winfo_exists():
                self._history_popup_panel.refresh([])
        except StoreError as error:
            messagebox.showerror("Penyimpanan gagal", str(error), parent=self.root)

    def _update_mode_buttons(self):
        for mode, button in self.mode_buttons.items():
            selected = mode == self.mode
            button.configure(
                fg_color=self.colors["accent"] if selected else self.colors["key_op"],
                hover_color=self.colors["hover"],
                text_color="#FFFFFF" if selected else self.colors["text"],
            )
        self._configure_header_theme()

    def _on_resize(self, event):
        if event.widget != self.root:
            return
        if self._resize_job:
            self.root.after_cancel(self._resize_job)
        self._resize_job = self.root.after(100, self._update_responsive_layout)
        if self._save_job:
            self.root.after_cancel(self._save_job)
        self._save_job = self.root.after(500, self._save_window_size)

    def _update_responsive_layout(self):
        if not hasattr(self, "history_panel"):
            return
        if self.mode == "converter":
            self.history_panel.grid_remove()
            self.body.grid_columnconfigure(0, weight=1)
            self.body.grid_columnconfigure(1, weight=0)
            return
        if self.root.winfo_width() >= 720:
            self.body.grid_columnconfigure(0, weight=3, uniform="body")
            self.body.grid_columnconfigure(1, weight=2, uniform="body")
            if not self.history_panel.winfo_manager():
                self.history_panel.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        else:
            self.body.grid_columnconfigure(0, weight=1, uniform="body")
            self.body.grid_columnconfigure(1, weight=0, uniform="body")
            self.history_panel.grid_remove()

    def _save_window_size(self):
        if not self.root.winfo_exists():
            return
        geometry = self.root.geometry().split("+", 1)[0]
        try:
            width, height = (int(part) for part in geometry.split("x", 1))
            self.settings["window"] = {"width": width, "height": height}
            self.store.save_settings(self.settings)
        except (ValueError, StoreError) as error:
            messagebox.showerror("Pengaturan gagal", str(error), parent=self.root)

    def _persist_settings(self):
        try:
            self.store.save_settings(self.settings)
        except StoreError as error:
            messagebox.showerror("Pengaturan gagal", str(error), parent=self.root)

    def close(self):
        try:
            self._save_window_size()
            self.store.save_settings(self.settings)
        except StoreError as error:
            if not messagebox.askyesno(
                    "Pengaturan gagal",
                    "{}\n\nTutup aplikasi tanpa menyimpan?".format(error),
                    parent=self.root):
                return
        self.root.destroy()
