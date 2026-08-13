import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk
import math
import numpy as np

from ..image.viewer_assets.outline_layer import OutlineLayer

class CTkImageViewer(ctk.CTkFrame):

    ZOOMS = [
        0.25,
        0.5,
        1,
        2,
        4,
        8,
        16,
        32,
        64
    ]

    def __init__(self, master, global_color_picked_id, mapped_ids, **kwargs):
        super().__init__(master, **kwargs)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(
            self,
            bg="#202020",
            highlightthickness=0,
            bd=0
        )

        self.canvas.grid(row=0, column=0, sticky="nsew")

        # ----------------------
        # stan

        self._image = None
        self._photo = None
        self._image_id = None
        
        self.global_color_picked_id = global_color_picked_id
        self.mapped_ids = mapped_ids
        
        # środek aktualnego widoku w obrazie
        self._camera_x = 0.0
        self._camera_y = 0.0

        # indeks aktualnego zoomu
        self._zoom_index = 2    # 1:1
        
        # ostatnia pozycja myszy
        self._last_mouse_x = 0
        self._last_mouse_y = 0
        
        # początkowa pozycja przy poruszaniu
        self._pan_start_camera_x = 0
        self._pan_start_camera_y = 0
        
        # podświetlenie pixela
        self._highlight_id = self.canvas.create_rectangle(
            0, 0, 0, 0,
            outline="#ffffff",
            width=3,
            state="hidden",
            tags="highlight"
        )
        
        # indeksy klastra
        self.outline_layer = OutlineLayer(self)
        
        # ----------------------
        # eventy

        self.canvas.bind(
            "<Configure>",
            self._on_resize
        )

        self.canvas.bind(
            "<MouseWheel>",
            self._mousewheel
        )
        
        self.canvas.bind(
            "<1>",
            self._start_pan
        )
        
        self.canvas.bind(
            "<B1-Motion>",
            self._pan
        )
        
        self.canvas.bind(
            "<ButtonRelease-1>",
            self._end_pan
        )
        
        self.canvas.bind(
            "<Motion>",
            self._highlight_pixel
        )
        
        self.canvas.bind(
            "<3>",
            self.check_color
        )

        self.canvas.bind(
            "<2>",
            self.recenter_view
        )
    
    # -------------------
    # Obraz
    
    def open(self, path):
        if isinstance(path, Image.Image):
            self._image = path
        else:
            self._image = Image.open(path)
        
        self.reset_view()
        
    
    def close(self):
        
        self._image = None
        self._photo = None
        
        if self._image_id:
            
            self.canvas.delete(self._image_id)
            self._image_id = None
            
            
    # -------------
    # zoom
    
    @property
    def zoom(self):
        
        return self.ZOOMS[self._zoom_index]
    
    
    def zoom_in(self):
        if self._zoom_index < len(self.ZOOMS)-1:
            self._zoom_index += 1
            self._render()
            
            
    def zoom_out(self):
        if self._zoom_index > 0:
            self._zoom_index -= 1
            self._render()
            
            
    def set_zoom(self, zoom):
        if zoom in self.ZOOMS:
            self._zoom_index = self.ZOOMS.index(zoom)
            self._render()
    
    # -------------------
    # Widok
    
    def reset_view(self):
        
        if self._image is None:
            return
        
        self._zoom_index = self.ZOOMS.index(4)
        
        self._camera_x = self._image.width / 2
        self._camera_y = self._image.height / 2
        
        self._render()

    def recenter_view(self, event):
            self._camera_x = self._image.width / 2
            self._camera_y = self._image.height / 2
            
            self._render()
     
        
    # --------------------------
    # poruszanie się po obrazie (pan)
    
    # FIXME
    # brzydka metoda, generuje nowy obraz (resampling, liczenie mase rzeczy) kiedy on już istnieje
    
    # a tam się przypierdalasz
    def _move(self, dx, dy):
        
        self._camera_x += dx
        self._camera_y += dy
        
        self._render()
    
    def _start_pan(self, event):
        
        self._last_mouse_x = event.x
        self._last_mouse_y = event.y
        
        self._pan_start_camera_x = self._camera_x
        self._pan_start_camera_y = self._camera_y
        
    
    def _pan(self, event):
        
        dx = event.x - self._last_mouse_x
        dy = event.y - self._last_mouse_y
    
        
        self._last_mouse_x = event.x
        self._last_mouse_y = event.y
        
        # zamiast render żeby to działało szybciej
        # poruszaj się po wygenerowanym obrazie a nie generuj co chwila nowy
        self.canvas.move(
            self._image_id,
            dx,
            dy
        )
        
        self.canvas.move(self._highlight_id, dx, dy)
        self.canvas.move("cluster_outline", dx, dy)
        
    def _end_pan(self, event):
        
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        
        cx = cw / 2 
        cy = ch / 2
        
        # aktualna pozycja obrazu
        coords = self.canvas.coords(self._image_id)
        
        left = coords[0]
        top = coords[1]
        
        self._camera_x = (cx - left) / self.zoom
        self._camera_y = (cy - top) / self.zoom
        
        
    # ----------------
    # render    
        
    def _render(self):
        
        if self._image is None:
            return
        
        zoom = self.zoom
        
        scaled_w = int(self._image.width * zoom)
        scaled_h = int(self._image.height * zoom)
        
        rescaled = self._image.resize(
            (scaled_w, scaled_h),
            Image.Resampling.NEAREST
        )
        
        self._photo = ImageTk.PhotoImage(rescaled)
        
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        
        # środek canvas
        cx = cw / 2
        cy = ch / 2
        
        
        # pozycja lewego górnego - maszyna zawsze liczy od lewego górnego
        
        left = cx - self._camera_x * zoom
        top = cy - self._camera_y * zoom
        
        left = round(left)
        top = round(top)
        
        if self._image_id is None:
            
            self._image_id = self.canvas.create_image(
                left, top,
                anchor= "nw",
                image=self._photo,
                tags="image"
            )
            
        else:
            self.canvas.itemconfigure(
                self._image_id,
                image=self._photo
            )
            
            self.canvas.coords(
                self._image_id,
                left,
                top
            )
        
        self.outline_layer.redraw()
        
        # wrzucenie prostokąta na góre bo się chowa hihi
        self.canvas.tag_raise("highlight")
    
    # ---------------------------
    # zoom względem kursora (koło myszy)
    
    def _mousewheel(self, event):
        
        if self._image is None:
            return
        
        old_zoom = self.zoom
        
        if event.delta > 0:
            if self._zoom_index >= len(self.ZOOMS)-1:
                return
            
            new_index = self._zoom_index + 1
            
        else:
            if self._zoom_index <= 0:
                return
            
            new_index = self._zoom_index - 1
            
            
        new_zoom = self.ZOOMS[new_index]
        
        
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        
        cx = cw / 2
        cy = ch / 2
        
        # lewy górny róg starego
        left = cx - self._camera_x * old_zoom
        top = cy - self._camera_y * old_zoom
        
        
        # piksel pod kursorem
        image_x = (event.x - left) / old_zoom
        image_y = (event.y - top) / old_zoom
        
        
        # zmiana zoomu
        self._zoom_index = new_index
        
        
        # nowa kamera
        
        self._camera_x = image_x - (event.x - cx) / new_zoom
        self._camera_y = image_y - (event.y - cy) / new_zoom
        
        
        self._render()
        
        
    # ----------
    # pozycja piksela
    
    def screen_to_pixel(self, screen_x: float, screen_y: float) -> tuple[int, int]:
        
        if self._image is None:
            return (0, 0)
        
        zoom = self.zoom
        
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        
        cx = cw / 2
        cy = ch / 2
        
        left = cx - self._camera_x * zoom
        top = cy - self._camera_y * zoom
        
        idx_x = math.floor((left - screen_x) / zoom)
        idx_y = math.floor((top - screen_y) / zoom)
        
        # FIXME (?) wygląda to strasznie, jakby ktoś to chujem myślał
        # no ale działa
        return -idx_x - 1, -idx_y - 1
    
    
    def pixel_to_screen(self, pixel_x: float, pixel_y: float) -> tuple[float, float]:
        
        if self._image is None:
            return (0.0, 0.0)
        
        zoom = self.zoom
        
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        
        cx = cw / 2
        cy = ch / 2
        
        left = cx - self._camera_x * zoom
        top = cy - self._camera_y * zoom
        
        screen_x = left + pixel_x * zoom
        screen_y = top + pixel_y * zoom
    
        return screen_x, screen_y
        
        
    # ---------
    # rysowanie pixela pod myszką
    
    def pixel_rect(self, pixel_x: int, pixel_y: int):
        # FIXME nie mam pojęcia dlaczego, ale bez minusów tutaj w metodzie niżej rysuje prawidłowo, tyle że symetrycznie względem [0, 0] obrazu.
        # dodatkowo, jak narzuciłem obrócenie względem ów symetrii w _highlight_pixel to left, top są piksel niżej w prawo
        # nie mam dladego pojęcia co jebie się z koordynatami, ale musisz to naprawić. mocno.
        
        # jak nie działa napierdalaj, jak działa to spierdalaj - zostaw to skoro działą
        
        left, top = self.pixel_to_screen(pixel_x, pixel_y)
        
        zoom = self.zoom
        
        return (
            left,
            top,
            left + zoom,
            top + zoom
        )
        
    
    def _highlight_pixel(self, event):
        
        if self.zoom <= 4:
            self.canvas.itemconfigure(self._highlight_id, state= "hidden")
            return
        
        px, py = self.screen_to_pixel(event.x, event.y)
        
        self.canvas.coords(
            self._highlight_id,
            *self.pixel_rect(px, py)
        )
        
        self.canvas.itemconfigure(
            self._highlight_id,
            state="normal"
        )
        
    
    def check_color(self, event):
        
        px, py = self.screen_to_pixel(event.x, event.y)
        
        if (
            px < 0 or py < 0 or
            py >= self.mapped_ids.shape[0] or
            px >= self.mapped_ids.shape[1]
        ):
            return
        
        image_array = np.asarray(self._image)
        
        cluster = self.outline_layer.find_cluster(input_array=image_array, start_x=px, start_y=py)
        self.outline_layer.set_cluster(cluster)
        
        # globalna śledzona RGB żeby wiedziec jaki kolor jest wybrany mogłem zapisać tylko id kurwa co za debil
        # update: już slędzę id
        picked_color_id = self.mapped_ids[py, px]
        self.global_color_picked_id.set(int(picked_color_id))


    # --------------------------
    # resize okna
    
    def _on_resize(self, event):
        self._render()
        