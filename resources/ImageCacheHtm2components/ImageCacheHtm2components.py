import re

def convert_html_to_components(input_file, output_file):
    components = {}

    # Regular expression to extract names and coordinates from HTML <area> tags
    pattern = re.compile(r'<area title="(?:Bitmap|Colour):(\w+)" shape=rect coords="(\d+),(\d+),(\d+),(\d+)">')

    with open(input_file, 'r') as file:
        html_content = file.read()

        # Find all matches in the HTML file
        matches = pattern.findall(html_content)
        for match in matches:
            name, x1, y1, x2, y2 = match
            x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
            components[name] = (x1, y1, x2 + 1, y2 + 1)  # Adding 1 to make coordinates inclusive

    # Write the components to the output file
    with open(output_file, 'w') as out_file:
        out_file.write("{\n")
        for name, rect in components.items():
            out_file.write(f'    "{name}": {rect},\n')
        out_file.write("}\n")

# Usage
convert_html_to_components('ImageCache.htm', 'components.txt')
