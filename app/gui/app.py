import customtkinter as ctk
import tkinter as tk
from PIL import Image
import numpy as np

from ..image.settings import IMAGE_DATA
from ..image.Legoify import Legoify
from app.utils import resource_path

from ..gui.menu_view import MenuView
from ..gui.results_view import ResultsView
from .colors_list import ColorsList

class App(ctk.CTk):
    
    def __init__(self, fg_color = None, **kwargs):
        super().__init__(fg_color, **kwargs)
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        self.title("BrickHue")
        self.geometry("1500x900")
        
        self._legoify = Legoify(resource_path("assets/lego_colors.csv"))
        
        self.current_view = None
        self.current_sidelist = None
        self.current_filename = ""
        
        self.global_picked_color_id = ctk.IntVar(value=-1)
        
        self._build_ui()
        self.show_menu()
        
    
    def _build_ui(self):
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=1)
        
        self.rowconfigure(0, weight=4)
        self.rowconfigure(1, weight=1)
        
        self.container = ctk.CTkFrame(self)
        self.container.grid(row=0, column=0, sticky="nsew")
        
        self.log = ctk.CTkTextbox(self)
        self.log.grid(row=1, column=0, sticky='nsew')
        
        self.side_list = ctk.CTkFrame(self, bg_color="#323232")
        self.side_list.grid(row=0, rowspan=2, column=1, sticky="nsew")
        
    
    def _log(self, msg: str):
        self.log.insert("end", msg + "\n")
        self.log.see("end")
    
        
    def _set_view(self, view: ctk.CTkFrame):
        if self.current_view is not None:
            self.current_view.destroy()
            
        self.current_view = view
        self.current_view.pack(fill="both", expand=True)
        
    def _set_sidelist(self, sidelist: ctk.CTkFrame|ctk.CTkScrollableFrame):
        if self.current_sidelist is not None:
            self.current_sidelist.destroy()
            
        self.current_sidelist = sidelist
        self.side_list.grid(row=0, rowspan=2, column=1, sticky="nsew")
    
    
    def _load_image(self):
        if IMAGE_DATA["filepath"] is None:
            self._log("Nie wybrano pliku lub ścieżka jest nieprawidłowa.")
            return
        
        IMAGE_DATA["pil_image"] = Image.open(IMAGE_DATA["filepath"])
        
        w, h = IMAGE_DATA["pil_image"].size
        IMAGE_DATA["width"] = w
        IMAGE_DATA["height"] = h
        
        self._log(f"Załadowano zdjęcie z pliku {IMAGE_DATA["filepath"]}\nWymiary: {IMAGE_DATA["width"]}x{IMAGE_DATA["height"]}")
        
        
    def show_menu(self):
        view = MenuView(master=self.container, on_pick_input_file=self._pick_filename, on_generate=self._on_generate)

        if self.current_view is not None:
            self.current_view.destroy()

        # nie wiem dlaczego, ale nie mogę zrestartować sidelisty w poniższy sposób hmmmmmmmmmmm
        self._set_sidelist(ctk.CTkFrame(self, bg_color="#323232"))

        if IMAGE_DATA["pil_image"] is not None:
            IMAGE_DATA["filepath"] = None
            IMAGE_DATA["width"] = 1
            IMAGE_DATA["height"] = 1
            IMAGE_DATA["pil_image"] = None
        
        self._set_view(view)
        
    
    def _pick_filename(self):
            """
            Zapytaj użytkownika o ścieżkę do pliku i ustaw go w widoku oraz jako aktualny plik.
            """
            picked_filename = ctk.filedialog.askopenfilename()
            
            if ".jpg" not in picked_filename and ".png" not in picked_filename and ".jpeg" not in picked_filename:
                self._log("ERROR: Obsługiwane formaty pliku to: .jpg, .png, .jpeg")
                return
            
            self._log(f"Wybrany plik: {picked_filename}")
            
            self.current_view.set_filename_label(picked_filename)
            IMAGE_DATA["filepath"] = picked_filename
            self._load_image()
            
            
    def _on_generate(self, sigma, amount, target_w: int, target_h: int):
        mapped_ids, _, mapped_rgb = self._legoify.generate_lego_image(IMAGE_DATA["pil_image"], sigma=sigma, amount=amount, target_size=(target_w, target_h))
        generated_image_rgb = Image.fromarray((mapped_rgb * 255).astype(np.uint8))
        
        results_view = ResultsView(master=self.container, start_image=generated_image_rgb, mapped_ids=mapped_ids, global_color_picked_id=self.global_picked_color_id, on_back=self.show_menu, logger_function=self._log)
        
        unique_ids, counts = np.unique(mapped_ids, return_counts=True)
        color_records = [self._legoify.decode_color_from_id(id) for id in unique_ids]
        for i in range(len(color_records)):
            color_records[i]["count"] = counts[i]

        colors_sidelist = ColorsList(self.side_list, color_records, self.global_picked_color_id)
        
        self._set_sidelist(colors_sidelist)
        self._set_view(results_view)