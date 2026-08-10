import customtkinter as ctk
from PIL import Image
import math

from ..image.settings import IMAGE_DATA
from app.utils import resource_path
from ..utils import find_height_from_width, find_width_from_height


class MenuView(ctk.CTkFrame):
    
    def __init__(self, master, on_pick_input_file, on_generate):
        super().__init__(master)
        
        self.on_pick_input_file = on_pick_input_file
        self.on_generate = on_generate
        
        self._build_ui()
        
    
    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        
        title_label = ctk.CTkLabel(
            self,
            text="BrickHue",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=10)
        
        self.filepath_label = ctk.CTkLabel(
            self,
            text="Nie wybrano zdjęcia.",
            font=ctk.CTkFont(size=14)
        )
        self.filepath_label.grid(row=1, column=0, pady=(0, 8))
        
        self.pick_input_file_button = ctk.CTkButton(
            self,
            width=100,
            height=25,
            corner_radius=2,
            command=self.on_pick_input_file,
            text="Wybierz plik..."
        )
        self.pick_input_file_button.grid(row=1, column=1, padx=6, pady=(0, 8))
        
        
        # kontener opcji do samego obrazu
        parameters_frame = ctk.CTkFrame(self, fg_color="transparent")
        parameters_frame.grid(row=2, column=0, columnspan=2)
        parameters_frame.grid_columnconfigure(0, weight=1)
    
    
        width_label = ctk.CTkLabel(
            parameters_frame,
            text="Szerokość",
            font=ctk.CTkFont(size=14),
        )
        width_label.grid(row=0, column=0, padx=4)
        
        self.width_entry = ctk.CTkEntry(parameters_frame)
        self.width_entry.bind("<FocusOut>", self._on_width_change)
        self.width_entry.grid(row=0, column=1)
        
        
        height_label = ctk.CTkLabel(
            parameters_frame,
            text="Wysokość",
            font=ctk.CTkFont(size=14),
        )
        height_label.grid(row=1, column=0, padx=4, pady=(0, 8))
        
        self.height_entry = ctk.CTkEntry(parameters_frame)
        self.height_entry.bind("<FocusOut>", self._on_height_change)
        self.height_entry.grid(row=1, column=1, pady=(0, 8))
        
        
        amount_label = ctk.CTkLabel(
            parameters_frame,
            text="Rescalling amount",
            font=ctk.CTkFont(size=14)
        )
        amount_label.grid(row=2, column=0, padx=4)
        
        self.amount_entry = ctk.CTkEntry(parameters_frame)
        self.amount_entry.grid(row=2, column=1)
        
        sigma_label = ctk.CTkLabel(
            parameters_frame,
            text="Rescalling Sigma",
            font=ctk.CTkFont(size=14)
        )
        sigma_label.grid(row=3, column=0, padx=4, pady=(0, 8))
        
        self.sigma_entry = ctk.CTkEntry(parameters_frame)
        self.sigma_entry.grid(row=3, column=1, pady=(0, 8))
        
        
        self.generate_button = ctk.CTkButton(
            self,
            text="Generuj obraz",
            corner_radius=2,
            command=lambda: self.on_generate(
                    float(self.sigma_entry.get()),
                    float(self.amount_entry.get()),
                    int(self.width_entry.get()),
                    int(self.height_entry.get())
                ),
            width=100,
            height=25
        )
        self.generate_button.grid(row=3, column=0, columnspan=2)
        
        
        
    def set_filename_label(self, text: str):
        self.filepath_label.configure(text=text)
        

    def _on_width_change(self, event):
        if len(self.width_entry.get()) == 0 or int(self.width_entry.get()) <= 0:
            return
        
        new_width = int(self.width_entry.get())
        new_height = math.floor(IMAGE_DATA["height"] * (new_width / IMAGE_DATA["width"]))
        
        self.height_entry.delete(0, ctk.END)
        self.height_entry.insert(0, str(new_height))
    
    
    def _on_height_change(self, event):
        if len(self.height_entry.get()) == 0 or int(self.height_entry.get()) <= 0:
            return
        
        new_height = int(self.height_entry.get())
        new_width = math.floor(IMAGE_DATA["width"] * (new_height / IMAGE_DATA["height"]))
        
        self.width_entry.delete(0, ctk.END)
        self.width_entry.insert(0, str(new_width))