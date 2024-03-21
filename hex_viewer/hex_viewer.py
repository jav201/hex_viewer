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
        if not isinstance(other, HexViewer):
            print("Objects are not of the same type.")
            return

        self_sections = {section['name']: section for section in self._sections}
        other_sections = {section['name']: section for section in other._sections}
        if set(self_sections.keys()) != set(other_sections.keys()):
            print("Objects do not have the same sections.")
            return

        # Prepare to collect reports for both self and other
        self_differences_report = []
        other_differences_report = []

        for name in self_sections.keys():
            if name not in other_sections:
                continue

            self_section = self_sections[name]
            other_section = other_sections[name]

            # Calculate line numbers
            start_line_self, end_line_self = self._calculate_line_numbers(self_section)
            start_line_other, end_line_other = self._calculate_line_numbers(other_section)

            # Capture output for both self and other
            self_output = self.capture_display_range(start_line_self, end_line_self)
            other_output = other.capture_display_range(start_line_other, end_line_other)

            # Process and compare the outputs
            self_report, other_report = self._process_section_differences(name, self_output, other_output)
            self_differences_report.append(self_report)
            other_differences_report.append(other_report)

        # Write reports for both self and other
        self._write_report(self_differences_report, self.file_path, other.file_path)
        self._write_report(other_differences_report, other.file_path, self.file_path)

    def _calculate_line_numbers(self, section):
        start_address = int(section['start'], 16)
        end_address = int(section['end'], 16)
        start_line = start_address // 16
        end_line = end_address // 16
        return start_line, end_line

    def _process_section_differences(self, section_name, self_output, other_output):
        self_lines = self_output.splitlines()
        other_lines = other_output.splitlines()
        self_section_report = f"\nSection: {section_name}\n"
        other_section_report = f"\nSection: {section_name}\n"

        for self_line, other_line in zip(self_lines, other_lines):
            if self_line != other_line:
                self_section_report += f"{self_line}    *\n"
                other_section_report += f"{other_line}    *\n"
            else:
                self_section_report += self_line + "\n"
                other_section_report += other_line + "\n"

        return self_section_report, other_section_report

    def _write_report(self, report_content, file_path_1, file_path_2):
        report_filename = f"{file_path_1}-vs-{file_path_2}-differences.txt"
        with open(report_filename, 'w') as report_file:
            for section_diff in report_content:
                report_file.write(section_diff)
        
        print(f"Detailed report added to {report_filename}")


        # Additional methods like capture_display_range need to be implemented accordingly.
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