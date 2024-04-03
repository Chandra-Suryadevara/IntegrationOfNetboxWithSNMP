import requests
import json
import time
import urllib3
import pynetbox
from requests.exceptions import HTTPError

# Disable insecure request warning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class NetboxManager:
    def __init__(self, netbox_url, api_token):
        """
        Initializes NetboxManager with Netbox URL and API token.

        Args:
            netbox_url (str): URL of the Netbox instance.
            api_token (str): API token for authentication.
        """
        self.NETBOX_URL = netbox_url
        self.API_TOKEN = api_token
        self.HEADERS = {'Authorization': f'Token {api_token}',
                        'Content-Type': 'application/json', 'Accept': 'application/json'}
        self.nb = pynetbox.api(netbox_url, token=api_token)

    def request_devices(self, device_name, max_retries=3, delay_seconds=1):
        """
        Requests device information from Netbox.

        Args:
            device_name (str): Name of the device.
            max_retries (int): Maximum number of retries.
            delay_seconds (int): Delay between retries.

        Returns:
            str: Device ID if found, "NULL" otherwise.
        """
        for _ in range(max_retries):
            try:
                request_url = f"{self.NETBOX_URL}/api/dcim/devices/?name={device_name}"
                devices = requests.get(request_url, headers=self.HEADERS)
                devices.raise_for_status()
                result = devices.json()
                device_id = result["results"][0]["id"]
                return device_id
            except requests.exceptions.RequestException as e:
                print(f"Error: {e}. Retrying in {delay_seconds} seconds...")
                time.sleep(delay_seconds)
            except json.decoder.JSONDecodeError as json_err:
                print(f"JSON Decode Error: {json_err}")
                print(f"Response content: {devices.text}")

        print(f"Maximum retries reached. Unable to get device ID for {device_name}.")
        return "NULL"

    def request_interface_id(self, device_name, interface_name, max_retries=2, delay_seconds=0.5):
        """
        Requests interface ID from Netbox.

        Args:
            device_name (str): Name of the device.
            interface_name (str): Name of the interface.
            max_retries (int): Maximum number of retries.
            delay_seconds (int): Delay between retries.

        Returns:
            str: Interface ID if found, "NULL" otherwise.
        """
        for _ in range(max_retries):
            try:
                device_id = self.request_devices(device_name)
                interface = self.nb.dcim.interfaces.get(device_id=device_id, name=interface_name)

                if interface is not None:
                    result = interface.id
                    return result
                else:
                    print(f"Interface not found. Retrying in {delay_seconds} seconds...")
                    time.sleep(delay_seconds)
                    if max_retries == 9:
                        return "NULL"
            except Exception as e:
                print(f"An unexpected error occurred: {e}. Retrying in {delay_seconds} seconds...")
                time.sleep(delay_seconds)

        print(f"Maximum retries reached. Unable to get interface ID for {device_name} - {interface_name}.")
        return "NULL"

    def update_interface(self, device_name, interface_name, port_des):
        """
        Updates interface information in Netbox.

        Args:
            device_name (str): Name of the device.
            interface_name (str): Name of the interface.
            port_des (str): Port description.

        Returns:
            None
        """
        max_retries = 5
        retry_delay_seconds = 0.2
        
        ID = self.request_interface_id(device_name, interface_name)
        if ID != "NULL":
            portdes_from_netbox = str(self.request_port_des_from_netbox(device_name, interface_name)).strip()
            if portdes_from_netbox == None or portdes_from_netbox == " ":
                portdes_from_netbox = ""
            if port_des == None or port_des == " ":
                port_des = ""
            if portdes_from_netbox != port_des:
                for attempt in range(1, max_retries + 1):
                    try:
                        devices = self.nb.dcim.interfaces.update([
                            {'id': int(ID), 'name': str(interface_name), 'custom_fields': {'Port_Description': str(port_des)}}
                        ])
                        print(device_name, interface_name, str(port_des))
                        break
                    except requests.exceptions.InvalidJSONError as e:
                        print(f"Attempt {attempt} failed. Waiting for {retry_delay_seconds} seconds before retrying...")
                        time.sleep(retry_delay_seconds)
                    except Exception as e:
                        print(f"An unexpected error occurred: {e}")
                        break
                else:
                    print(f"Update failed for {device_name} after {max_retries} attempts.")

    def request_port_des_from_netbox(self, device_name, interface_name):
        """
        Requests port description from Netbox.

        Args:
            device_name (str): Name of the device.
            interface_name (str): Name of the interface.

        Returns:
            str: Port description.
        """
        interface = self.request_interface_object(device_name, interface_name)
        try:
            cus = interface.custom_fields['Port_Description']
            return cus
        except KeyError:
            return "Port description not available"

    def request_interface_object(self, device_name, interface_name):
        """
        Requests interface object from Netbox.

        Args:
            device_name (str): Name of the device.
            interface_name (str): Name of the interface.

        Returns:
            Interface: Interface object.
        """
        device_id = self.request_devices(device_name)
        interface = self.nb.dcim.interfaces.get(device_id=device_id, name=interface_name)
        return interface

# Example usage:
if __name__ == "__main__":
    netbox_manager = NetboxManager(netbox_url="Your netbox website", api_token="API TOKEN")
    netbox_manager.update_interface(device_name="device_name", interface_name="interface_name", port_des="port_description")
