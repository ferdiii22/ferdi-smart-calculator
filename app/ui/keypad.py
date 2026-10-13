import customtkinter as ctk


class Keypad(ctk.CTkFrame):
    STANDARD_ROWS = (
        ("AC", "⌫", "%", "÷"),
        ("7", "8", "9", "×"),
        ("4", "5", "6", "−"),
        ("1", "2", "3", "+"),
        ("±", "0", ",", "="),
    )
    SCIENTIFIC_ROWS = (
        ("sin", "cos", "tan", "π"),
        ("log", "ln", "e", "√"),
        ("x²", "xʸ", "n!", "("),
    )

    def __init__(self, master, colors, on_press, scientific=False):
        super().__init__(master, fg_color="transparent")
        self.colors = colors
        self.on_press = on_press
        self.buttons = []
        self.set_rows(scientific)

    def set_rows(self, scientific):
        for button in self.buttons:
            button.destroy()
        self.buttons = []
        rows = self.SCIENTIFIC_ROWS + self.STANDARD_ROWS if scientific else self.STANDARD_ROWS
        for row, labels in enumerate(rows):
            self.grid_rowconfigure(row, weight=1, minsize=48)
            for column, label in enumerate(labels):
                self.grid_columnconfigure(column, weight=1, uniform="keypad")
                button = ctk.CTkButton(
                    self, text=label, height=48, corner_radius=14,
                    fg_color=self._button_color(label),
                    hover_color=self.colors["hover"],
                    text_color=self.colors["text"],
                    font=("Segoe UI", 17 if len(label) > 3 else 14),
                    command=lambda value=label: self.on_press(value),
                )
                button.grid(row=row, column=column, sticky="nsew", padx=4, pady=4)
                self.buttons.append(button)

    def _button_color(self, label):
        if label == "=":
            return self.colors["accent"]
        if label in ("+", "−", "×", "÷", "%", "AC", "⌫"):
            return self.colors["key_op"]
        return self.colors["key"]

    def set_theme(self, colors):
        self.colors = colors
        for button in self.buttons:
            label = button.cget("text")
            button.configure(
                fg_color=self._button_color(label),
                hover_color=colors["hover"],
                text_color=colors["text"],
            )
