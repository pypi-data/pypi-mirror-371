import trigga
import asyncio


async def main():
    trigga.run()

    previous_state = None
    while True:
        current_state = trigga.trigga
        if previous_state is not None and previous_state != current_state:
            if current_state:
                print("Deadman activated")
            else:
                print("Deadman deactivated")
        previous_state = current_state
        print(trigga.trigga)
        await asyncio.sleep(0.1)

if __name__ == "__main__":
    asyncio.run(main())