"""This module manages Bluetooth connection.

BluetoothManager allows finding Bittle's physical address, connecting to
Bittle, sending and receiving messages from it.
"""

from bleak import BleakScanner, BleakClient
import logging


__author__ = "EnriqueMoran"

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class BluetoothManager:
    """Main class to manage Bluetooth connection.

    Attributes
    ----------
    name : str
        Bittle device name (by default its BittleSPP-XXXXXX).
    address : str
        Bittle device MAC address.
    port : int
        Communication port.
    discovery_timeout : int
        Time for discovery Bluetooth devices (seconds).
    recv_timeout : int
        Socket timeout for receiving messages (seconds).
    socket : bluetooth.BluetoothSocket
        Socket for Bluetooth connection.

    Methods
    -------
    initialize_name_and_address(get_first_bittle=True):
        Finds and sets Bittle's device name and MAC address.
    get_paired_devices(flush_cache=True, lookup_names=True):
        Returns avaliable paired devices.
    connect():
        Connects to Bittle.
    send_msg(msg):
        Sends a message to Bittle.
    recv_msg(callback):
        Receives messages from Bittle via notifications.
    close_connection():
        Closes connection with Bittle.
    """

    def __init__(self):
        logging.info("Initializing BluetoothManager.")
        self._name = ""
        self._address = ""
        self._port = 1
        self._discovery_timeout = 8
        self._recv_timeout = 10
        self.client = None
        self._characteristic_uuid = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"  # Example UUID for BLE devices
        self._characteristic_uuid_rx = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"  # Example UUID for BLE devices
        self._characteristic_uuid_tx = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"  # Example UUID for BLE devices
        self._cleanup_done = False  # Track whether cleanup has been performed

    async def __aenter__(self):
        """Support async context management."""
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        """Ensure proper cleanup when exiting an async context."""
        await self.close_connection()

    def __del__(self):
        """Ensure proper cleanup when the object is deleted."""
        if not self._cleanup_done:
            logging.warning("BluetoothManager instance deleted without proper cleanup.")

    def __repr__(self):
        return f"BluetoothManager - name: {self.name}, address: " \
               f"{self.address}, port: {self.port}, discovery_timeout: " \
               f"{self.discovery_timeout}, recv_timeout: {self.recv_timeout}"

    def __str__(self):
        return f"BluetoothManager - name: {self.name}, address: " \
               f"{self.address}, port: {self.port}"

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name):
        if isinstance(new_name, str) and new_name:
            self._name = new_name
        else:
            raise TypeError("Name must be non empty str.")

    @property
    def address(self):
        return self._address

    @address.setter
    def address(self, new_address):
        if isinstance(new_address, str) and new_address:
            self._address = new_address
        else:
            raise TypeError("Address must be non empty str.")

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, new_port):
        if isinstance(new_port, int) and new_port > 0:
            self._port = new_port
        else:
            raise TypeError("Port type must be int, greater than 0.")

    @property
    def discovery_timeout(self):
        return self._discovery_timeout

    @discovery_timeout.setter
    def discovery_timeout(self, new_timeout):
        if isinstance(new_timeout, int) and new_timeout > 0:
            self._discovery_timeout = new_timeout
        else:
            raise TypeError("New timeout type must be int, greater than 0.")

    @property
    def recv_timeout(self):
        return self._recv_timeout

    @recv_timeout.setter
    def recv_timeout(self, new_timeout):
        if isinstance(new_timeout, int) and new_timeout > 0:
            self._recv_timeout = new_timeout
        else:
            raise TypeError("New timeout type must be int, greater than 0.")

    async def initialize_name_and_address(self, get_first_bittle=True):
        """Sets self._name and self._address values by searching
        among paired devices and returns its values.

        Parameters:
            get_first_bittle (bool): If True, it will search for the first
            "BittleSPP" occurrence; otherwise will search for self._name
            ocurrence (full name must be stored in self._name:
            BittleSPP-XXXXXX). If is set to False but there is no valid
            self._name (empty), it will work as if was set to True.

        Returns:
            name (str) : Found name, None if not found.
            address (str) : Found address, None if not found.
        """
        logging.info("Initializing name and address.")
        if not isinstance(get_first_bittle, bool):
            raise TypeError("Value type must be bool.")

        search_name = self.name if not get_first_bittle and self.name else "Bittle9E"
        devices = await BleakScanner.discover()

        for device in devices:
            if device.name and search_name in device.name:
                logging.info(f"Found device: {device.name} at {device.address}")
                self.name = device.name
                self.address = device.address
                return self.name, self.address

        logging.warning("No matching device found.")
        return None, None

    async def connect(self):
        """Connects to Bittle.

        Connects to Bittle and waits until a full response is given.
        Once connected, sets self.client's timeout to self._recv_timeout.

        Returns:
            res (bool): True if connected successfully, False otherwise.
        """
        logging.info(f"Attempting to connect to device at address: {self.address}")
        res = False
        try:
            self.client = BleakClient(self.address)
            res = await self.client.connect()
        except Exception as e:
            logging.error(f"Failed to connect: {e}")
        if res:
            logging.info("Successfully connected to the device.")
        else:
            logging.error("Failed to connect to the device.")
        return res

    async def send_msg(self, msg):
        """Sends a message to Bittle.

        Parameters:
            msg (str): Message to send.
        """
        logging.info(f"Sending message: {msg}")
        if not isinstance(msg, str) or not msg:
            raise TypeError("Message must be a non-empty string.")

        try:
            await self.client.write_gatt_char(self._characteristic_uuid_rx, msg.encode())
        except Exception as e:
            logging.error(f"Failed to send message: {e}")

    async def recv_msg(self, callback):
        """Receives messages from Bittle via notifications.

        Parameters:
            callback (function): A function to handle incoming notifications.
        """
        logging.info("Receiving messages via notifications.")
        try:
            await self.subscribe_to_notifications(callback)
        except Exception as e:
            logging.error(f"Failed to receive messages via notifications: {e}")

    async def close_connection(self):
        """Closes connection."""
        logging.info("Closing connection.")
        try:
            if self.client:
                await self.client.disconnect()
                self._cleanup_done = True  # Mark cleanup as done
        except Exception as e:
            logging.error(f"Failed to close connection: {e}")

    async def subscribe_to_notifications(self, callback):
        """Subscribes to notifications on the characteristic UUID.

        Parameters:
            callback (function): A function to handle incoming notifications.
        """
        logging.info("Subscribing to notifications.")
        try:
            await self.client.start_notify(self._characteristic_uuid_tx, callback)
            logging.info("Successfully subscribed to notifications.")
        except Exception as e:
            logging.error(f"Failed to subscribe to notifications: {e}")

    async def unsubscribe_from_notifications(self):
        """Unsubscribes from notifications on the characteristic UUID."""
        logging.info("Unsubscribing from notifications.")
        try:
            await self.client.stop_notify(self._characteristic_uuid_tx)
            logging.info("Successfully unsubscribed from notifications.")
        except Exception as e:
            logging.error(f"Failed to unsubscribe from notifications: {e}")
