from collections import deque
import numpy as np

class OutlineLayer:
    
    def __init__(self, viewer):
        
        self.viewer = viewer
        
        self.cluster = None
        self.items = []
        
        self.color = "#00F7FF"
        self.width = 2
        
        
    def clear(self):
        
        for item in self.items:
            self.viewer.canvas.delete(item)
            
        self.items.clear()
        
    
    def set_cluster(self, cluster):
        self.clear()
        
        self.cluster = set(cluster)
        
        self.redraw()
        
        
    def redraw(self):

        if self.cluster is None:
            return

        self.clear()

        z = self.viewer.zoom

        for x, y in self.cluster:

            left, top = self.viewer.pixel_to_screen(x, y)

            neighbours = (
                (0, -1, left, top, left + z, top),
                (0,  1, left, top + z, left + z, top + z),
                (-1, 0, left, top, left, top + z),
                (1,  0, left + z, top, left + z, top + z)
            )

            for dx, dy, x1, y1, x2, y2 in neighbours:

                if (x + dx, y + dy) not in self.cluster:

                    item = self.viewer.canvas.create_line(
                        x1,
                        y1,
                        x2,
                        y2,
                        fill=self.color,
                        width=self.width,
                        tags="cluster_outline"
                    )

                    self.items.append(item)
                    
                    
    @staticmethod
    def find_cluster(input_array: np.ndarray, start_x: int, start_y: int):
        dir = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        
        ids_in_cluster = []
        visited = np.zeros(input_array.shape[:2], dtype=bool)
        
        q = deque()
        picked_color = input_array[start_y, start_x]
        q.append((start_x, start_y))
        
        visited[start_y, start_x] = True
        ids_in_cluster.append((start_x, start_y))
        
        while q:
            x, y = q.popleft()
            
            for dx, dy in dir:
                nx = x + dx
                ny = y + dy
                
                if 0 <= ny < len(input_array) and 0 <= nx < len(input_array[0]) and np.array_equal(input_array[ny, nx], picked_color) and not visited[ny, nx]:
                    ids_in_cluster.append((nx, ny))
                    q.append((nx, ny))
                    visited[ny, nx] = True
                    
        return ids_in_cluster
    
    
    @staticmethod
    def cluster_outline(cluster):
        
        cluster = set(cluster)
        
        outline = []
        
        for x, y in cluster:
            
            for dx, dy in ((1,0), (-1,0), (0,1), (0,-1)):
                
                if (x + dx, y + dy) not in cluster:
                    outline.append((x, y))
                    break
                
        return outline