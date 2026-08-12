import customtkinter as ctk
import tkinter as tk
from PIL import Image

from ..image.image_viewer import CTkImageViewer
from ..utils import resource_path


class ResultsView(ctk.CTkFrame):
    
    def __init__(self, master, start_image: Image, mapped_ids, global_color_picked_id):
        
        super().__init__(master)
        
        self._viewer = CTkImageViewer(self, global_color_picked_id, mapped_ids)
        self._viewer.open(start_image)
        
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
        _recenter_button = ctk.CTkButton(self._button_pane, 
                                         width=50, height=50, 
                                         image=recenter_ctkimage,
                                         text=None,
                                         command=self._on_recenter,
                                         corner_radius=6)
        _recenter_button.grid(row=0, column=0, sticky="ns", pady=6)

        save_image = Image.open(resource_path("assets/icons/save.png"))
        save_ctkimage = ctk.CTkImage(light_image=save_image, dark_image=save_image, size=(40, 40))
        _save_button = ctk.CTkButton(self._button_pane, 
                                     width=50, height=50, 
                                     image=save_ctkimage,
                                     text=None, 
                                     command=self._on_save
                                     corner_radius=6)
        _save_button.grid(row=1, column=0, sticky="ns", pady=6)


    def _on_save(self):
        pass


    def _on_recenter(self):
        pass