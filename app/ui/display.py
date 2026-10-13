import customtkinter as ctk


class CalculatorDisplay(ctk.CTkFrame):
    def __init__(self, master, colors, variable, on_change):
        super().__init__(master, fg_color=colors["surface"], corner_radius=16)
        self.colors = colors
        self.variable = variable
        self.on_change = on_change
        self.entry = ctk.CTkEntry(
            self, textvariable=variable, height=48, border_width=0,
            fg_color="transparent", text_color=colors["muted"],
            font=("Segoe UI", 18), justify="right",
        )
        self.entry.pack(fill="x", padx=16, pady=(16, 4))
        self.preview = ctk.CTkLabel(
            self, text="", anchor="e", text_color=colors["muted"],
            font=("Segoe UI", 14),
        )
        self.preview.pack(fill="x", padx=18, pady=(0, 2))
        self.result = ctk.CTkLabel(
            self, text="0", anchor="e", text_color=colors["text"],
            font=("Segoe UI", 40, "bold"),
        )
        self.result.pack(fill="x", padx=16, pady=(0, 12))
        self._trace = variable.trace_add("write", self._on_variable)
        self.result.bind("<Configure>", self._fit_result)

    def destroy(self):
        self.variable.trace_remove("write", self._trace)
        super().destroy()

    def _on_variable(self, *_):
        self.on_change(self.variable.get())

    def set_preview(self, text):
        self.preview.configure(text=text)

    def set_result(self, text, is_error=False):
        self.result.configure(
            text=text,
            text_color=self.colors["danger"] if is_error else self.colors["text"],
        )
        self._fit_result()

    def _fit_result(self, _event=None):
        text = self.result.cget("text")
        available = max(1, self.result.winfo_width() - 8)
        size = 40
        while size > 16:
            measured = len(text) * size * 0.58
            if measured <= available:
                break
            size -= 1
        self.result.configure(font=("Segoe UI", size, "bold"))

    def set_theme(self, colors):
        self.colors = colors
        self.configure(fg_color=colors["surface"])
        self.entry.configure(text_color=colors["muted"])
        self.preview.configure(text_color=colors["muted"])
        self.result.configure(text_color=colors["text"])
