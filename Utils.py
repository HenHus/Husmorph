import sys
sys.setrecursionlimit(10**9)  # Set a higher limit

import os
import cv2
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import dlib
import optuna
from joblib import Parallel, delayed
from sklearn.model_selection import KFold
from xml.dom import minidom
import glob
import pandas as pd
import math
import shutil
import random

class LandmarkClass:
    def __init__(self, image_folder, landmarks):
        self.landmarks = landmarks
        self.image_folder = image_folder
        self.output_xml_path = self.create_output_xml_path(image_folder)
        self.landmarks_data = {}
        self.image_paths = sorted([os.path.join(image_folder, file_name) for file_name in os.listdir(image_folder) if file_name.lower().endswith(('.jpg', '.jpeg'))])
        self.current_image_index = 0
        self.current_image_name = ""

        # Start with the first image
        self.load_next_image()

    def create_output_xml_path(self, image_folder):
        folder_name = os.path.basename(os.path.normpath(image_folder))
        return os.path.join(os.getcwd(), f"{folder_name}.xml")

    def load_next_image(self):
        if self.current_image_index < len(self.image_paths):
            self.image_path = self.image_paths[self.current_image_index]

            # Read the image
            self.image = cv2.imread(self.image_path)

            # Initialize landmarks for the new image
            self.current_image_name = os.path.basename(self.image_path)
            if self.current_image_name not in self.landmarks_data:
                self.landmarks_data[self.current_image_name] = []

            # Display the image
            self.show_image()
        else:
            # Save the XML file after processing all images
            self.save_xml(self.output_xml_path)

    def show_image(self):
        # Create a figure and display the image
        self.fig, self.ax = plt.subplots(figsize=(12, 8))
        self.ax.imshow(cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB))

        # Connect the mouse click event to the callback function
        self.cid = self.fig.canvas.mpl_connect('button_press_event', self.on_click)

        # Connect the close event to the callback function
        self.fig.canvas.mpl_connect('close_event', self.on_close)

        # Connect the key press event to skip the image on Tab press
        self.kid = self.fig.canvas.mpl_connect('key_press_event', self.on_key_press)

        # Show the plot
        plt.show()

    def on_click(self, event):
        # Check if the click is within the image boundaries
        if event.inaxes != self.ax:
            return

        # Get the coordinates of the click
        x, y = int(event.xdata), int(event.ydata)

        # Get the image name
        image_name = os.path.basename(self.image_path)
        if image_name not in self.landmarks_data:
            self.landmarks_data[image_name] = []

        # Right-click to undo the last point
        if event.button == 3 and len(self.landmarks_data[image_name]) > 0:
            if len(self.landmarks_data[image_name]) == self.landmarks:
                self.fig.canvas.mpl_disconnect(self.cid)

            self.landmarks_data[image_name].pop()
            self.redraw_image()
            return

        # Left-click to add a point or move to the next image
        if event.button == 1:
            if len(self.landmarks_data[image_name]) < self.landmarks:
                self.landmarks_data[image_name].append((x, y))

                # Draw a blue point at the clicked location
                self.redraw_image()

            if len(self.landmarks_data[image_name]) == self.landmarks:
                # Allow one more click to move to the next image
                self.cid = self.fig.canvas.mpl_connect('button_press_event', self.load_next_on_click)

    def load_next_on_click(self, event):
        # Only move to the next image if the click is within the image boundaries
        if event.inaxes != self.ax:
            return

        # Any left-click after placing the required points will load the next image
        if event.button == 1:
            self.fig.canvas.mpl_disconnect(self.cid)
            self.fig.canvas.mpl_disconnect(self.kid)
            plt.close(self.fig)
            self.current_image_index += 1
            self.load_next_image()

    def on_key_press(self, event):
        # Skip the image if Tab is pressed
        if event.key == 'tab':
            self.fig.canvas.mpl_disconnect(self.cid)
            self.fig.canvas.mpl_disconnect(self.kid)
            plt.close(self.fig)
            # Remove the current image data if it exists
            if self.current_image_name in self.landmarks_data:
                del self.landmarks_data[self.current_image_name]
            self.current_image_index += 1
            self.load_next_image()

    def redraw_image(self):
        # Redraw the image with the current points
        self.ax.clear()
        self.ax.imshow(cv2.cvtColor(cv2.imread(self.image_path), cv2.COLOR_BGR2RGB))
        image_name = os.path.basename(self.image_path)
        for (x, y) in self.landmarks_data[image_name]:
            cv2.circle(self.image, (x, y), 8, (255, 0, 0), -1)
            self.ax.scatter(x, y, color='blue')
        plt.draw()

    def on_close(self, event):
        # Save the XML file when the window is closed
        self.save_xml(self.output_xml_path)

    def save_xml(self, xml_path):
        # Create XML structure
        root = ET.Element("dataset")

        name_elem = ET.SubElement(root, "name")
        comment_elem = ET.SubElement(root, "comment")

        images_elem = ET.SubElement(root, "images")

        for image_name, landmarks in self.landmarks_data.items():
            image_elem = ET.SubElement(images_elem, "image", file=os.path.relpath(os.path.join(self.image_folder, image_name), os.path.dirname(self.image_folder)))

            height, width, _ = self.image.shape
            box_elem = ET.SubElement(image_elem, "box", top='1', left='1', width=str(width-1), height=str(height-1))

            for idx, point in enumerate(landmarks):
                part_elem = ET.SubElement(box_elem, "part", name=str(idx), x=str(point[0]), y=str(point[1]))

        # Create an ElementTree object and write to XML file
        tree = ET.ElementTree(root)
        tree.write(xml_path, xml_declaration=True, encoding='utf-8')

        print(f"Landmarks saved to {xml_path}")


class CoordinateOverlay:
    def __init__(self, xml_file, images_directory=""):
        self.xml_file = xml_file
        self.images_directory = images_directory
        self.coordinates = self.read_coordinates()


    def read_coordinates(self):
        tree = ET.parse(self.xml_file)
        root = tree.getroot()
        coordinates = []

        for image in root.findall('.//image'):
            file_path = image.get('file')
            box = image.find('box')

            xmin = int(box.get('left'))
            ymin = int(box.get('top'))
            xmax = int(box.get('width')) + xmin
            ymax = int(box.get('height')) + ymin

            parts = []
            for part in box.findall('.//part'):
                x = int(part.get('x'))
                y = int(part.get('y'))
                parts.append((x, y))

            coordinates.append(((xmin, ymin, xmax, ymax), parts, file_path))

        return coordinates

    def overlay_coordinates(self, image_path, coordinates):
        # Read the image
        image = cv2.imread(image_path)

        if image is None:
            print(f"Error: Unable to read image at path: {image_path}")
            return

        # Original image size
        original_height, original_width = image.shape[:2]

        # Desired image size (adjust as needed)
        target_size = (1800, 1200)
        scale_width = target_size[0] / original_width
        scale_height = target_size[1] / original_height

        # Resize the image
        image = cv2.resize(image, target_size, interpolation=cv2.INTER_LINEAR)

        # Process and scale coordinates, then draw them on the image
        for coord_set in coordinates:
            xmin, ymin, xmax, ymax = coord_set[0]
            # Scale the coordinates
            xmin = int(xmin * scale_width)
            ymin = int(ymin * scale_height)
            xmax = int(xmax * scale_width)
            ymax = int(ymax * scale_height)

            # Draw a rectangle
            cv2.rectangle(image, (xmin, ymin), (xmax, ymax), (0, 255, 0), 4)  # Thick green rectangle box

            # Draw circles for each part
            for x, y in coord_set[1]:
                # Scale the part coordinates
                x = int(x * scale_width)
                y = int(y * scale_height)
                cv2.circle(image, (x, y), 5, (255, 0, 0), -1)  # Blue circles

        # Create a named window, move it, and resize it
        cv2.namedWindow('Image with Coordinates', cv2.WINDOW_NORMAL)
        cv2.moveWindow('Image with Coordinates', 0, 0)
        cv2.resizeWindow('Image with Coordinates', target_size[0], target_size[1])

        # Show the image
        cv2.imshow('Image with Coordinates', image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def process_images(self):
        for coord_set in self.coordinates:
            image_path = os.path.join(self.images_directory, coord_set[2])
            print(f"Attempting to read image at path: {image_path}")
            self.overlay_coordinates(image_path, [coord_set])

class StopOptimization(Exception):
    pass

class ShapePredictorTrainer:
    def __init__(self, xml_file, threads=6, k_folds=5):
        self.xml_file = xml_file
        self.k_folds = k_folds
        self.threads = threads
        self.images = self.parse_xml(xml_file)

    @staticmethod
    def parse_xml(xml_file):
        tree = ET.parse(xml_file)
        root = tree.getroot()
        images = root.findall('.//image')
        return images

    @staticmethod
    def save_to_xml(images, xml_file):
        root = ET.Element("dataset")
        name = ET.SubElement(root, "name")
        comment = ET.SubElement(root, "comment")
        images_elem = ET.SubElement(root, "images")
        for img in images:
            images_elem.append(img)
        tree = ET.ElementTree(root)
        tree.write(xml_file)

    def train_and_test(self, train_images, val_images, options):
        try:
            train_path = 'temp_train.xml'
            val_path = 'temp_val.xml'
            self.save_to_xml(train_images, train_path)
            self.save_to_xml(val_images, val_path)
            
            model_filename = 'temp_model.dat'
            dlib.train_shape_predictor(train_path, model_filename, options)
            training_deviation = dlib.test_shape_predictor(train_path, model_filename)
            print(f"Training error: {training_deviation}")

            testing_deviation = dlib.test_shape_predictor(val_path, model_filename)
            print(f"Validation error: {testing_deviation}")

            new_model_filename = model_filename.split(".")[0] + f"_{testing_deviation:.3f}.dat"
            os.rename(model_filename, new_model_filename)

            return testing_deviation, new_model_filename
        except RuntimeError as e:
            print(f"Error during training/testing: {e}")
            return float('inf'), None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return float('inf'), None

    def run_trial(self, trial):
        options = dlib.shape_predictor_training_options()
        options.nu = trial.suggest_float('nu', 0.06, 0.24)
        options.num_trees_per_cascade_level = trial.suggest_int('num_trees', 300, 1000, log=True)
        options.feature_pool_size = trial.suggest_int('feature_pool_size', 800, 2000, log=True)
        options.num_test_splits = trial.suggest_int('test_splits', 5, 30)
        options.tree_depth = trial.suggest_int('tree_depth', 3, 6)
        options.cascade_depth = trial.suggest_int('cascade_depth', 15, 40)
        options.oversampling_amount = trial.suggest_int('oversampling', 40, 180)
        options.lambda_param = trial.suggest_float('lambda_param', 0.04, 0.14)
        options.feature_pool_region_padding = trial.suggest_float('feature_pool_region_padding', -0.5, 1.5)
        options.num_threads = self.threads
        options.be_verbose = True

        kfold = KFold(n_splits=self.k_folds)
        val_errors = []
        temp_model_files = []
        best_model = ""

        for _, (train_index, val_index) in enumerate(kfold.split(self.images)):
            train_images = [self.images[i] for i in train_index]
            val_images = [self.images[i] for i in val_index]
            val_error, model_filename = self.train_and_test(train_images, val_images, options)
            val_errors.append(val_error)
            if model_filename:
                temp_model_files.append((val_error, model_filename))
        
        avg_val_error = sum(val_errors) / len(val_errors)
        if temp_model_files:
            best_model = min(temp_model_files, key=lambda x: x[0])
            best_model_filename = best_model[1]
            for val, model_filename in temp_model_files:
                if model_filename != best_model_filename:
                    if os.path.exists(model_filename):
                        os.remove(model_filename)
                else:
                    os.rename(model_filename, f'model_{val:.3f}_{avg_val_error}.dat')
        else:
            best_model_filename = None

        return avg_val_error, best_model_filename

    def parallel_optuna(self, n_trials):
        def objective(trial):
            avg_val_error, best_model_filename = self.run_trial(trial)
            return avg_val_error

        study = optuna.create_study(direction='minimize')
        best_model_filename = None
        best_avg_val_error = float('inf')

        try:
            study.optimize(objective, n_trials=n_trials)
            
            for trial in study.trials:
                if trial.value < best_avg_val_error:
                    if best_model_filename:
                        for file in glob.glob('*.dat'):
                            if f'{best_avg_val_error}' in file:
                                os.remove(file)
                                # print(f'Removed file: {file}')
                    best_avg_val_error = trial.value
                    best_model_filename = f'model_{best_avg_val_error:.3f}.dat'
                else:
                    for file in glob.glob('*.dat'):
                            if f'{trial.value}' in file:
                                os.remove(file)
                                # print(f'Removed file: {file}')

            if best_model_filename:
                print(f"Best model saved as {best_model_filename} with avg validation deviation: {best_avg_val_error}")
            
            optuna.visualization.plot_optimization_history(study).show()
            optuna.visualization.plot_slice(study).show()
            optuna.visualization.plot_param_importances(study).show()
        except optuna.exceptions.TrialPruned:
            pass  # Ignore pruned trials

        print("Best trial:")
        print(study.best_params)
        print("Best average validation deviation:")
        print(study.best_value)



def predict_landmarks(predictor_name, images, ignore=None):
    extensions = {'.jpg', '.JPG', '.jpeg', '.JPEG',}
    predictor = dlib.shape_predictor(predictor_name)
    root = ET.Element('dataset')
    root.append(ET.Element('name'))
    root.append(ET.Element('comment'))
    images_e = ET.Element('images')
    root.append(images_e)

    for f in glob.glob(os.path.join(images, '*')):
        ext = os.path.splitext(f)[1]
        if ext in extensions:
            img = cv2.imread(f)
            image_e = ET.Element('image')
            image_e.set('file', str(f))

            # Assuming a single face in the image covering the whole image
            e = dlib.rectangle(left=1, top=1, right=img.shape[1]-1, bottom=img.shape[0]-1)
            shape = predictor(img, e)
            box = ET.Element('box')
            box.set('top', '1')
            box.set('left', '1')
            box.set('width', str(img.shape[1]-1))
            box.set('height', str(img.shape[0]-1))

            for i in range(shape.num_parts):
                if ignore is None or i not in ignore:
                    part = ET.Element('part')
                    part.set('name', str(i))
                    part.set('x', str(shape.part(i).x))
                    part.set('y', str(shape.part(i).y))
                    box.append(part)

            box[:] = sorted(box, key=lambda child: int(child.get('name')))
            image_e.append(box)
            images_e.append(image_e)

    # Generate the output file name based on the image folder
    folder_name = os.path.basename(images)
    out_file = f"{folder_name}_output.xml"

    et = ET.ElementTree(root)
    xmlstr = minidom.parseString(ET.tostring(et.getroot())).toprettyxml(indent="   ")
    with open(out_file, "w") as f:
        f.write(xmlstr)


class XMLtoCSVConverter:
    def __init__(self, xml_file, csv_file="data.csv"):
        self.xml_file = xml_file
        self.csv_file = csv_file
        self.data = []
        self.max_parts = 0

    def parse_xml(self):
        tree = ET.parse(self.xml_file)
        self.root = tree.getroot()

    def extract_data(self):
        for image in self.root.findall('.//image'):
            file_path = image.get('file')
            image_name = file_path.split('/')[-1].split('.')[0]  # Extract the image name without extension

            row = [image_name]

            box = image.find('box')
            parts = box.findall('part')

            if len(parts) > self.max_parts:
                self.max_parts = len(parts)

            for part in parts:
                x = part.get('x')
                y = part.get('y')
                row.append(x)
                row.append(y)

            self.data.append(row)

    def create_dataframe(self):
        self.df = pd.DataFrame(self.data)

        # Generate column names
        columns = ['image']
        for i in range(1, self.max_parts + 1):
            columns.append(f'x{i}')
            columns.append(f'y{i}')

        # Rename the columns
        self.df.columns = columns

    def save_to_csv(self):
        self.df.to_csv(self.csv_file, index=False)

    def convert(self):
        self.parse_xml()
        self.extract_data()
        self.create_dataframe()
        self.save_to_csv()

    def calculate_metrics(self):
        def polygon_area(x, y):
            """Calculates the area of a polygon using the Shoelace formula."""
            return 0.5 * abs(sum(x[i] * y[i - 1] - y[i] * x[i - 1] for i in range(len(x))))

        def distance(x1, y1, x2, y2):
            """Calculates the Euclidean distance between two points."""
            return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

        def polygon_perimeter(x, y):
            """Calculates the perimeter (outline length) of a polygon."""
            return sum(distance(x[i], y[i], x[i - 1], y[i - 1]) for i in range(len(x)))

        areas = []
        perimeters = []
        lengths = []

        for index, row in self.df.iterrows():
            x_coords = [float(row[f'x{i}']) for i in range(1, self.max_parts + 1) if pd.notna(row[f'x{i}'])]
            y_coords = [float(row[f'y{i}']) for i in range(1, self.max_parts + 1) if pd.notna(row[f'y{i}'])]

            if len(x_coords) == 2:  # Only 2 points, calculate the length
                length = distance(x_coords[0], y_coords[0], x_coords[1], y_coords[1])
                areas.append(None)
                perimeters.append(None)
                lengths.append(length)
            elif len(x_coords) > 2:  # More than 2 points, calculate area and perimeter
                area = polygon_area(x_coords, y_coords)
                perimeter = polygon_perimeter(x_coords, y_coords)
                areas.append(area)
                perimeters.append(perimeter)
                lengths.append(None)
            else:
                areas.append(None)
                perimeters.append(None)
                lengths.append(None)

        self.df['area'] = areas
        self.df['perimeter'] = perimeters
        self.df['length'] = lengths

    def save_to_csv_with_metrics(self):
        self.df.to_csv("data_with_metrics.csv", index=False)


class DatasetSplitter:
    def __init__(self, input_folder: str, train_ratio: float = 0.8):
        self.input_folder = input_folder
        self.train_ratio = train_ratio
        self.train_folder = os.path.join(os.getcwd(), "train")
        self.test_folder = os.path.join(os.getcwd(), "test")

    def create_folders(self) -> None:
        os.makedirs(self.train_folder, exist_ok=True)
        os.makedirs(self.test_folder, exist_ok=True)

    def get_all_files(self) -> list:
        source_folder = os.path.join(os.getcwd(), self.input_folder)
        return [f for f in os.listdir(source_folder) if os.path.isfile(os.path.join(source_folder, f))]

    def split_files(self, all_files: list) -> tuple:
        random.shuffle(all_files)
        split_index = int(len(all_files) * self.train_ratio)
        return all_files[:split_index], all_files[split_index:]

    def copy_files(self, files: list, destination_folder: str) -> None:
        source_folder = os.path.join(os.getcwd(), self.input_folder)
        for file in files:
            shutil.copy2(os.path.join(source_folder, file), os.path.join(destination_folder, file))

    def split_dataset(self) -> None:
        self.create_folders()
        all_files = self.get_all_files()
        train_files, test_files = self.split_files(all_files)
        self.copy_files(train_files, self.train_folder)
        self.copy_files(test_files, self.test_folder)
