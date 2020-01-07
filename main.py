def basic_test():
    import time, machine

    led = machine.Pin(5, machine.Pin.OUT)
    button = machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_UP)
    try:
        while True:
            print(button.value())
            if button.value():
                led.on()
            else:
                led.off()
            time.sleep(1)
    except KeyboardInterrupt:
        led.off()
