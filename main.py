import eel
import os
import csv
import base64
import sys
from web.Utils import ShapePredictorTrainer, predict_landmarks
from PyQt5 import QtWidgets
import xml.etree.ElementTree as ET

eel.init('web')
VALID_EXTENSIONS = ('.jpg', '.jpeg', '.png')

@eel.expose
def select_folder():
    # Create a QApplication instance if one isn't already running.
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
    folder = QtWidgets.QFileDialog.getExistingDirectory(
        None, "Select Folder with Images"
    )
    return folder

@eel.expose
def select_save_folder():
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
    folder = QtWidgets.QFileDialog.getExistingDirectory(
        None, "Select save destination"
    )
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
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
    file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
        None, "Select a datafile", "", "XML Files (*.xml)"
    )
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
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
    file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
        None, "Select a ML model", "", "Data Files (*.dat)"
    )
    return file_path

@eel.expose
def predict_new_landmarks(ml_model, images, path):
    try:
        predict_landmarks(ml_model, images, path)
    except Exception as e:
        return e

@eel.expose
def xml_to_csv(xml_file):
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        images = root.findall('.//image')
        rows = []
        for img in images:
            image_name = img.get('file')
            # Use the basename only.
            base_name = os.path.basename(image_name)
            # Find the <box> element and its parts.
            box = img.find('box')
            if box is not None:
                parts = box.findall('part')
                row = [base_name]
                for part in parts:
                    # Convert coordinates to integers.
                    x = int(float(part.get('x')))
                    y = int(float(part.get('y')))
                    row.extend([x, y])
                rows.append(row)
        # Determine output CSV file path (same directory as XML, same base name).
        csv_file = os.path.splitext(xml_file)[0] + '.csv'
        # Determine maximum number of landmark columns (excluding image name).
        max_cols = max((len(row) - 1 for row in rows), default=0)
        # Prepare header.
        header = ["image name"]
        num_landmarks = max_cols // 2
        for i in range(1, num_landmarks + 1):
            header.extend([f"x{i}", f"y{i}"])
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            for row in rows:
                # Pad row if necessary.
                if len(row) < len(header):
                    row.extend([""] * (len(header) - len(row)))
                writer.writerow(row)
        return csv_file
    except Exception as e:
        return f"Error converting XML to CSV: {e}"

eel.start('index.html', size=(1024, 768))