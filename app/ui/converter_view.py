import customtkinter as ctk

from app.engine.converter import UNITS, convert
from app.engine.formatter import format_result


class ConverterView(ctk.CTkFrame):
    def __init__(self, master, colors):
        super().__init__(master, fg_color="transparent")
        self.colors = colors
        self.category = ctk.StringVar(value="Panjang")
        self.source = ctk.StringVar(value="Meter")
        self.target = ctk.StringVar(value="Kilometer")
        self.amount = ctk.StringVar(value="1")
        self._build()

    def _build(self):
        color = self.colors
        ctk.CTkLabel(
            self, text="Kategori", text_color=color["muted"],
            font=("Segoe UI", 13),
        ).pack(anchor="w", padx=4, pady=(4, 4))
        self.category_menu = ctk.CTkOptionMenu(
            self, variable=self.category, values=list(UNITS),
            command=self._category_changed, fg_color=color["key_op"],
            button_color=color["accent"], text_color=color["text"],
        )
        self.category_menu.pack(fill="x", padx=4, pady=(0, 16))
        self.input_entry = ctk.CTkEntry(
            self, textvariable=self.amount, height=52, justify="right",
            font=("Segoe UI", 20), fg_color=color["surface"],
            text_color=color["text"],
        )
        self.input_entry.pack(fill="x", padx=4, pady=4)
        self.source_menu = ctk.CTkOptionMenu(
            self, variable=self.source, values=list(UNITS["Panjang"]),
            fg_color=color["key_op"], button_color=color["accent"],
            text_color=color["text"],
        )
        self.source_menu.pack(fill="x", padx=4, pady=4)
        swap = ctk.CTkButton(
            self, text="⇅  Tukar satuan", height=42, fg_color="transparent",
            hover_color=color["hover"], text_color=color["accent"],
            command=self._swap,
        )
        swap.pack(pady=6)
        self.output_entry = ctk.CTkEntry(
            self, height=52, justify="right", font=("Segoe UI", 20),
            fg_color=color["surface"], text_color=color["text"],
        )
        self.output_entry.pack(fill="x", padx=4, pady=4)
        self.target_menu = ctk.CTkOptionMenu(
            self, variable=self.target, values=list(UNITS["Panjang"]),
            fg_color=color["key_op"], button_color=color["accent"],
            text_color=color["text"],
        )
        self.target_menu.pack(fill="x", padx=4, pady=4)
        self.amount.trace_add("write", self._update_result)
        self.source.trace_add("write", self._update_result)
        self.target.trace_add("write", self._update_result)
        self.category.trace_add("write", self._update_result)
        self._update_result()

    def _category_changed(self, category):
        units = list(UNITS[category])
        self.source.set(units[0])
        self.target.set(units[1] if len(units) > 1 else units[0])
        self.source_menu.configure(values=units)
        self.target_menu.configure(values=units)
        self._update_result()

    def _swap(self):
        source, target = self.source.get(), self.target.get()
        self.source.set(target)
        self.target.set(source)

    def _update_result(self, *_):
        try:
            value = self.amount.get().strip().replace(",", ".")
            result = convert(
                value, self.category.get(), self.source.get(), self.target.get(),
            )
            text = format_result(result)
            self.output_entry.configure(state="normal")
            self.output_entry.delete(0, "end")
            self.output_entry.insert(0, text)
        except (ValueError, ArithmeticError):
            self.output_entry.configure(state="normal")
            self.output_entry.delete(0, "end")

    def set_theme(self, colors):
        self.colors = colors
        self.configure(fg_color="transparent")
        for widget in (
                self.category_menu, self.source_menu, self.target_menu):
            widget.configure(
                fg_color=colors["key_op"], button_color=colors["accent"],
                text_color=colors["text"],
            )
        for widget in (self.input_entry, self.output_entry):
            widget.configure(fg_color=colors["surface"], text_color=colors["text"])
