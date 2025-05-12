"""An example of Connecting to Bittle using BluetoothManager.

Create a BluetoothManager instance and search for Bittle MAC address.
If Bittle is found among avaliable paired bluetooth devices, connect to it.
If connection is successful, send 'khi' and 'd' commands to check whether
Bittle receives and replies to them.
"""

import os
import sys
import time
import asyncio

sys.path.append(os.path.join(sys.path[0], '..'))

from pyBittle import bluetoothManager  # noqa: E402


__author__ = "EnriqueMoran"


if __name__ == "__main__":
    async def main():
        btManager = bluetoothManager.BluetoothManager()  # Create bluetoothManager
        print(f"Searching for Bittle in paired devices...")
        name, addr = await btManager.initialize_name_and_address()  # Get name and addr
        if name and addr:
            print(f"Bittle found, name: {name}, address: {addr}")
            print("Connecting to Bittle...")
            connected = await btManager.connect()  # Connect to Bittle
            print(f"Connected: {connected}")
            if connected:
                print("Subscribing to notifications...")

                # Function to handle notifications and print them to stdout
                def notification_callback(sender, data):
                    message = data.decode("utf-8").strip()
                    print(f"Received from {sender}: {message}")

                # Subscribe to notifications with the new callback
                await btManager.subscribe_to_notifications(notification_callback)

                # Read messages from stdin and send them via Bluetooth
                try:
                    while True:
                        user_input = input("Enter message to send: ")
                        if user_input.lower() == "exit":
                            print("Exiting...")
                            break
                        await btManager.send_msg(user_input)
                except KeyboardInterrupt:
                    print("Exiting due to keyboard interrupt...")
                finally:
                    print("Unsubscribing from notifications and closing connection...")
                    await btManager.unsubscribe_from_notifications()
                    await btManager.close_connection()
                    print("Connection closed.")
        else:  # Bittle not found in paired and avaliable devices
            print("Bittle not found!")

    asyncio.run(main())
