import csv
from lxml import etree
from typing import List, Tuple

class XMLManipulator:
    """
    A class to handle XML file manipulation operations such as parsing and saving.
    
    Attributes:
        template_filename (str): The filename of the XML template to be manipulated.
        tree (etree.ElementTree): The parsed XML tree.
        root (etree.Element): The root element of the parsed XML tree.
    """

    def __init__(self, template_filename: str):
        """
        Initialize the XMLManipulator with the provided template filename.
        
        Args:
            template_filename (str): The filename of the XML template to be manipulated.
        """
        self.template_filename = template_filename
        self.tree = etree.parse(template_filename)
        self.root = self.tree.getroot()

    def save_to_file(self, output_filename: str):
        """
        Save the modified XML tree to a file.
        
        Args:
            output_filename (str): The name of the file to save the modified XML content.
        """
        self.tree.write(output_filename, pretty_print=True, xml_declaration=True, encoding="UTF-8")

    def find_rllcontent(self):
        """
        Find the RLLContent element by traversing the XML structure.
        
        Returns:
            etree.Element: The RLLContent element if found, otherwise None.
        """
        for controller in self.root.findall("Controller"):
            for program in controller.findall("Programs"):
                for prog in program.findall("Program"):
                    for routine in prog.findall("Routines"):
                        for rtn in routine.findall("Routine"):
                            rllcontent = rtn.find("RLLContent")
                            if rllcontent is not None:
                                return rllcontent
        return None

class L5XParser:
    """
    A class to handle the parsing and modification of L5X files.
    
    Attributes:
        xml_manipulator (XMLManipulator): An instance of XMLManipulator to handle XML operations.
    """

    def __init__(self, xml_manipulator: XMLManipulator):
        """
        Initialize the L5XParser with an XMLManipulator instance.
        
        Args:
            xml_manipulator (XMLManipulator): An instance of XMLManipulator to handle XML operations.
        """
        self.xml_manipulator = xml_manipulator

    def clear_rungs(self):
        """
        Clear all Rung elements from the RLLContent element.
        """
        rllcontent = self.xml_manipulator.find_rllcontent()
        if rllcontent is not None:
            for rung in rllcontent.findall("Rung"):
                rllcontent.remove(rung)

    def add_rungs(self, devices: List[List[str]], output_filename: str):
        """
        Add rungs to the RLLContent element for each device provided.
        
        Args:
            devices (List[List[str]]): A list of device information lists.
            output_filename (str): The name of the file to save the modified XML content.
        """
        rllcontent = self.xml_manipulator.find_rllcontent()
        if rllcontent is not None:
            next_rung_number = 1

            for device in devices:
                module_name, ip_address, id_number, em_switch, port = device
                ip_formatted = ",".join(ip_address.split("."))

                # Create the first rung
                rung1_comment = (
                    f"**************************\n{module_name}\n**************************\n"
                    "Mapping of switch port inputs to IP Address"
                )
                rung1_content = "NOP();"
                rung1 = self.create_rung_with_cdata(next_rung_number, rung1_comment, rung1_content)
                rllcontent.append(rung1)
                next_rung_number += 1

                # Create the content for the second rung
                module_name_length = len(module_name)
                moves = [
                    f"MOV({module_name_length}, ENET_STAT_1stSYS_ID[{id_number}].Description.LEN)"
                ]
                for index, char in enumerate(module_name):
                    ascii_value = ord(char)
                    moves.append(f"MOV({ascii_value}, ENET_STAT_1stSYS_ID[{id_number}].Description.DATA[{index}])")

                # Combine all MOV commands into a single content string and wrap with additional square brackets
                rung2_content = f"[{', '.join(moves)} ];"
                rung2 = self.create_rung_with_cdata(next_rung_number, None, rung2_content)
                rllcontent.append(rung2)
                next_rung_number += 1

        self.xml_manipulator.save_to_file(output_filename)

    @staticmethod
    def create_rung_with_cdata(rung_number: int, comment: str, content: str) -> etree.Element:
        """
        Create a rung XML element with CDATA content.
        
        Args:
            rung_number (int): The rung number.
            comment (str): A comment associated with the rung.
            content (str): The content of the rung in CDATA format.
        
        Returns:
            etree.Element: The created Rung element.
        """
        rung = etree.Element("Rung", Use="Target", Number=str(rung_number), Type="N")
        if comment:
            comment_elem = etree.SubElement(rung, "Comment")
            comment_elem.text = etree.CDATA(comment)
        text = etree.SubElement(rung, "Text")
        text.text = etree.CDATA(content)
        return rung

class DeviceParser:
    """
    A class to handle parsing of device information from a CSV file.
    """

    @staticmethod
    def read_devices_from_csv(csv_filename: str) -> List[List[str]]:
        """
        Parse the CSV file containing device information.
        
        Args:
            csv_filename (str): The name of the CSV file containing device information.
        
        Returns:
            List[List[str]]: A list of device information lists.
        """
        devices = []
        with open(csv_filename, newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                devices.append(row)
        return devices

if __name__ == "__main__":
    template_filename = 'HMI_Lables_Template.L5X'
    csv_filename = 'devices.csv'
    output_filename = 'output.L5X'

    devices = DeviceParser.read_devices_from_csv(csv_filename)

    xml_manipulator = XMLManipulator(template_filename)
    parser = L5XParser(xml_manipulator)

    parser.clear_rungs()
    parser.add_rungs(devices, output_filename)

    print(f'Rungs added successfully and saved to {output_filename}')
