import customtkinter as ctk
import numpy as np

SCROLL_OFFSET = 20

class ItemCard(ctk.CTkFrame):
    
    def __init__(self, master, lego_id, name, color, amount, **kwargs):
        super().__init__(
            master,
            fg_color="#121212",
            corner_radius=8,
            height=60,
            **kwargs
        )
        
        self.default_color = "#121212"
        self.selected_color = "#27479E"
        self.lego_id = lego_id
        
        self.grid_columnconfigure(1, weight=1)
        
        self.color_box = ctk.CTkFrame(
            self,
            width=50,
            fg_color=f"#{color}",
            corner_radius= 0
        )
        self.color_box.grid(row=0, column=0, rowspan=2, sticky="nsw", padx=(10, 15), pady=10)
        
        
        self.name_label = ctk.CTkLabel(
            self,
            text= f"{lego_id}: {name}",
            font=("Comfortaa", 22, "bold"),
            anchor="w"
        )
        self.name_label.grid(row=0, column=1, sticky="sw")
        
        self.info_label = ctk.CTkLabel(
            self,
            text=f"{amount} pcs.",
            font=("Comfortaa", 20),
            text_color="#cccccc",
            anchor="w"
        )
        self.info_label.grid(row=1, column=1, sticky="nw", pady=(0, 12))
        
    
    def set_selected(self, selected: bool):
        if selected:
            self.configure(fg_color=self.selected_color)
        else:
            self.configure(fg_color=self.default_color)
        


class ColorsList(ctk.CTkScrollableFrame):
    
    def __init__(self, master, mapped_color_records, global_picked_color_id, **kwargs):
        
        super().__init__(master, **kwargs)

        self.color_records = mapped_color_records
        self.global_picked_color_id = global_picked_color_id
        
        self.frame_list = []
        
        self._build_ui()
        
        self.global_picked_color_id.trace_add(
            "write",
            self._color_changed
        )
        
        
    def _build_ui(self):
        
        for record in self.color_records:

            frame_entry = ItemCard(
                self,
                lego_id=record["id"],
                name=record["name"],
                color=record["hex"],
                amount=record["count"],
            )

            frame_entry.pack(fill="x", padx=10, pady=6)

            self.frame_list.append(frame_entry)
            
            
    def scroll_to_color(self, color_id):
        for card in self.frame_list:
            if card.lego_id == color_id:
                total_height = self.frame_list[-1].winfo_y() + self.frame_list[-1].winfo_height()

                if total_height > 0:
                    position = card.winfo_y() / total_height

                    # przesunięcie do góry bo sobie spierdala
                    offset = 0.05

                    self._parent_canvas.yview_moveto(
                        max(0, position - offset)
                    )

                break
            
            
    def _color_changed(self, *_):
        picked_id = self.global_picked_color_id.get()
        
        for card in self.frame_list:
            selected = card.lego_id == picked_id
            card.set_selected(
                card.lego_id == picked_id
            )
            
            if selected:
                self.scroll_to_color(picked_id)
            

            