import vrcosc
import time

def test_chatbox_input() -> None:
    vrc = vrcosc.VRCOSC()
    vrc.chatbox_input("Hello, world!")
    time.sleep(2)
    vrc.chatbox_input()
    time.sleep(2)

def test_chatbox_typing() -> None:
    vrc = vrcosc.VRCOSC()
    vrc.chatbox_typing(True)
    time.sleep(2)
    vrc.chatbox_typing(False)
    time.sleep(2)
