import re

class DataExtractor:
    @staticmethod
    def filter_data(DICT_DATA):
        """
        Filters the data based on predefined patterns.

        Args:
            DICT_DATA (dict): Dictionary containing data.

        Returns:
            dict: Filtered data dictionary.
        """
        patterns = [r'Gi\d+/0/\d+', r'Te\d+/1/\d+']
        extracted_data = {}
        for OID, Data in DICT_DATA.items():
            matches_list = []
            for pattern in patterns:
                matches = re.findall(pattern, Data)
                matches_list.extend(matches)
            extracted_data[OID] = matches_list
        extracted_data = DataExtractor.remove_empty_data(extracted_data)
        return extracted_data

    @staticmethod
    def remove_empty_data(extracted_data):
        """
        Removes entries with empty data.

        Args:
            extracted_data (dict): Extracted data dictionary.

        Returns:
            dict: Data dictionary with empty entries removed.
        """
        keys_to_remove = [key for key, value in extracted_data.items() if value == []]
        
        for key in keys_to_remove:
            del extracted_data[key]
        return extracted_data

    @staticmethod
    def find_last_period_index(string):
        """
        Finds the index of the last period in the string.

        Args:
            string (str): Input string.

        Returns:
            int: Index of the last period in the string.
        """
        last_period_index = string.rfind('.')
        return last_period_index

    @staticmethod
    def extract_content_inside_double_quotes_and_OID(Filtered_Data):
        """
        Extracts content inside double quotes and OID from filtered data.

        Args:
            Filtered_Data (list): List of filtered data.

        Returns:
            dict: Dictionary containing OID and corresponding content inside double quotes.
        """
        DICT_DATA = {}
        pattern = r'"(.*?)"'
        for data in Filtered_Data:
            index = data.find("=")
            OID = data[:index]
            OID = data[DataExtractor.find_last_period_index(OID) + 1:index - 1].strip()
            matches = str(re.findall(pattern, data))
            DICT_DATA[OID] = matches
        DICT_DATA = DataExtractor.filter_data(DICT_DATA)
        return DICT_DATA

    @staticmethod
    def extract_content_inside_double_quotes_for_device_name(Data):
        """
        Extracts content inside double quotes for device name.

        Args:
            Data (str): Input data.

        Returns:
            str: Content inside double quotes for device name.
        """
        pattern = r'"(.*?)"'
        Data = str(Data)
        matches = str(re.findall(pattern, Data))
        index = matches.find(".")
        index2 = matches.find("'")
        matches = matches[index2 + 1:index]
        return matches

    @staticmethod
    def extract_content_inside_double_quotes_for_port(Data):
        """
        Extracts content inside double quotes for port.

        Args:
            Data (str): Input data.

        Returns:
            str: Content inside double quotes for port.
        """
        pattern = r'"(.*?)"'
        Data = str(Data)
        matches = re.findall(pattern, Data)
        # Joining the matches into a single string
        matches_str = ' '.join(matches)
        if not matches_str:
            matches_str = " "
        return matches_str
