import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageDraw
import os
import ast

# Function to load components from a text file
def load_components(filename):
    with open(filename, 'r') as file:
        components = ast.literal_eval(file.read())
    return components

# Function to save components as individual images
def save_component(image, component, rect, output_folder):
    cropped_image = image.crop(rect)
    cropped_image.save(os.path.join(output_folder, f"{component}.png"))

# Function to split an image into individual components
def split_image(image_path, components_file, output_folder):
    image = Image.open(image_path)
    components = load_components(components_file)
    os.makedirs(output_folder, exist_ok=True)

    for component, rect in components.items():
        save_component(image, component, rect, output_folder)

    # If "Colour_TimelineRulerBackground" is missing in source components, create it from "Colour_TrackInfo"
    if "Colour_TimelineRulerBackground" not in components and "Colour_TrackInfo" in components:
        save_component(image, "Colour_TimelineRulerBackground", components["Colour_TrackInfo"], output_folder)

# Function to assemble the final image from components with yellow borders and adjusted sizes
def assemble_image(output_path, components_file, temp_folder):
    components = load_components(components_file)
    assembled_image = Image.new('RGBA', (440, 836), '#010101')  # Set the correct image size and background color
    draw = ImageDraw.Draw(assembled_image)
    border_color = (242, 176, 39)  # Yellow color for the border
    border_width = 1

    for component, rect in components.items():
        try:
            component_image = Image.open(os.path.join(temp_folder, f"{component}.png"))
            
            # Calculate the size of the component based on the target rect
            target_width = rect[2] - rect[0]
            target_height = rect[3] - rect[1]
            
            # Resize the component image if its size does not match the target size
            if component_image.size != (target_width, target_height):
                component_image = component_image.resize((target_width, target_height), Image.Resampling.LANCZOS)

            # Paste the resized component onto the assembled image
            assembled_image.paste(component_image, (rect[0], rect[1]))

            # Draw the yellow border around the component
            draw.rectangle(
                [rect[0] - border_width, rect[1] - border_width, rect[2] + border_width - 1, rect[3] + border_width - 1],
                outline=border_color,
                width=border_width
            )
        except FileNotFoundError:
            print(f"Component {component} not found, skipping.")

    assembled_image.save(output_path)

# Function to handle the conversion process
def convert_image():
    if not source_file or not target_version_var.get() or not source_version_var.get():
        messagebox.showerror("Error", "Please select the ImageCache.png and versions.")
        return

    output_file = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
    if not output_file:
        return

    # Temp folder for storing components
    temp_folder = "Temp"
    
    # Split the target ImageCacheXXX.png
    split_image(os.path.join("resources", f"ImageCache{target_version_var.get()}.png"), os.path.join("resources", f"components{target_version_var.get()}.txt"), temp_folder)
    
    # Split the source ImageCacheYYY.png
    split_image(source_file, os.path.join("resources", f"components{source_version_var.get()}.txt"), temp_folder)
    
    # Assemble the final ImageCache.png with yellow borders
    assemble_image(output_file, os.path.join("resources", f"components{target_version_var.get()}.txt"), temp_folder)

    messagebox.showinfo("Success", "ImageCache.png has been successfully converted.")

# Function to select the source ImageCache
def select_image_cache():
    global source_file
    source_file = filedialog.askopenfilename(filetypes=[("PNG files", "*.png")])
    if source_file:
        image_label.config(text=f"Selected: {os.path.basename(source_file)}")

# Function to load available versions from resources
def load_versions():
    resources_path = "resources"
    component_files = [f for f in os.listdir(resources_path) if f.startswith("components") and f.endswith(".txt")]
    return [f[len("components"):-len(".txt")] for f in component_files]

# Set up the GUI
root = tk.Tk()
root.title("AudacityTheme Version Convertor")
root.geometry("400x250")  # Adjust the width of the window

source_file = None

# Load available versions dynamically
available_versions = load_versions()

# Button to select the ImageCache file
select_button = tk.Button(root, text="Select ImageCache", command=select_image_cache)
select_button.grid(row=0, column=0, columnspan=2, padx=140, pady=10)

# Label to display the selected file
image_label = tk.Label(root, text="No file selected")
image_label.grid(row=1, column=0, columnspan=2, padx=60, pady=10)

# Label and ComboBox for selecting the source version
source_label = tk.Label(root, text="Source Version:")
source_label.grid(row=2, column=0, sticky="e", padx=5)
source_version_var = tk.StringVar(root)
source_version_var.set(available_versions[0])  # default value for source version (first value)
source_version_combobox = tk.OptionMenu(root, source_version_var, *available_versions)
source_version_combobox.grid(row=2, column=1, padx=5, pady=5)

# Label and ComboBox for selecting the target version
target_label = tk.Label(root, text="Target Version:")
target_label.grid(row=3, column=0, sticky="e", padx=5)
target_version_var = tk.StringVar(root)
target_version_var.set(available_versions[-1])  # default value for target version (last value)
target_version_combobox = tk.OptionMenu(root, target_version_var, *available_versions)
target_version_combobox.grid(row=3, column=1, padx=5, pady=5)

# Button to start the conversion process
convert_button = tk.Button(root, text="Convert", command=convert_image)
convert_button.grid(row=4, column=0, columnspan=2, padx=140, pady=20)

root.mainloop()

