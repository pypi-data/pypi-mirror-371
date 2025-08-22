import vrcosc
import time

def test_jump() -> None:
    vrc = vrcosc.VRCOSC()
    vrc.jump()
    time.sleep(2)

def test_moving() -> None:
    vrc = vrcosc.VRCOSC()
    vrc.moving_forward(True)
    time.sleep(0.5)
    vrc.moving_forward(False)
    vrc.moving_right(True)
    time.sleep(0.5)
    vrc.moving_right(False)
    vrc.moving_backward(True)
    time.sleep(0.5)
    vrc.moving_backward(False)
    vrc.moving_left(True)
    time.sleep(0.5)
    vrc.moving_left(False)
    time.sleep(2)

def test_running() -> None:
    vrc = vrcosc.VRCOSC()
    vrc.running(True)
    vrc.moving_forward(True)
    time.sleep(0.5)
    vrc.moving_forward(False)
    vrc.moving_right(True)
    time.sleep(0.5)
    vrc.moving_right(False)
    vrc.moving_backward(True)
    time.sleep(0.5)
    vrc.moving_backward(False)
    vrc.moving_left(True)
    time.sleep(0.5)
    vrc.moving_left(False)
    vrc.running(False)
    time.sleep(2)
