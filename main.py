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
def select_file():
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
    file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
        None, "Select a file", "", "Supported Files (*.tps *.csv);;All Files (*)"
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

@eel.expose 
def xml_to_tps(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()

    entries = []
    for idx, img in enumerate(root.findall('.//image')):
        filename = os.path.basename(img.get('file'))
        box = img.find('box')
        w = int(box.get('width'))
        h = int(box.get('height'))
        parts = box.findall('part')
        coords = [(float(p.get('x')), float(p.get('y'))) for p in parts]
        entries.append((filename, w, h, coords))

    if not entries:
        raise ValueError("No <image> elements found in XML!")

    lm_count = len(entries[0][3])
    if any(len(coords) != lm_count for _, _, _, coords in entries):
        raise ValueError("Landmark count varies between images!")

    out_path = os.path.splitext(xml_path)[0] + '.tps'
    with open(out_path, 'w') as f:
        for idx, (filename, w, h, coords) in enumerate(entries):
            # 1) LM header
            f.write(f"LM={lm_count}\n")
            # 2) each landmark line with trailing dot
            for x, y in coords:
                f.write(f"{x:.0f}. {y:.0f}.\n")
            # 3) IMAGE, SIZE, ID
            f.write(f"IMAGE={filename}\n")
            f.write(f"SIZE={w} {h}\n")
            f.write(f"ID={idx}\n")
            # no blank line between blocks
    return out_path

@eel.expose
def tps_to_xml(tps_path):
    # read all non-empty lines
    with open(tps_path) as f:
        lines = [l.strip() for l in f if l.strip()]

    entries = []
    i = 0
    while i < len(lines):
        # LM count
        if not lines[i].startswith("LM="):
            raise ValueError(f"Expected 'LM=' at line {i+1}")
        lm_count = int(lines[i].split('=',1)[1])
        i += 1

        # coords
        coords = []
        for _ in range(lm_count):
            x_str, y_str = lines[i].split()
            x = float(x_str.rstrip('.'))
            y = float(y_str.rstrip('.'))
            coords.append((x, y))
            i += 1

        # IMAGE
        if not lines[i].startswith("IMAGE="):
            raise ValueError(f"Expected 'IMAGE=' at line {i+1}")
        filename = lines[i].split('=',1)[1]
        i += 1

        # SIZE
        if not lines[i].startswith("SIZE="):
            raise ValueError(f"Expected 'SIZE=' at line {i+1}")
        w, h = map(int, lines[i].split('=',1)[1].split())
        i += 1

        # ID (we ignore the value but sanity‐check)
        if not lines[i].startswith("ID="):
            raise ValueError(f"Expected 'ID=' at line {i+1}")
        _ = int(lines[i].split('=',1)[1])
        i += 1

        entries.append((filename, w, h, coords))

    # build XML
    dataset = ET.Element('dataset')
    ET.SubElement(dataset, 'name').text    = 'Converted from TPS'
    images_el = ET.SubElement(dataset, 'images')

    for filename, w, h, coords in entries:
        img_el = ET.SubElement(images_el, 'image', {'file': filename})
        box_el = ET.SubElement(img_el, 'box', {
            'top':    '0',
            'left':   '0',
            'width':  str(w),
            'height': str(h)
        })
        for idx, (x, y) in enumerate(coords):
            ET.SubElement(box_el, 'part', {
                'name': str(idx),
                'x':    str(int(x)),
                'y':    str(int(y))
            })

    out_path = os.path.splitext(tps_path)[0] + '.xml'
    ET.ElementTree(dataset).write(out_path,
                                  encoding='utf-8',
                                  xml_declaration=True)
    return out_path

eel.start('index.html', size=(1024, 768))