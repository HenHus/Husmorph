import sys
sys.setrecursionlimit(10**9)  # Set a higher limit

import os
import cv2
import xml.etree.ElementTree as ET
import dlib
import optuna
from sklearn.model_selection import KFold
from xml.dom import minidom
import glob

class ShapePredictorTrainer:
    def __init__(self, xml_file, base_path, threads=6, k_folds=5):
        self.xml_file = xml_file
        self.base_path = base_path
        self.k_folds = k_folds
        self.threads = threads
        self.images = self.parse_xml(xml_file)

        # Ensure the base path exists
        os.makedirs(base_path, exist_ok=True)

    @staticmethod
    def parse_xml(xml_file):
        tree = ET.parse(xml_file)
        root = tree.getroot()
        images = root.findall('.//image')
        return images

    def save_to_xml(self, images, xml_file):
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
            # Define paths relative to the base path
            train_path = os.path.join(self.base_path, 'temp_train.xml')
            val_path = os.path.join(self.base_path, 'temp_val.xml')
            model_filename = os.path.join(self.base_path, 'temp_model.dat')

            # Save the train and validation images
            self.save_to_xml(train_images, train_path)
            self.save_to_xml(val_images, val_path)

            # Train and test
            dlib.train_shape_predictor(train_path, model_filename, options)
            training_deviation = dlib.test_shape_predictor(train_path, model_filename)
            print(f"Training error: {training_deviation}")

            testing_deviation = dlib.test_shape_predictor(val_path, model_filename)
            print(f"Validation error: {testing_deviation}")

            # Rename model file to include testing deviation
            new_model_filename = os.path.join(
                self.base_path, f"model_{testing_deviation}.dat"
            )
            os.rename(model_filename, new_model_filename)

            return testing_deviation, new_model_filename
        except RuntimeError as e:
            print(f"Error during training/testing: {e}")
            return float('inf'), None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return float('inf'), None

    def run_trial(self, trial):
        '''
        Parameters to optimize:

        The study will look for the best parameters within the given ranges.
        
        '''

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
        options.be_verbose = False

        kfold = KFold(n_splits=self.k_folds)
        val_errors = []
        temp_model_files = []
        best_model = ""
        counter = 0

        for _, (train_index, val_index) in enumerate(kfold.split(self.images)):
            counter += 1
            train_images = [self.images[i] for i in train_index]
            val_images = [self.images[i] for i in val_index]
            print(f"Starting cross-validation training number {counter} out of 5")
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
                    os.rename(model_filename, os.path.join(self.base_path, f'model_{val}_{avg_val_error}.dat'))
        else:
            best_model_filename = None

        return avg_val_error, best_model_filename

    def parallel_optuna(self, n_trials):
        global trials_counter
        trials_counter = 0
        def objective(trial):
            global trials_counter
            trials_counter += 1
            print(f"Running trial number {trials_counter} out of {n_trials}")
            avg_val_error, best_model_filename = self.run_trial(trial)
            return avg_val_error

        study = optuna.create_study(direction='minimize')
        best_model_filename = None
        best_avg_val_error = float('inf')

        try:
            study.optimize(objective, n_trials=n_trials)

            for trial in study.trials:
                trial_model_files = glob.glob(os.path.join(self.base_path, '*.dat'))
                if trial.value < best_avg_val_error:
                    # Remove the previous best model if it exists
                    if best_model_filename:
                        for file in trial_model_files:
                            if f'{best_avg_val_error}' in file:
                                os.remove(file)

                    # Update the best model
                    best_avg_val_error = trial.value
                    best_model_filename = os.path.join(
                        self.base_path, f'model_{best_avg_val_error}.dat'
                    )
                else:
                    # Remove models from non-optimal trials
                    for file in trial_model_files:
                        if f'{trial.value}' in file:
                            os.remove(file)

            if best_model_filename:
                print(f"Best model saved as {best_model_filename} with avg validation deviation: {best_avg_val_error}")

            # Optional: Visualization (if necessary)
            # optuna.visualization.plot_optimization_history(study).show()
            # optuna.visualization.plot_slice(study).show()
            # optuna.visualization.plot_param_importances(study).show()

        except optuna.exceptions.TrialPruned:
            pass  # Ignore pruned trials

        print("Best trial:")
        print(study.best_params)
        print("Best average validation deviation:")
        print(study.best_value)



def predict_landmarks(predictor_name, images, output_folder, ignore=None):
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

    folder_name = os.path.basename(images)
    out_file = os.path.join(output_folder, f"{folder_name}_prediction.xml")

    et = ET.ElementTree(root)
    xmlstr = minidom.parseString(ET.tostring(et.getroot())).toprettyxml(indent="   ")
    with open(out_file, "w") as f:
        f.write(xmlstr)