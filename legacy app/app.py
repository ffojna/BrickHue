import customtkinter as ctk
import numpy as np
from PIL import Image

from .menu_view import MenuView
from ..image.settings import IMAGE_DATA
from ..image.Legoify import Legoify
from app.utils import resource_path

class App(ctk.CTk):
    
    def __init__(self):
        super().__init__()
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        self.title("LegoHue")
        self.geometry("1000x850")
        
        self.legoify = Legoify(resource_path("assets/lego_colors.csv"))
        
        self.current_view = None
        self.current_filename = ""
        
        self._build_ui()
        self.show_menu()
        
    def _build_ui(self):
        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True)
        
        self.log = ctk.CTkTextbox(self, height=220)
        self.log.pack(fill='x', expand=True, padx=16, pady=(16, 16))
        
    def _log(self, msg: str):
        self.log.insert("end", msg + "\n")
        self.log.see("end")
        
    def _set_view(self, view):
        if self.current_view is not None:
            self.current_view.destroy()
            
        self.current_view = view
        self.current_view.pack(fill="both", expand=True)
        
    def _load_image(self):
        if IMAGE_DATA["filepath"] is None:
            self._log("Nie wybrano pliku lub ścieżka jest nieprawidłowa.")
            return
        
        IMAGE_DATA["pil_image"] = Image.open(IMAGE_DATA["filepath"])
        
        w, h = IMAGE_DATA["pil_image"].size
        IMAGE_DATA["width"] = w
        IMAGE_DATA["height"] = h
        
        self.current_view.set_image_label(IMAGE_DATA["pil_image"])
        
        self._log(f"Załadowano zdjęcie z pliku {IMAGE_DATA["filepath"]}\nWymiary: {IMAGE_DATA["width"]}x{IMAGE_DATA["height"]}")
        
    def _reload_image(self, image):
        if isinstance(image, np.ndarray):
            image = Image.fromarray((image * 255.0).astype(np.uint8))
            
        w,h = image.size
            
        IMAGE_DATA["pil_image"] = image
        IMAGE_DATA["width"] = w
        IMAGE_DATA["height"] = h
            
        
        
        
    def show_menu(self):
        view = MenuView(master=self.container, 
                        on_pick_filename=self.pick_filename, 
                        on_height_change=self.find_width_from_height, 
                        on_width_change=self.find_height_from_width, 
                        on_generate=self.generate_lego_image, 
                        on_save=self.save_image)
        
        self._set_view(view)
        
    def pick_filename(self):
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
        
    def find_width_from_height(self, new_height: int):
        if not isinstance(self.current_view, MenuView):
            self._log("Menu nie załadowane.")
        
        if new_height == 0:
            self._log("Dzielenie przez 0!")
            return
        
        new_w = int(IMAGE_DATA["width"] * (new_height / IMAGE_DATA["height"]))
        
        self.current_view.set_width_entry(new_w)
        
    def find_height_from_width(self, new_width: int):
        if not isinstance(self.current_view, MenuView):
            self._log("Menu nie załadowane.")
        
        if new_width == 0:
            self._log("Dzielenie przez 0!")
            return
        
        new_h = int(IMAGE_DATA["height"] * (new_width / IMAGE_DATA["width"]))
        
        self.current_view.set_height_entry(new_h)
        

    def generate_lego_image(self, image: Image.Image, sigma, amount, size):
        if not isinstance(image, Image.Image) or IMAGE_DATA["pil_image"] is None:
            self._log("Nie załadowane zdjęcia.")
            return
        
        self._log("Generowanie zdjęcia...")
        
        mapped_idx, mapped_hex, mapped_rgb = self.legoify.generate_lego_image(IMAGE_DATA["pil_image"], sigma, amount, size)
        
        self._log("Ładuję wygenerowane zdjęcie zdjęcie...")
        
        mapped_rgb_pil = Image.fromarray((mapped_rgb * 255.0).astype(np.uint8))
        
        self._reload_image(mapped_rgb_pil)
        
        self.current_view.set_image_label(mapped_rgb_pil)
        
    
    def save_image(self):
        if IMAGE_DATA["pil_image"] is None:
            self._log("Nie wygenerowano jeszcze zdjęcia.")
        
        savepath = ctk.filedialog.asksaveasfilename()
        
        if "." not in savepath:
            savepath = savepath + ".jpg"
            
        self._log(f"Zapisuję zdjęcie w: {savepath}")
        
        IMAGE_DATA["pil_image"].save(savepath)
        
