import subprocess
from DataExtractor import DataExtractor

class PortDescriptionExtractor:
    @staticmethod
    def get_port_des(ip, number):
        """
        Retrieves port description using SNMP.

        Args:
            ip (str): IP address.
            number (int): Port number.

        Returns:
            str: Port description.
        """
        command_for_port_des1 = "snmpwalk -v 1 -c community string "
        command_for_port_des2 = " 1.3.6.1.2.1.31.1.1.1.18"  # your OID

        command_for_port_des = command_for_port_des1 + str(ip) + command_for_port_des2 + "." + str(number)
        result = subprocess.run(command_for_port_des, shell=True, capture_output=True, text=True)
        data = DataExtractor.extract_content_inside_double_quotes_for_port(result)
        return data
