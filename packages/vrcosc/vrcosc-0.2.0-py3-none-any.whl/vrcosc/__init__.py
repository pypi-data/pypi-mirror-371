from __future__ import annotations
from pythonosc.udp_client import SimpleUDPClient
import time

class VRCOSC:
    def __init__(self, host:str="127.0.0.1", port:int=9000) -> None:
        self.host = host
        self.port = port
        self.client = SimpleUDPClient(self.host, self.port)

    def chatbox_input(self, text:str="", immediate:bool=True, sound:bool=False) -> None:
        self.client.send_message("/chatbox/input", [text, immediate, sound])

    def chatbox_typing(self, typing:bool=True) -> None:
        self.client.send_message("/chatbox/typing", typing)

    def jump(self) -> None:
        self.client.send_message("/input/Jump", 1)
        time.sleep(0.01)
        self.client.send_message("/input/Jump", 0)

    def running(self, running:bool=True) -> None:
        self.client.send_message("/input/Run", running)

    def moving_forward(self, moving:bool=True) -> None:
        self.client.send_message("/input/MoveForward", moving)

    def moving_backward(self, moving:bool=True) -> None:
        self.client.send_message("/input/MoveBackward", moving)

    def moving_left(self, moving:bool=True) -> None:
        self.client.send_message("/input/MoveLeft", moving)

    def moving_right(self, moving:bool=True) -> None:
        self.client.send_message("/input/MoveRight", moving)
