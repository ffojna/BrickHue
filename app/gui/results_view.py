import customtkinter as ctk
from PIL import Image
import numpy as np

from ..image.image_viewer import CTkImageViewer
from ..utils import resource_path


class ResultsView(ctk.CTkFrame):
    
    def __init__(self, master, start_image: Image, mapped_ids, global_color_picked_id, on_back, logger_function):
        
        super().__init__(master)
        
        self._log = logger_function
        
        self._viewer = CTkImageViewer(self, global_color_picked_id, mapped_ids)
        self._viewer.open(start_image)

        self._on_back = on_back
        
        self._build_ui()
        
        
    def _build_ui(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=15)
        
        self._viewer.grid(row=0, column=1, sticky="nsew")

        self._button_pane = ctk.CTkFrame(self, bg_color="transparent")
        self._button_pane.grid(row=0, column=0, sticky="ns")


        recenter_image = Image.open(resource_path("assets/icons/recenter.png"))
        recenter_ctkimage = ctk.CTkImage(light_image=recenter_image, dark_image=recenter_image, size=(40, 40))
        recenter_button = ctk.CTkButton(self._button_pane, 
                                         width=50, height=50, 
                                         image=recenter_ctkimage,
                                         text=None,
                                         command=self._on_recenter,
                                         corner_radius=6)
        recenter_button.grid(row=0, column=0, sticky="ns", pady=6)

        save_image = Image.open(resource_path("assets/icons/save.png"))
        save_ctkimage = ctk.CTkImage(light_image=save_image, dark_image=save_image, size=(40, 40))
        save_button = ctk.CTkButton(self._button_pane, 
                                     width=50, height=50, 
                                     image=save_ctkimage,
                                     text=None, 
                                     command=self._on_save,
                                     corner_radius=6)
        save_button.grid(row=1, column=0, sticky="ns", pady=6)

        back_button = ctk.CTkButton(self._button_pane,
                                    width=50, height=50,
                                    text="Powrót",
                                    command=self._on_back,
                                    corner_radius=6)
        back_button.grid(row=2, column=0, sticky="ns", pady=6)


    # Zapisz zdjęcie i dane potrzebne do otwarcia go znowu bez ponownej analizy
    def _on_save(self):
        
        starting_dir = resource_path("saved_images/")
        picked_filename = ctk.filedialog.asksaveasfilename(title="Zapisz jako...", initialdir=starting_dir)
        
        # wyrzuć rozszerzenie, jeżeli użytkownik wrzuci
        if "." in picked_filename:
            picked_filename = picked_filename.split(".", 1)[0]
            
        # picked_filename jest czysty dla bitowego dodaj .dat, a do zdjęciowego .png / bestratny
        data_filename = picked_filename + ".dat"
        image_filename = picked_filename + ".png"
        
        self._viewer.mapped_ids.tofile(data_filename)
        self._viewer._image.save(image_filename)
        
        self._log(f"Zapisano obraz do pliku {picked_filename}")


    # wycentruj widok ImageViewer
    def _on_recenter(self):
        self._viewer.recenter_view(None)

