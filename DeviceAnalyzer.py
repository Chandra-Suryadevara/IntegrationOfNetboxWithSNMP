import subprocess
import DataExtractor as EI
import PortDescriptionExtractor as Getport
import NetboxManager as netbox

class DeviceAnalyzer:
    def __init__(self, file_name):
        self.file_name = file_name
        self.IPS = []
        self.Interface_name = []
        self.port_descriptions = []
        self.Device_name = []

    def read_ips_from_file(self):
        """Reads IP addresses from a file and stores them."""
        with open(self.file_name, 'r') as file:
            for line in file:
                self.IPS.append(line.strip())

    def add_device_ID(self, device_name, device_id):
        """Adds device ID to device name."""
        index = device_name.rfind("-")
        if device_name[index + 1] == str(device_id):
            return device_name
        else:
            if index + 1 < len(device_name) and device_name[index + 1].isdigit():
                device_name_list = list(device_name)
                device_name_list[index + 1] = str(device_id)
                updated_device_name = ''.join(device_name_list)
                return updated_device_name
            else:
                new_dev = device_name + "-" + str(device_id)
                return new_dev

    def analyze_devices(self):
        """Analyzes devices and extracts interface information."""
        command_for_ports_interface1 = "snmpwalk -v 1 -c coomunitystring "
        command_for_ports_interface2 = " 1.3.6.1.2.1.31.1.1.1.1"  # your OID
        comand_for_name_of_device1 = "snmpwalk -v 1 -c comunity string "
        comand_for_name_of_device2 = " 1.3.6.1.2.1.1.5.0"  # your OID

        for IP in self.IPS:
            Filtered_data = []
            result = subprocess.run(command_for_ports_interface1 + str(IP) + command_for_ports_interface2,
                                      shell=True, capture_output=True, text=True)
            device_name = EI.extract_content_inside_double_quotes_for_device_name(
                subprocess.run(comand_for_name_of_device1 + str(IP) + comand_for_name_of_device2,
                               shell=True, capture_output=True, text=True))

            if result.returncode == 0:
                output_lines = result.stdout.splitlines()

                for line in output_lines:
                    index1 = line.find("STRING")
                    if index1 != -1:
                        Filtered_data.append(line)

                DICT_DATA = EI.extract_content_inside_double_quotes_and_OID(Filtered_data)
                count = 0
                pre_id = 0
                for OID_local, Data in DICT_DATA.items():
                    number = str(Data)[str(Data).rfind("/") + 1:str(Data).rfind("'")]
                    if str(Data).startswith("['Gi"):
                        deviceid = str(Data)[str(Data).find("i") + 1:str(Data).find("/")]
                    else:
                        deviceid = str(Data)[str(Data).find("e") + 1:str(Data).find("/")]
                    if pre_id != deviceid:
                        device_name = self.add_device_ID(device_name, deviceid)
                        device_name = netbox.check_device(device_name)
                        pre_id = deviceid
                    if str(Data) == "['Gi" + str(deviceid) + "/0/" + str(number) + "']":
                        self.Device_name.append(device_name)
                        self.port_descriptions.append(Getport.get_port_des(IP, OID_local))
                        self.Interface_name.append("GigabitEthernet1/0/" + str(number))
                        netbox.update_interface(device_name, "GigabitEthernet1/0/" + str(number),
                                                Getport.get_port_des(IP, OID_local))

                    elif str(Data) == "['Te" + str(deviceid) + "/1/" + str(number) + "']":
                        self.Device_name.append(device_name)
                        self.port_descriptions.append(Getport.get_port_des(IP, OID_local))
                        self.Interface_name.append("TenGigabitEthernet1/1/" + str(number))
                        netbox.update_interface(device_name, "TenGigabitEthernet1/1/" + str(number),
                                                Getport.get_port_des(IP, OID_local))
            else:
                print("failed to get data using SNMP")

    def write_output_to_file(self, file_name):
        """Writes analyzed data to a file."""
        # Combine the lists into a list of strings
        data = []
        for items in zip(self.Interface_name, self.Device_name, self.port_descriptions):
            data.append('\t'.join(map(str, items)))  # Using tab as a delimiter

        # Write data to text file
        with open(file_name, 'w') as file:
            for line in data:
                file.write(line + '\n')

        print("Output saved to 'output.txt'")

# Example usage:
if __name__ == "__main__":
    analyzer = DeviceAnalyzer(file_name='input.txt')
    analyzer.read_ips_from_file()
    analyzer.analyze_devices()
    analyzer.write_output_to_file(file_name='output.txt')
