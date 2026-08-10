import customtkinter as ctk

from PIL import Image

from ..image.settings import IMAGE_DATA
from app.utils import resource_path

class MenuView(ctk.CTkFrame):
    def __init__(self, master, on_pick_filename, on_height_change, on_width_change, on_generate, on_save):
        super().__init__(master)

        self.on_pick_filename = on_pick_filename
        self.on_height_change = on_height_change
        self.on_width_change = on_width_change
        self.on_generate = on_generate
        self.on_save = on_save
        
        self._build_ui()       
        
    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        
        title = ctk.CTkLabel(
            self,
            text="LegoHue",
            font=ctk.CTkFont(size=28, weight="bold"),
        )
        title.grid(row=0, column=0, padx=20, pady=(24,8), sticky='n', columnspan=2)
        
        self.filepath_label = ctk.CTkLabel(
            self,
            text = "Nie wybrano pliku.",
            font = ctk.CTkFont(size=14),
        )
        self.filepath_label.grid(row=1, column=0, padx=(6, 0), pady=(0, 30), sticky='n')
        
        pick_file_button = ctk.CTkButton(
            self,
            width = 100,
            height = 25,
            corner_radius=2,
            command=self.on_pick_filename,
            text="Wybierz plik..."
        )
        pick_file_button.grid(row=1, column=1, padx=(0, 20), pady=(0, 20), sticky='nw')
        
        
        parameters_frame = ctk.CTkFrame(self, fg_color="transparent")
        parameters_frame.grid(row=2, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="n")
        parameters_frame.grid_columnconfigure(0, weight=1)
        
        sigma_label = ctk.CTkLabel(
            parameters_frame,
            text = "Sigma",
            font = ctk.CTkFont(size=14),
        )
        sigma_label.grid(row=0, column=0, pady=6, padx=(0, 3))
        
        self.sigma_entry = ctk.CTkEntry(
            parameters_frame,
        )
        self.sigma_entry.grid(row=0, column=1, pady=6, padx=(0, 3))
        
        
        amount_label = ctk.CTkLabel(
            parameters_frame,
            text = "Amount",
            font = ctk.CTkFont(size=14),
        )
        amount_label.grid(row=1, column=0, pady=6, padx=(0, 3))
        
        self.amount_entry = ctk.CTkEntry(
            parameters_frame,
        )
        self.amount_entry.grid(row=1, column=1, pady=(6,20), padx=(0, 3))
        
        
        width_label = ctk.CTkLabel(
            parameters_frame,
            text = "Szerokość",
            font = ctk.CTkFont(size=14),
        )
        width_label.grid(row=2, column=0, pady=6, padx=(0, 3))
        
        self.width_entry = ctk.CTkEntry(parameters_frame)
        self.width_entry.insert(0, "1")
        self.width_entry.bind("<FocusOut>", self._width_changed)
        self.width_entry.grid(row=2, column=1, pady=6, padx=(0, 3))
        
        
        height_label = ctk.CTkLabel(
            parameters_frame,
            text = "Wysokość",
            font = ctk.CTkFont(size=14),
        )
        height_label.grid(row=3, column=0, pady=6, padx=(0, 3))
        
        self.height_entry = ctk.CTkEntry(parameters_frame)
        self.height_entry.insert(0, "1")
        self.height_entry.bind("<FocusOut>", self._height_changed)
        self.height_entry.grid(row=3, column=1, pady=(6,20), padx=(0, 3))
        
        dummy_label = ctk.CTkLabel(
            parameters_frame,
            text = "X-Factor",
            font = ctk.CTkFont(size=14),
        )
        dummy_label.grid(row=4, column=0, pady=6, padx=(0, 3))
        
        dummy_entry = ctk.CTkEntry(
            parameters_frame,
        )
        dummy_entry.grid(row=4, column=1, pady=(20, 6), padx=(0, 3))
        
        generate_button = ctk.CTkButton(
            parameters_frame,
            text="Generuj obraz",
            command=lambda: self.on_generate(
                IMAGE_DATA["pil_image"],
                float(self.sigma_entry.get()),
                float(self.amount_entry.get()),
                (
                    int(self.width_entry.get()),
                    int(self.height_entry.get())
                )
            ),
        )
        generate_button.grid(row=5, column=0, columnspan=2, pady=(32, 16), padx=6)
        
        placeholder_image = Image.open(resource_path("assets/john_placeholder.jpg"))
        size = placeholder_image.size
        preview_image = ctk.CTkImage(
            light_image=placeholder_image,
            dark_image=placeholder_image,
            size=size,
        )
        self.image_label = ctk.CTkLabel(
            self,
            text="",
            image=preview_image,
        )
        self.image_label.grid(row=2, column=1, columnspan=6, rowspan=6, padx=10, pady=10)
        
        self.save_button = ctk.CTkButton(
            self,
            text="Zapisz zdjęcie",
            command=self.on_save,
        )
        self.save_button.grid(row=3, column=0, columnspan=2)
        
        
        
    def _width_changed(self, event):
        try:
            self.on_width_change(int(self.width_entry.get()))
        except ValueError:
            pass

    def _height_changed(self, event):
        try:
            self.on_height_change(int(self.height_entry.get()))
        except ValueError:
            pass
        
    def set_width_entry(self, width: int):
        self.width_entry.delete(0, ctk.END)
        self.width_entry.insert(0, width)
        
    def set_height_entry(self, height: int):
        self.height_entry.delete(0, ctk.END)
        self.height_entry.insert(0, height)
        
    def set_filename_label(self, text: str):
        self.filepath_label.configure(text=text)
        
    def set_image_label(self, image: Image.Image):
        size = image.size

        self.preview_image = ctk.CTkImage(
            light_image=image,
            dark_image=image,
            size=size
        )

        self.image_label.configure(image=self.preview_image)
        
        
# TODO  pyisntaller nie widzi innych packages, poszukaj jak to robić