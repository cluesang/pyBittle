"""An example of creating a Bittle instance and communicating with it.

Three examples are provided, three of them consist in creating a Bittle
instance and connect to it through Bluetooth, WiFi or Serial.
If connection is successful, send 'khi' and 'd' commands to check whether
Bittle receives and replies to them.
"""

import os
import sys
import time
import asyncio

sys.path.append(os.path.join(sys.path[0], '..'))

from pyBittle import bittleManager  # noqa: E402


__author__ = "EnriqueMoran"


greet = bittleManager.Command.GREETING  # khi command
rest = bittleManager.Command.REST  # d command
sit = bittleManager.Command.SIT  # ksit command


async def test_bluetooth(bittle):
    """Connect to Bittle through Bluetooth and send 'khi' and 'd' commands.

    Parameters:
            bittle (bittleManager.Bittle) : Bittle instance.
    """
    try:
        print("Connecting to Bittle through Bluetooth...")
        isConnected = await bittle.connect_bluetooth()
        print(f"Connected: {isConnected}")
        if isConnected:
            print("Subscribing to notifications...")

            def notification_callback(sender, data):
                decoded_msg = data.decode("utf-8").strip()
                print(f"Received from {sender}: {decoded_msg}")

            await bittle.receive_msg_bluetooth(notification_callback)
            print("Subscribed to notifications.")

            print("Sending command: 'GREETING'...")
            await bittle.send_command_bluetooth(greet)
            await asyncio.sleep(6)

            print("Sending command: 'REST'...")
            await bittle.send_command_bluetooth(rest)
            await asyncio.sleep(5)

            print("Closing Bluetooth connection...")
            await bittle.disconnect_bluetooth()
            print("Connection closed")
        else:
            print("Bittle not found")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        print("Ensuring cleanup...")
        await bittle.bluetoothManager.close_connection()
        print("Cleanup complete.")


def test_wifi(bittle):
    """Connect to Bittle through WiFi and send 'khi' and 'd' commands.

    Parameters:
            bittle (bittleManager.Bittle) : Bittle instance.
    """
    bittle.wifiManager.ip = input("Enter Bittle IP address: ")
    print("Connecting to Bittle through WiFi...")
    if bittle.has_wifi_connection():
        print(f"Bittle found, REST API address: "
              f"{bittle.wifiManager.http_address}")
        print("Sending command: 'GREETING'...")
        response = bittle.send_command_wifi(greet)
        print(f"Received message: {response}, expected: 200")
        time.sleep(6)
        print("Sending command: 'REST'...")
        response = bittle.send_command_wifi(rest)
        print(f"Received message: {response}, expected: 200")
        time.sleep(6)
        print("Connection closed")
    else:
        print("Can't connect to Bittle")

def test_serial(bittle):
    """Connect to Bittle through Serial and send 'ksit' and 'd' commands.

    Parameters:
            bittle (bittleManager.Bittle) : Bittle instance.
    """
    print("Connecting to Bittle through Serial...")
    isConnected = bittle.connect_serial()
    print(f"Connected: {isConnected}")
    if isConnected:
        print("Sending command: 'SIT'...")
        bittle.send_command_serial(sit)
        received = bittle.receive_msg_serial()
        decoded_msg = received.decode("utf-8")
        decoded_msg = decoded_msg.replace('\r\n', '')
        print(f"Received message: {decoded_msg}, expected: k")
        time.sleep(6)
        print("Sending command: 'REST'...")
        bittle.send_command_serial(rest)
        received = bittle.receive_msg_serial()
        decoded_msg = received.decode("utf-8")
        decoded_msg = decoded_msg.replace('\r\n', '')
        print(f"Received message: {decoded_msg}, expected: d")
        time.sleep(5)
        print("Closing Serial connection...")
        bittle.disconnect_serial()
        print("Connection closed")
    else:
        print("Bittle not found")


if __name__ == "__main__":
    connection = int(input("Select test (1 -> Bluetooth, 2 -> WiFi): "))
    if connection != 1 and connection != 2 and connection != 3:
        print("Wrong value.")
    else:
        bittle = bittleManager.Bittle()
        print("Bittle instance created")
        if connection == 1:
            asyncio.run(test_bluetooth(bittle))
        elif connection == 2:
            test_wifi(bittle)
        elif connection == 3:
            test_serial(bittle)
    print("Bittle data:\n {!s}".format(bittle))
