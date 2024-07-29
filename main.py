import csv
from lxml import etree

class L5XParser:
    def __init__(self, template_filename):
        self.template_filename = template_filename
        self.tree = etree.parse(template_filename)
        self.root = self.tree.getroot()

    def clear_rungs(self):
        for controller in self.root.findall("Controller"):
            for program in controller.findall("Programs"):
                for prog in program.findall("Program"):
                    for routine in prog.findall("Routines"):
                        for rtn in routine.findall("Routine"):
                            rllcontent = rtn.find("RLLContent")
                            if rllcontent is not None:
                                for rung in rllcontent.findall("Rung"):
                                    rllcontent.remove(rung)
                                return

    def add_rungs(self, devices, output_filename):
        rllcontent = None
        for controller in self.root.findall("Controller"):
            for program in controller.findall("Programs"):
                for prog in program.findall("Program"):
                    for routine in prog.findall("Routines"):
                        for rtn in routine.findall("Routine"):
                            rllcontent = rtn.find("RLLContent")
                            if rllcontent is not None:
                                break

        if rllcontent is not None:
            next_rung_number = 1

            def create_rung_with_cdata(rung_number, comment, content):
                rung = etree.Element("Rung", Use="Target", Number=str(rung_number), Type="N")
                if comment:
                    comment_elem = etree.SubElement(rung, "Comment")
                    comment_elem.text = etree.CDATA(comment)
                text = etree.SubElement(rung, "Text")
                text.text = etree.CDATA(content)
                return rung

            for module_name, ip_address, id_number, em_switch, port in devices:
                ip_formatted = ",".join(ip_address.split("."))

                rung1_comment = f"**************************\n{module_name}\n**************************\nMapping of switch port inputs to IP Address"
                rung1_content = "NOP();"
                rung1 = create_rung_with_cdata(next_rung_number, rung1_comment, rung1_content)
                rllcontent.append(rung1)
                next_rung_number += 1

                # Create the content for the second rung
                module_name_length = len(module_name)
                moves = [f"MOV({module_name_length}, ENET_STAT_1stSYS_ID[{id_number}].Description.LEN)"]
                for index, char in enumerate(module_name):
                    ascii_value = ord(char)
                    moves.append(f"MOV({ascii_value}, ENET_STAT_1stSYS_ID[{id_number}].Description.DATA[{index}])")

                # Combine all MOV commands into a single content string and wrap with additional square brackets
                rung2_content = f"[{', '.join(moves)} ];"
                rung2 = create_rung_with_cdata(next_rung_number, None, rung2_content)
                rllcontent.append(rung2)
                next_rung_number += 1

        self.tree.write(output_filename, pretty_print=True, xml_declaration=True, encoding="UTF-8")

def read_devices_from_csv(csv_filename):
    devices = []
    with open(csv_filename, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            devices.append(row)
    return devices

if __name__ == "__main__":
    template_filename = 'HMI_Lables_Template.L5X'  # File to parse
    csv_filename = 'devices.csv'  # 
    output_filename = 'output.L5X'

    devices = read_devices_from_csv(csv_filename)

    parser = L5XParser(template_filename)
    parser.clear_rungs()
    parser.add_rungs(devices, output_filename)

    print(f'Rungs added successfully and saved to {output_filename}')
