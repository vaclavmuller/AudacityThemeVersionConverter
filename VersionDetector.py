import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageDraw, ImageTk
import os
import ast

# Function to load components from a text file
def load_components(filename):
    with open(filename, 'r') as file:
        components = ast.literal_eval(file.read())
    return components

# Function to overlay components on the selected ImageCache
def overlay_components(image_path, components_file):
    image = Image.open(image_path)
    components = load_components(components_file)
    draw = ImageDraw.Draw(image)
    border_color = (242, 176, 39)  # Yellow color for the border
    border_width = 1

    for rect in components.values():
        # Draw the yellow border around each component
        draw.rectangle(
            [rect[0] - border_width, rect[1] - border_width, rect[2] + border_width - 1, rect[3] + border_width - 1],
            outline=border_color,
            width=border_width
        )

    return image

# Function to resize an image for display
def resize_image(image, scale=0.8):
    new_width = int(image.width * scale)
    new_height = int(image.height * scale)
    return image.resize((new_width, new_height), Image.Resampling.LANCZOS)

# Function to display the overlay image in the GUI
def display_overlay():
    if not selected_image_path or not version_var.get():
        messagebox.showerror("Error", "Please select an ImageCache.png and version.")
        return

    components_file = os.path.join("resources", f"components{version_var.get()}.txt")
    if not os.path.exists(components_file):
        messagebox.showerror("Error", f"Components file not found for version {version_var.get()}.")
        return

    try:
        overlaid_image = overlay_components(selected_image_path, components_file)
        scaled_image = resize_image(overlaid_image, scale=0.8)  # Resize the image for display
        photo = ImageTk.PhotoImage(scaled_image)
        image_label.config(image=photo)
        image_label.image = photo  # Keep a reference to avoid garbage collection
    except Exception as e:
        messagebox.showerror("Error", f"Failed to display overlay: {e}")

# Function to select the ImageCache.png
def select_image_cache():
    global selected_image_path
    selected_image_path = filedialog.askopenfilename(filetypes=[("PNG files", "*.png")])
    if selected_image_path:
        image_name_label.config(text=f"Selected: {os.path.basename(selected_image_path)}")
        display_overlay()  # Automatically update overlay after selecting a file

# Set up the GUI
root = tk.Tk()
root.title("Audacity Theme Version Detector")
root.geometry("700x710")  # Adjust the height to accommodate the scaled image

selected_image_path = None

# Frame for controls
controls_frame = tk.Frame(root)
controls_frame.pack(side="left", padx=10, pady=10)

# Button to select the ImageCache.png
select_button = tk.Button(controls_frame, text="Select ImageCache", command=select_image_cache)
select_button.grid(row=0, column=0, columnspan=2, pady=10)

# Label to display the selected file
image_name_label = tk.Label(controls_frame, text="No file selected")
image_name_label.grid(row=1, column=0, columnspan=2, pady=5)

# Label and ComboBox for selecting the version
version_label = tk.Label(controls_frame, text="Select Version:")
version_label.grid(row=2, column=0, sticky="e", padx=5)
version_var = tk.StringVar(root)

# Dynamically populate ComboBox with available versions
known_definitions = [f.split('components')[1].split('.txt')[0] for f in os.listdir("resources") if f.startswith("components") and f.endswith(".txt")]
if known_definitions:
    version_var.set(known_definitions[0])  # Automatically set the first version as default
version_combobox = tk.OptionMenu(controls_frame, version_var, *known_definitions, command=lambda _: display_overlay())
version_combobox.grid(row=2, column=1, pady=5)

# Frame for image display
image_frame = tk.Frame(root, bd=2, relief="sunken")
image_frame.pack(side="right", expand=True, fill="both", padx=10, pady=10)

image_label = tk.Label(image_frame)
image_label.pack(expand=True)

root.mainloop()
