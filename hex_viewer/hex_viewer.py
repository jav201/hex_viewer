import json
import io
import sys
import difflib

class HexViewer:
    def __init__(self, file_path, json_sections_path):
        self.file_path = file_path
        self._json_sections_path = json_sections_path
        self.hex_data = self.read_hex_file()
        self._sections = self._load_sections()
        self._data_type = self._load_data_type()

    def read_hex_file(self):
        with open(self.file_path, 'rb') as f:
            return f.read()
    
    def _load_sections(self):
        with open(self._json_sections_path, 'r') as f:
            sections_data = json.load(f)
            return sections_data["memory_sections"]
    
    def _load_data_type(self):
        with open(self._json_sections_path, 'r') as f:
            data = json.load(f)
            return data["data_type"]
        
    @property
    def data_type(self):
        return self._data_type

    def read_hex_file(self):
        with open(self.file_path, 'rb') as f:
            return f.read()
        
    def decode_hex(self):
        # Read hex file as binary data, return each byte as an integer in a list
        return [byte for byte in self.hex_data]
    
    def print_header(data):
        # Print the header columns
        print("Offset(hex)|", end='')
        for i in range(16):
            print(f"{i:02X}", end=' ')
        print('| Decoded Text')
        print("-" * 77)

    def get_string(self, offset_line):
        # Calculate offset string and prepare hex and text strings for the current line
        offset_string = f"{offset_line * 16:010X}"  # Note: offset_line * 16 assumes offset_line is line number
        hex_string = ' '.join(f"{byte:02X}" for byte in self.hex_data[offset_line * 16: (offset_line + 1) * 16])
        text_string = ''.join(chr(x) if 32 <= x <= 126 else '.' for x in self.hex_data[offset_line * 16: (offset_line + 1) * 16])
        return f"{offset_string}  {hex_string} | {text_string}"

    def display_offset(self, offset_line):
        self.print_header()
        print(self.get_string(offset_line))

    def display_range(self, start_line, end_line):
        # Display a range of lines from start_line to end_line
        self.print_header()
        for offset_line in range(start_line, end_line + 1):
            print(self.get_string(offset_line))

    def display_section_data(self, section_name):
        # Find the section by name
        section = next((s for s in self._sections if s['name'] == section_name), None)
        
        if section:
            # Convert start and end addresses from hex to integers
            start_address = int(section['start'], 16)
            end_address = int(section['end'], 16)
            
            # Assuming each line represents 16 bytes, calculate start and end line numbers
            start_line = start_address // 16
            end_line = end_address // 16
            
            # Display the range of lines that includes the section
            print(f"Displaying data for section '{section['name']}', Start:{start_address}, End:{end_address}:")
            self.display_range(start_line, end_line)
        else:
            print(f"Section '{section_name}' not found.")

    def display_all_sections(self):
        print("Displaying all sections:")
        for section in self._sections:
            # Print section header
            print(f"\nSection Name: {section['name']}")
            print(f"Start Address: {section['start']}, End Address: {section['end']}")

            # Convert start and end addresses from hex to integers
            start_address = int(section['start'], 16)
            end_address = int(section['end'], 16)
            
            # Calculate start and end line numbers assuming each line represents 16 bytes
            start_line = start_address // 16
            end_line = end_address // 16

            # Display the range of lines for the section
            self.display_range(start_line, end_line)
    
    def difference(self, other):
        # Check if the other object is an instance of HexViewer to ensure compatibility
        if not isinstance(other, HexViewer):
            print("Objects are not of the same type.")
            return
        
        # Create dictionaries of the sections in each HexViewer object, using section names as keys
        self_sections = {section['name']: section for section in self._sections}
        other_sections = {section['name']: section for section in other._sections}

        # Check if the set of section names in both HexViewer objects are the same
        if set(self_sections.keys()) != set(other_sections.keys()):
            print("Objects do not have the same sections.")
            return
        
        # Iterate over each section in the current (self) HexViewer object
        for name, self_section in self_sections.items():
            # Get the matching section from the other HexViewer object by name
            other_section = other_sections.get(name)
            if not other_section:
                # Skip the comparison if the section is not present in both objects
                continue
                
            # Convert start and end addresses of the section from hexadecimal to integers for both HexViewer objects
            start_address_self = int(self_section['start'], 16)
            end_address_self = int(self_section['end'], 16)
            start_address_other = int(other_section['start'], 16)
            end_address_other = int(other_section['end'], 16)
            
            # Calculate the line numbers based on the assumption that each line represents 16 bytes of data
            start_line_self = start_address_self // 16
            end_line_self = end_address_self // 16
            start_line_other = start_address_other // 16
            end_line_other = end_address_other // 16
            
            # Capture the output of the display_range function as strings for both self and other
            # Note: The capture_display_range method is assumed to redirect the output of display_range to a string
            self_output = self.capture_display_range(start_line_self, end_line_self)
            other_output = other.capture_display_range(start_line_other, end_line_other)
            
            print(f"\nSection: {name}\n")
            
            # Split the captured outputs into lines for comparison
            self_lines = self_output.splitlines()
            other_lines = other_output.splitlines()
            
            # Iterate over the lines of the captured outputs, comparing them
            for self_line, other_line in zip(self_lines, other_lines):
                # If the lines differ, print the line from self with an asterisk to indicate a difference
                if self_line != other_line:
                    print(f"{self_line}    *")
                else:
                    # If the lines are the same, just print the line without an asterisk
                    print(self_line)

                    
            # For sections in self not in other or vice versa, further handling can be added here
            # For example, print the entire section data for the section that is not present in the other object
                     
    
    def capture_display_range(self, start_line, end_line):
        # Temporarily redirect stdout to capture display_range output
        old_stdout = sys.stdout
        try:
            sys.stdout = io.StringIO()
            self.display_range(start_line, end_line)
            return sys.stdout.getvalue()
        finally:
            sys.stdout = old_stdout
            
    def __sub__(self, other):
        self.difference(other)
        return self

def main():
    viewer = HexViewer('sample.hex', 'memory_sections_type_a.json')
    viewer.display_offset(0)
    print()
    viewer.display_range(0, 10)
    print()
    viewer.display_section_data('Section01')
    print()
    viewer.display_all_sections()
    print()
    viewer1 = HexViewer('sample1.hex', 'memory_sections_type_a.json')
    viewer1 - viewer
if __name__ == "__main__":
    main()