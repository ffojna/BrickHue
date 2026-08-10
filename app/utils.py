import sys
import os

def resource_path(path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, path)
    return os.path.join(os.path.abspath("."), path)


def find_width_from_height(width: int, height: int, new_height: int):
    if new_height == 0:
        return
    
    new_w = int(width * (new_height / height))
    
    return new_w
        
        
def find_height_from_width(width: int, height: int, new_width: int):
    if new_width == 0:
        return
    
    new_h = int(height * (new_width / width))
    
    return new_h