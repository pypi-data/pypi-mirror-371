import asyncio

import trigga

async def monitor_gamepad():
    import sdl2
    sdl2.SDL_Init(sdl2.SDL_INIT_JOYSTICK)
    sdl2.SDL_JoystickEventState(sdl2.SDL_ENABLE)
    njoy = sdl2.SDL_NumJoysticks()
    print(f"Found {njoy} joystick(s)")

    if njoy == 0:
        print("No joystick found")
        exit(1)

    joy = sdl2.SDL_JoystickOpen(0)

    event = sdl2.SDL_Event()
    while True:
        trigga_now = trigga.trigga 
        while sdl2.SDL_PollEvent(event) != 0:
            if event.type == sdl2.SDL_JOYBUTTONDOWN:
                trigga_now = True
            elif event.type == sdl2.SDL_JOYBUTTONUP:
                trigga_now = False
                break
        if trigga.trigga != trigga_now:
            trigga.trigga = trigga_now
            if trigga.trigga:
                print("Deadman trigger pressed")
            else:
                print("Deadman trigger released")
        await asyncio.sleep(0.01)

async def monitor_foot_pedal(path=None):
    """
    path e.g.: "/dev/input/by-id/usb-PCsensor_FootSwitch-event-kbd"
    """
    from evdev import InputDevice, ecodes

    dev = InputDevice(path)
    dev.grab() 

    while True:
        keys = dev.active_keys(verbose=False)
        KEY = 48 # for whatever reason it sends the 'b' key
        now_pressed = KEY in keys
        if now_pressed and not trigga.trigga:
            print("↓  pressed")
        elif not now_pressed and trigga.trigga:
            print("↑  released")

        trigga.trigga = now_pressed


        await asyncio.sleep(0.001)

async def sleep(seconds, edge=None, dt=0.001):
    """
    edge: "rising", "falling", "both" or None (which interrupts the sleep)
    """
    prev_state = trigga.trigga
    acc = 0
    while True:
        if seconds is not None and acc >= seconds:
            return
        current_state = trigga.trigga
        if current_state and not prev_state and (edge == "rising" or edge == "both"):
                return
        elif not current_state and prev_state and (edge == "falling" or edge == "both"):
            return
        prev_state = current_state
        acc += dt
        await asyncio.sleep(dt)

async def monitor(type="gamepad", **kwargs):
    if type == "gamepad":
        await monitor_gamepad(**kwargs)
    elif type == "foot-pedal":
        await monitor_foot_pedal(**kwargs)

def run(type="gamepad"):
    loop = asyncio.get_event_loop()
    loop.create_task(monitor(type))


if __name__ == "__main__":
    asyncio.run(monitor(type="foot-pedal", path="/dev/input/by-id/usb-PCsensor_FootSwitch-event-kbd"))