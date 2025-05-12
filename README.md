# pyBittle

pyBittle is an Open Source Python library for easily connecting to Bittle and controlling it.
This library provides a set of methods to communicating with Bittle through Bluetooth and WiFi, allowing to control it remotely.

In-depth documentation and usage examples: [pyBittle](https://enriquemoran95.gitbook.io/pybittle/).


## Usage example

Connecting to Bittle and sending commands is as easy as shown below:

```python
bittle = pyBittle.Bittle()  # This is your Bittle

is_connected = bittle.connect_bluetooth()  # Returns True if Bittle is connected to your computer

if is_connected:
    greet_command = pyBittle.Command.GREETING  # This is 'khi' message to be sent
    bittle.send_command_bluetooth(greet_command)  # Send 'khi' message through Bluetooth
    bittle.disconnect_bluetooth()
```

```python
bittle = pyBittle.Bittle()

bittle.wifiManager.ip = '192.168.1.241'  # This is your Bittle's IP address

push_up_command = pyBittle.Command.PUSHUP  # This is 'kpu' message to be sent

has_connection = bittle.has_wifi_connection()
if has_connection:
    bittle.send_command_wifi(push_up_command)  # Send 'kpu' message through WiFi
```

```python
bittle = pyBittle.Bittle()

is_connected = bittle.connect_serial()  # Returns True if Bittle is connected to your computer

if is_connected:
    stretch_command = pyBittle.Command.STRETCH  # This is 'kstr' message to be sent
    bittle.send_command_serial(stretch_command)  # Send 'kstr' message through Serial
    bittle.disconnect_serial()
```


## Updated Bluetooth Implementation

The `pyBittle` library now uses the `bleak` package for Bluetooth communication instead of `PyBluez`. This change improves compatibility and provides a more modern interface for handling Bluetooth Low Energy (BLE) devices.

### Notification Structure

The library now supports subscribing to notifications from Bittle. Notifications allow Bittle to send data back to your application asynchronously. Here's an example of how to use the notification system:

```python
import asyncio
from pyBittle.bluetoothManager import BluetoothManager

async def main():
    async with BluetoothManager() as btManager:
        # Initialize and connect to Bittle
        name, addr = await btManager.initialize_name_and_address()
        if name and addr:
            print(f"Connected to Bittle: {name} at {addr}")
            await btManager.connect()

            # Define a callback to handle notifications
            def notification_callback(sender, data):
                print(f"Notification from {sender}: {data.decode('utf-8').strip()}")

            # Subscribe to notifications
            await btManager.subscribe_to_notifications(notification_callback)

            # Keep the script running to receive notifications
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                print("Exiting...")
                await btManager.unsubscribe_from_notifications()

asyncio.run(main())
```

### Key Changes
- **Dependency Update**: The library now uses `bleak` instead of `PyBluez`.
- **Notification Support**: Added support for subscribing to and handling notifications from Bittle.

### Installation Update
To install the updated library, ensure you have the `bleak` package installed:

```bash
pip install bleak
```

Then, install `pyBittle` as usual:

```bash
pip install .
```


## Installation

Install automatically using the following command:
```
pip install pyBittle
```

pyBittle has the following dependencies: [bleak](https://github.com/hbldh/bleak) and [pySerial](https://github.com/pyserial/pyserial), install them manually using the following commands:

```
pip install bleak

pip install pyserial

git clone https://github.com/EnriqueMoran/pyBittle.git
pip install .
```