import customtkinter as ctk


class HistoryPanel(ctk.CTkFrame):
    def __init__(self, master, colors, on_select, on_clear):
        super().__init__(master, fg_color=colors["surface"], corner_radius=16)
        self.colors = colors
        self.on_select = on_select
        self.on_clear = on_clear
        self.heading = ctk.CTkLabel(
            self, text="Riwayat", font=("Segoe UI", 17, "bold"),
            text_color=colors["text"], anchor="w",
        )
        self.heading.pack(fill="x", padx=14, pady=(14, 6))
        self.items_frame = ctk.CTkScrollableFrame(
            self, fg_color="transparent", scrollbar_button_color=colors["key_op"],
        )
        self.items_frame.pack(fill="both", expand=True, padx=8, pady=4)
        self.clear_button = ctk.CTkButton(
            self, text="Hapus riwayat", height=38,
            fg_color=colors["key_op"], hover_color=colors["hover"],
            text_color=colors["text"], command=self.on_clear,
        )
        self.clear_button.pack(fill="x", padx=12, pady=(4, 12))
        self.refresh([])

    def refresh(self, history):
        for child in self.items_frame.winfo_children():
            child.destroy()
        for item in reversed(history):
            button = ctk.CTkButton(
                self.items_frame,
                text="{}\n= {}".format(item.get("expr", ""), item.get("result", "")),
                anchor="e", height=58, fg_color=self.colors["key"],
                hover_color=self.colors["hover"], text_color=self.colors["text"],
                font=("Segoe UI", 13),
                command=lambda entry=item: self.on_select(entry),
            )
            button.pack(fill="x", padx=2, pady=3)
        if not history:
            ctk.CTkLabel(
                self.items_frame, text="Belum ada perhitungan",
                text_color=self.colors["muted"], font=("Segoe UI", 13),
            ).pack(pady=12)

    def set_theme(self, colors):
        self.colors = colors
        self.configure(fg_color=colors["surface"])
        self.heading.configure(text_color=colors["text"])
        self.clear_button.configure(
            fg_color=colors["key_op"], hover_color=colors["hover"],
            text_color=colors["text"],
        )
        self.items_frame.configure(scrollbar_button_color=colors["key_op"])
