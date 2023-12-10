import CapturaJoystick.CapturaJoystick as joystick

if __name__ == '__main__':
    joystick.start()
    while True:
        joystick.captureEvents()