

import socket
import json
import time

class gui_client:
    def __init__(self, host="127.0.0.1", port=65167):
        self.sock = socket.create_connection((host, port))
        self.clear()

    def _send(self, cmd):
        self.sock.sendall((json.dumps(cmd) + "\n").encode())
        time.sleep(0.1)

    def show_text(self, x, y, text, color="black", size=16):
        self._send({"type": "text", "x": x, "y": y, "text": text, "color": color, "size": size})

    def print(self, text):
        self._send({"type": "print", "text": text})

    def println(self, text):
        self._send({"type": "println", "text": text})

    def show_image(self, x, y, path, width, height):
        self._send({"type": "image", "x": x, "y": y, "path": path, "width": width, "height": height})

    def draw_line(self, x1, y1, x2, y2, color="black", width=1):
        self._send({"type": "line", "x1": x1, "y1": y1, "x2": x2, "y2": y2, "color": color, "width": width})

    def fill_rect(self, x, y, w, h, color="black"):
        self._send({"type": "fill_rect", "x": x, "y": y, "w": w, "h": h, "color": color})
        
    def draw_rect(self, x, y, w, h, width, color="black"):
        self._send({"type": "draw_rect", "x": x, "y": y, "w": w, "h": h, "width": width, "color": color})

    def fill_circle(self, cx, cy, r, color="black"):
        self._send({"type": "fill_circle", "cx": cx, "cy": cy, "r": r, "color": color})

    def draw_circle(self, cx, cy, r, width, color="black"):
        self._send({"type": "draw_circle", "cx": cx, "cy": cy, "r": r, "width": width, "color": color})
    
    def clear(self):
        self._send({"type": "clear"})

    def finish(self):
        self.sock.close()

# 外部调用
GUI = gui_client()

