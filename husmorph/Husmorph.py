import customtkinter as ctk
import model
import os
import time
import threading
from tkinter import messagebox, Toplevel


xml = ""
xml_train = ""
dir_path = ""
ml_model = ""
save_path = ""

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tip_window:
            return
        # Get the widget's position on the screen
        x = self.widget.winfo_rootx() + 150
        y = self.widget.winfo_rooty() + 20
        self.tip_window = tw = Toplevel(self.widget)
        tw.wm_overrideredirect(True)  # No window decorations
        tw.wm_geometry(f"+{x}+{y}")  # Position the tooltip
        tw.configure(bg="black")  # Tooltip background color

        # Create the tooltip label using CTkLabel
        label = ctk.CTkLabel(tw, text=self.text, fg_color="black", text_color="white",
                             corner_radius=5, padx=10, pady=5, wraplength=400)
        label.pack(ipadx=1)

    def hide_tip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None

def show_frame(frame):
    frame.tkraise()

def init_overlay():
    global xml
    e =  None
    e = model.init_overlay(xml)
    if e is not None:
        messagebox.showerror("Error", f"Make sure the XML file is correct.\n\n{e}")

def init_landmarks():
    global dir_path
    global combobox_var

    e = None
    if dir_path != "" and combobox_var.get() != "Select amount of landmarks" and not checkbox_var.get():
        e = model.init_landmarks(dir_path, int(combobox_var.get()))
        
    
    elif dir_path != "" and checkbox_var.get() and ml_model != "":
        e = model.predict_new_landmarks(ml_model, dir_path)

    else:
        messagebox.showerror("Error", "Select a folder, and the amount of landmarks to place.")
    
    if e is not None:
            messagebox.showerror("Error", f"Make sure all images are '.JPG' or '.JPEG'.\nAlso make sure number of landmarks is set.\n\n{e}")


def init_training():
    global root
    global xml_train
    global slider_threads
    global slider_trials
    if xml_train.lower().endswith(".xml") and save_path != "":

        def start():
            model.init_training(xml_file=xml_train, path=save_path, threads=int(slider_threads.get()), n_trials=int(slider_trials.get()))

        # messagebox.showinfo("Training about to start!", model.getMessageBoxText1())

        if messagebox.showinfo("Training", model.getMessageBoxText1()) == "ok":
            root.after(1000, start)
    else:
        messagebox.showerror("Error", "Make sure dataset and save destination is set.")
    
        

def init_splitting():
    folder = model.open_folder()
    try:
        model.init_splitting(folder)
        messagebox.showinfo("Success", "The dataset has been split.")
    except Exception as e:
        messagebox.showerror("Error", f"Make sure the folder contains images.\n\n{e}")

def init_export():
    global xml
    e = model.init_export(xml)
    if e is not None:
        messagebox.showerror("Error", f"Make sure the XML file is correct.\n\n{e}")

def openpicturefolder():
    global dir_path
    folder = model.open_folder()
    dir_path = folder

    box_pictures.delete(1.0, "end")
    box_pictures.insert(1.0, dir_path)

def openMLmodel():
    global ml_model
    model_1 = model.open_file()
    filename = os.path.basename(model_1)

    if model_1.endswith(".dat"):
        ml_model = model_1

        box_model.configure(text=filename)
    else:
        messagebox.showerror("Error", "The file must be a '.dat' file.")


def open_XML():
    file_path = model.open_file()
    global xml
    xml = file_path

    overlay_XML.delete(1.0, "end")
    overlay_XML.insert("1.0", xml)

    export_XML.delete(1.0, "end")
    export_XML.insert("1.0", xml)

def open_XML_train():
    file_path = model.open_file()
    global xml_train
    xml_train = file_path
    machinelearning_train_label.configure(text=xml_train)

def save_destination():
    global save_path
    save_path = model.open_folder()

    machinelearning_save_label.configure(text=save_path)


def ml_trials(value):
    slider_trials_label.configure(text=f"Trials: {int(value)}")

def ml_threads(value):
    slider_threads_label.configure(text=f"Threads: {int(value)}")

# GUI
root = ctk.CTk()
root.geometry("800x600")
root.resizable(False, False)
root.title("Husmorph")

root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

# HOME PAGE
home_frame = ctk.CTkFrame(root)
home_frame.grid(row=0, column=0, sticky='nsew')

home_frame.grid_columnconfigure(0, weight=1, uniform="fixed")
home_frame.grid_columnconfigure(1, weight=1, uniform="fixed")
home_frame.grid_columnconfigure(2, weight=1, uniform="fixed")
home_frame.grid_rowconfigure(0, weight=1)
home_frame.grid_rowconfigure(1, weight=1)
home_frame.grid_rowconfigure(2, weight=1)
home_frame.grid_rowconfigure(3, weight=1)
home_frame.grid_rowconfigure(4, weight=1)
home_frame.grid_rowconfigure(5, weight=1)

home_label = ctk.CTkLabel(home_frame, text="", font=ctk.CTkFont(size=32, weight="bold"))
home_label.grid(row=0, column=0, sticky='nsew', pady=(0, 10), columnspan=3)

home_to_landmarks = ctk.CTkButton(home_frame, text='Set landmarks\non images', command=lambda: show_frame(landmarks_frame), border_width=1, height=70, border_color="yellow", width=180, font=ctk.CTkFont(size=16), corner_radius=20)
home_to_landmarks.grid(row=1, column=1, sticky='s', pady=10)

home_to_overlay = ctk.CTkButton(home_frame, text='Visualize landmarks', command=lambda: show_frame(overlay_frame), border_width=1, height=70, border_color="yellow", width=180, font=ctk.CTkFont(size=16), corner_radius=20)
home_to_overlay.grid(row=2, column=1, sticky='n', pady=10)

text_label1 = ctk.CTkLabel(home_frame, text=model.getHomePageText1(), font=ctk.CTkFont(size=14), wraplength=220)
text_label1.grid(row=0, column=0, padx=(20, 0), rowspan=6)

home_to_machinelearning = ctk.CTkButton(home_frame, text='Machine learning', command=lambda: show_frame(machinelearning_frame), border_width=1, height=70, border_color="yellow", width=180, font=ctk.CTkFont(size=16), corner_radius=20)
home_to_machinelearning.grid(row=3, column=1, sticky='s', pady=10)

home_to_export = ctk.CTkButton(home_frame, text='Export data', command=lambda: show_frame(export_frame), border_width=1, height=70, border_color="yellow", width=180, font=ctk.CTkFont(size=16), corner_radius=20)
home_to_export.grid(row=4, column=1, sticky='n', pady=10)

# SET LANDMARKS
landmarks_frame = ctk.CTkFrame(root)
landmarks_frame.grid(row=0, column=0, sticky='nsew')

landmarks_frame.grid_columnconfigure(0, weight=1, uniform="fixed")
landmarks_frame.grid_columnconfigure(1, weight=1, uniform="fixed")
landmarks_frame.grid_columnconfigure(2, weight=1, uniform="fixed")
landmarks_frame.grid_rowconfigure(0, weight=1)
landmarks_frame.grid_rowconfigure(1, weight=1)
landmarks_frame.grid_rowconfigure(2, weight=1)
landmarks_frame.grid_rowconfigure(3, weight=1)
landmarks_frame.grid_rowconfigure(4, weight=1)
landmarks_frame.grid_rowconfigure(5, weight=1)
landmarks_frame.grid_rowconfigure(6, weight=1)

landmark_header = ctk.CTkLabel(landmarks_frame, text=model.getLandmarksPageText1(), font=ctk.CTkFont(size=20), wraplength=500)
landmark_header.grid(row=0, column=0, pady=(10, 0), padx=20, columnspan=3)

button_openpictures = ctk.CTkButton(landmarks_frame, text="Choose pictures (folder)", command=openpicturefolder, height=70, width=200, border_color="yellow", border_width=1, font=ctk.CTkFont(size=16), corner_radius=20)
button_openpictures.grid(row=1, column=0, pady=0, sticky='s')
ToolTip(button_openpictures, "Choose the picture folder that you want to process. Must be JPEG images.")

box_pictures = ctk.CTkTextbox(landmarks_frame, width=400, height=100, corner_radius=10)
box_pictures.grid(row=3, column=0, padx=(20, 0))

button_landmarks = ctk.CTkButton(landmarks_frame, text="Back", command=lambda: show_frame(home_frame), border_color="yellow", border_width=1, height=40, font=ctk.CTkFont(size=16), corner_radius=20)
button_landmarks.grid(row=6, column=0, pady=30, padx=(30, 0))

landmark_text2 = ctk.CTkLabel(landmarks_frame, text=model.getLandmarksPageText2(), font=ctk.CTkFont(size=13), wraplength=200)
landmark_text2.grid(row=3, column=2, rowspan=2)

combobox_var = ctk.StringVar(value="Select amount of landmarks")
landmark_combobox = ctk.CTkComboBox(master=landmarks_frame, state="readonly", values=[str(i) for i in range(1, 21)], variable=combobox_var, width=400, font=ctk.CTkFont(size=16))
landmark_combobox.grid(row=4, column=0, padx=(20, 0), sticky='n')
ToolTip(landmark_combobox, "Select how many landmarks you want to place per image")

button_openMLmodel = ctk.CTkButton(landmarks_frame, text="Machine learning model", command=openMLmodel, height=70, width=200, border_color="yellow", border_width=1, font=ctk.CTkFont(size=16), corner_radius=20)
button_openMLmodel.grid(row=1, column=1, pady=0, sticky='s')
ToolTip(button_openMLmodel, "This is for predicting landmarks. You chould only upload something here if you already have done the machine learning part.")

box_model = ctk.CTkLabel(landmarks_frame, width=400, height=60, corner_radius=10, text="")
box_model.grid(row=3, column=1, padx=(20), pady=10)

checkbox_var = ctk.BooleanVar()
checkbox = ctk.CTkCheckBox(landmarks_frame, text="Use the selected model", variable=checkbox_var)
checkbox.grid(row=3, column=1, padx=(20), pady=40, sticky='s')

landmark_init_landmark = ctk.CTkButton(landmarks_frame, text='Place landmarks', command=init_landmarks, border_width=1, height=70, border_color="yellow", width=180, font=ctk.CTkFont(size=16), corner_radius=20)
landmark_init_landmark.grid(row=6, column=2, padx=(0, 20), pady=30)
ToolTip(landmark_init_landmark, "The XML file will be generated in the same folder that contains your image folder\n\nWARNING: The XML file will have the same name as your image folder, so move other XML files if they have the same name as the uploaded folder")


# OVERLAY
overlay_frame = ctk.CTkFrame(root)
overlay_frame.grid(row=0, column=0, sticky='nsew')

overlay_frame.grid_columnconfigure(0, weight=1, uniform="fixed")
overlay_frame.grid_columnconfigure(1, weight=1, uniform="fixed")
overlay_frame.grid_columnconfigure(2, weight=1, uniform="fixed")
overlay_frame.grid_rowconfigure(0, weight=1)
overlay_frame.grid_rowconfigure(1, weight=1)
overlay_frame.grid_rowconfigure(2, weight=1)
overlay_frame.grid_rowconfigure(3, weight=1)
overlay_frame.grid_rowconfigure(4, weight=1)

overlay_label = ctk.CTkLabel(overlay_frame, text='Overlay landmarks\non images', font=ctk.CTkFont(size=30, weight="bold"))
overlay_label.grid(row=0, column=0, pady=10, columnspan=3)

overlay_open_xml = ctk.CTkButton(overlay_frame, text='Choose XML file', command=open_XML, border_width=1, height=70, width=180, border_color="yellow", font=ctk.CTkFont(size=16), corner_radius=20)
overlay_open_xml.grid(row=1, column=1, pady=10)
ToolTip(overlay_open_xml, "It's important that the image folder containing you images is not moved. This is because the XML file contains a path to this folder. Feel free to double check that the path is correct by manually opening the XML file on your computer.")

overlay_XML = ctk.CTkTextbox(overlay_frame, width=400, height=100, corner_radius=10, font=ctk.CTkFont(size=16))
overlay_XML.grid(row=2, column=0, padx=(80), columnspan=3)

overlay_init_overlay = ctk.CTkButton(overlay_frame, text='Look at landmarks', command=init_overlay, border_width=1, height=70, width=180, border_color="yellow", font=ctk.CTkFont(size=16), corner_radius=20)
overlay_init_overlay.grid(row=3, column=1, pady=10)
ToolTip(overlay_init_overlay, "Press 'space' to go through the images. Press 'c' to cancel.")

overlay_text1 = ctk.CTkLabel(overlay_frame, text="-Instructions:\n\n-Make sure the picture folder path corresponds to the XML file (see explaination on this if you are uncertain)\n\n-Press 'space' to scroll through the images\n\n-Press 'c' to cancel", font=ctk.CTkFont(size=13), wraplength=200)
overlay_text1.grid(row=3, column=2, rowspan=2)

overlay_back = ctk.CTkButton(overlay_frame, text='Back', command=lambda: show_frame(home_frame), border_width=1, border_color="yellow", font=ctk.CTkFont(size=16), height=40, corner_radius=20)
overlay_back.grid(row=4, column=0, pady=30, padx=(30, 0))


# MACHINE LEARNING
machinelearning_frame = ctk.CTkFrame(root)
machinelearning_frame.grid(row=0, column=0, sticky='nsew')

machinelearning_frame.grid_columnconfigure(0, weight=1, uniform="fixed")
machinelearning_frame.grid_columnconfigure(1, weight=1, uniform="fixed")
machinelearning_frame.grid_columnconfigure(2, weight=1, uniform="fixed")
machinelearning_frame.grid_columnconfigure(3, weight=1, uniform="fixed")
machinelearning_frame.grid_columnconfigure(4, weight=1, uniform="fixed")
machinelearning_frame.grid_rowconfigure(0, weight=1)
machinelearning_frame.grid_rowconfigure(1, weight=1)
machinelearning_frame.grid_rowconfigure(2, weight=1)
machinelearning_frame.grid_rowconfigure(3, weight=1)
machinelearning_frame.grid_rowconfigure(4, weight=1)
machinelearning_frame.grid_rowconfigure(5, weight=1)
machinelearning_frame.grid_rowconfigure(6, weight=1)
machinelearning_frame.grid_rowconfigure(7, weight=1)

machinelearning_label = ctk.CTkLabel(machinelearning_frame, text='Machine learning', font=ctk.CTkFont(size=30, weight="bold"))
machinelearning_label.grid(row=0, column=1, pady=10, columnspan=3)


button_opentraining = ctk.CTkButton(machinelearning_frame, text="Select XML file", command=open_XML_train, height=70, width=180, border_color="yellow", border_width=1, font=ctk.CTkFont(size=16), corner_radius=20)
button_opentraining.grid(row=1, column=1, columnspan=3)
ToolTip(overlay_open_xml, "It's important that the image folder containing your images is not moved. This is because the XML file contains a path to this folder. Feel free to double check that the path is correct by manually opening the XML file on your computer.")


machinelearning_train_label = ctk.CTkLabel(machinelearning_frame, text='XML path will show here...', font=ctk.CTkFont(size=14, slant="italic"), wraplength=250)
machinelearning_train_label.grid(row=1, column=3, pady=0, columnspan=2)

button_select_destination = ctk.CTkButton(machinelearning_frame, text="Select save destination", command=save_destination, height=70, width=180, border_color="yellow", border_width=1, font=ctk.CTkFont(size=16), corner_radius=20)
button_select_destination.grid(row=2, column=1, columnspan=3)
ToolTip(button_select_destination, "Ideally make a new folder for this, since many files are going to be created.")


machinelearning_save_label = ctk.CTkLabel(machinelearning_frame, text='Destination path will show here...', font=ctk.CTkFont(size=14, slant="italic"), wraplength=250)
machinelearning_save_label.grid(row=2, column=3, pady=0, columnspan=2)

threads_recommended = int(os.cpu_count() * 0.8)
machinelearning_threads_label = ctk.CTkLabel(machinelearning_frame, text=f'Based on your computer, we recommend you using {threads_recommended} threads (80% of total capacity).', font=ctk.CTkFont(size=14), wraplength=250)
machinelearning_threads_label.grid(row=5, column=0, pady=0, columnspan=2, sticky='s')

slider_threads = ctk.CTkSlider(machinelearning_frame, from_=1, to=30, number_of_steps=30, command=ml_threads)
slider_threads.set(threads_recommended)
slider_threads.grid(row=6, column=2, sticky='n')

slider_threads_label = ctk.CTkLabel(machinelearning_frame, text=f"Threads: {int(slider_threads.get())}", font=ctk.CTkFont(size=12))
slider_threads_label.grid(row=5, column=2, sticky='s')

slider_trials = ctk.CTkSlider(machinelearning_frame, from_=20, to=200, number_of_steps=36, command=ml_trials)
slider_trials.set(100)
slider_trials.grid(row=6, column=3, sticky='n', columnspan=2)

slider_trials_label = ctk.CTkLabel(machinelearning_frame, text=f"Trials: {int(slider_trials.get())}", font=ctk.CTkFont(size=12))
slider_trials_label.grid(row=5, column=3, sticky='s', columnspan=2)

machinelearning_init = ctk.CTkButton(machinelearning_frame, text='Start training', command=init_training, border_width=1, border_color="yellow", height=70, width=180, font=ctk.CTkFont(size=16), corner_radius=20)
machinelearning_init.grid(row=7, column=3, pady=40, columnspan=2)

machinelearning_back = ctk.CTkButton(machinelearning_frame, text='Back', command=lambda: show_frame(home_frame), height=40, border_width=1, border_color="yellow", font=ctk.CTkFont(size=16), corner_radius=20)
machinelearning_back.grid(row=7, column=0, pady=20, padx=(50, 0))


# EXPORT
export_frame = ctk.CTkFrame(root)
export_frame.grid(row=0, column=0, sticky='nsew')

export_frame.grid_columnconfigure(0, weight=1, uniform="fixed")
export_frame.grid_columnconfigure(1, weight=1, uniform="fixed")
export_frame.grid_columnconfigure(2, weight=1, uniform="fixed")
export_frame.grid_rowconfigure(0, weight=1)
export_frame.grid_rowconfigure(1, weight=1)
export_frame.grid_rowconfigure(2, weight=1)
export_frame.grid_rowconfigure(3, weight=1)
export_frame.grid_rowconfigure(4, weight=1)

export_label = ctk.CTkLabel(export_frame, text='Export data', font=ctk.CTkFont(size=30, weight="bold"))
export_label.grid(row=0, column=1, pady=10)

export_open_xml = ctk.CTkButton(export_frame, text='Choose XML file', command=open_XML, border_width=1, height=70, width=180, border_color="yellow", font=ctk.CTkFont(size=16), corner_radius=20)
export_open_xml.grid(row=1, column=1, pady=10)

export_XML = ctk.CTkTextbox(export_frame, width=400, height=100, corner_radius=10, font=ctk.CTkFont(size=16))
export_XML.grid(row=2, column=0, padx=(80), columnspan=3)

export_init_export = ctk.CTkButton(export_frame, text='Convert', command=init_export, border_width=1, height=70, width=180, border_color="yellow", font=ctk.CTkFont(size=16), corner_radius=20)
export_init_export.grid(row=3, column=1, pady=10)

export_back = ctk.CTkButton(export_frame, text='Back', command=lambda: show_frame(home_frame), height=40, border_width=1, border_color="yellow", font=ctk.CTkFont(size=16), corner_radius=20)
export_back.grid(row=4, column=0, pady=40, padx=(50, 0))



show_frame(home_frame)

root.mainloop()