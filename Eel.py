import eel
import os
import base64
import tkinter as tk
from tkinter import filedialog
from husmorph.Utils import ShapePredictorTrainer, predict_landmarks
import xml.etree.ElementTree as ET

eel.init('web')
VALID_EXTENSIONS = ('.jpg', '.jpeg', '.png')

@eel.expose
def select_folder():
    root = tk.Tk()
    root.withdraw()
    folder = filedialog.askdirectory(title="Select Folder with Images")
    return folder

@eel.expose
def select_save_folder():
    root = tk.Tk()
    root.withdraw()
    folder = filedialog.askdirectory(title="Select Folder to Save XML")
    return folder

@eel.expose
def get_image_list(folder):
    if not folder:
        return []
    files = sorted([os.path.join(folder, f) for f in os.listdir(folder)
                    if f.lower().endswith(VALID_EXTENSIONS)])
    return files

@eel.expose
def get_image_data(image_path):
    if not os.path.exists(image_path):
        return ""
    ext = os.path.splitext(image_path)[1].lower()
    mime = "image/jpeg" if ext in (".jpg", ".jpeg") else "image/png"
    with open(image_path, "rb") as f:
        data = f.read()
    b64_data = base64.b64encode(data).decode('utf-8')
    return f"data:{mime};base64,{b64_data}"

@eel.expose
def select_xml_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(title="Select XML File", filetypes=[("XML Files", "*.xml")])
    return file_path

@eel.expose
def get_xml_data(file_path):
    if not os.path.exists(file_path):
        return ""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

@eel.expose
def save_xml(landmarks, image_dims, images_folder, save_folder):
    if not save_folder:
        return "No save folder selected."
    root_elem = ET.Element("dataset")
    name_elem = ET.SubElement(root_elem, "name")
    name_elem.text = "Image Dataset"
    comment_elem = ET.SubElement(root_elem, "comment")
    comment_elem.text = "This dataset contains images with landmarks."
    images_elem = ET.SubElement(root_elem, "images")
    for image_path, points in landmarks.items():
        if not points:
            continue
        image_elem = ET.SubElement(images_elem, "image")
        image_elem.set("file", os.path.abspath(image_path))
        dims = image_dims.get(image_path, {"width": 0, "height": 0})
        box_elem = ET.SubElement(image_elem, "box")
        box_elem.set("top", "1")
        box_elem.set("left", "1")
        box_elem.set("width", str(dims["width"] - 1))
        box_elem.set("height", str(dims["height"] - 1))
        for idx, point in enumerate(points):
            part_elem = ET.SubElement(box_elem, "part")
            part_elem.set("name", str(idx))
            part_elem.set("x", str(point["x"]))
            part_elem.set("y", str(point["y"]))
    tree = ET.ElementTree(root_elem)
    images_folder_name = os.path.basename(os.path.normpath(images_folder))
    output_path = os.path.join(save_folder, f"{images_folder_name}.xml")
    tree.write(output_path, xml_declaration=True, encoding="utf-8")
    return f"Landmarks saved to {output_path}"

@eel.expose
def save_xml_edit(landmarks, image_dims, xml_file_path):
    if not xml_file_path:
        return "No XML file loaded."
    root_elem = ET.Element("dataset")
    name_elem = ET.SubElement(root_elem, "name")
    name_elem.text = "Image Dataset"
    comment_elem = ET.SubElement(root_elem, "comment")
    comment_elem.text = "This dataset contains images with landmarks."
    images_elem = ET.SubElement(root_elem, "images")
    for image_path, points in landmarks.items():
        if not points:
            continue
        image_elem = ET.SubElement(images_elem, "image")
        image_elem.set("file", os.path.abspath(image_path))
        dims = image_dims.get(image_path, {"width": 0, "height": 0})
        box_elem = ET.SubElement(image_elem, "box")
        box_elem.set("top", "1")
        box_elem.set("left", "1")
        box_elem.set("width", str(dims["width"] - 1))
        box_elem.set("height", str(dims["height"] - 1))
        for idx, point in enumerate(points):
            part_elem = ET.SubElement(box_elem, "part")
            part_elem.set("name", str(idx))
            part_elem.set("x", str(point["x"]))
            part_elem.set("y", str(point["y"]))
    tree = ET.ElementTree(root_elem)
    tree.write(xml_file_path, xml_declaration=True, encoding="utf-8")
    return f"Landmarks saved to {xml_file_path}"

@eel.expose
def init_training(xml_file, path, threads, n_trials):
    try:
        trainer = ShapePredictorTrainer(xml_file=xml_file, base_path=path, threads=threads)
        trainer.parallel_optuna(n_trials)
    except Exception as e:
        print(e)

@eel.expose
def open_mlFile():
    root = tk.Tk()
    root.withdraw()
    file = filedialog.askopenfilename()
    return file

@eel.expose
def predict_new_landmarks(ml_model, images, path):
    try:
        predict_landmarks(ml_model, images, path)
    except Exception as e:
        return e

eel.start('index.html', size=(1024, 768))