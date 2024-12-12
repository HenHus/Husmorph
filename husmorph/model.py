from tkinter import filedialog
from Utils import CoordinateOverlay, LandmarkClass, ShapePredictorTrainer, predict_landmarks, XMLtoCSVConverter

def getHomePageText1():
    return """

    Welcome to the image analysis tool!

    
    Start with setting landmarks, or look at already set landmarks.
    

    
    

    For larger datasets, you can train a model to predict landmarks on images here:

    
    You can also export landmarks from XML to CSV for further analysis."""

def getLandmarksPageText1():
    return "Select a folder with images to set landmarks on.\n\nRemember that the folder can only contain '.JPG' or '.JPEG' images."

def getLandmarksPageText2():
    return "-Press 'Left mouse button' to set a landmark on the current image\n\n-Press 'Right mouse button' to remove a landmark on the current image\n\n-Left click anywhere on the image once all landmarks are placed to go to next image\n\n-Press 'Tab' to skip current image and go straight to the next one"

def getMLText1():
    return "Here, you can train a model to predict landmarks on images.\n\n\nStart by selecting a training and testing dataset."

def getMessageBoxText1():
    return "It seems like the initializing went well, and the training is about to start. This will most likely crash the application while training.\nThe training progress can be followed in the terminal. Good luck!\nTo stop manually, press 'control' + 'c' in the terminal window."

def open_file():
    file = filedialog.askopenfilename()
    return file

def open_folder():
    folder = filedialog.askdirectory()
    return folder

def init_overlay(file):
    try:
        overlay = CoordinateOverlay(file)
        overlay.process_images()
    except Exception as e:
        return e

def init_landmarks(image_folder, landmarks):
    try:
        landmarks = LandmarkClass(image_folder, landmarks)
    except Exception as e:
        return e

def predict_new_landmarks(ml_model, images):
    try:
        predict_landmarks(ml_model, images)
    except Exception as e:
        return e

def init_training(xml_file, path, threads, n_trials):
    try:
        trainer = ShapePredictorTrainer(xml_file=xml_file, base_path=path, threads=threads)
        trainer.parallel_optuna(n_trials)
    except Exception as e:
        print(e)

def init_export(xml):
    try:
        converter = XMLtoCSVConverter(xml)
        converter.convert()
        converter.calculate_metrics()
        converter.save_to_csv_with_metrics()
    except Exception as e:
        return e