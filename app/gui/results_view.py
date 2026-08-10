import customtkinter as ctk
from PIL import Image

from ..image.image_viewer import CTkImageViewer


class ResultsView(ctk.CTkFrame):
    
    def __init__(self, master, start_image: Image, mapped_ids, global_color_picked_id):
        
        super().__init__(master)
        
        self._viewer = CTkImageViewer(self, global_color_picked_id, mapped_ids)
        self._viewer.open(start_image)
        
        self._build_ui()
        
        
    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        
        self._viewer.pack(fill="both", anchor="center", expand=True)