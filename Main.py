import customtkinter as ctk
import model
import os
from tkinter import messagebox


xml = ""
xml_train = ""
dir_path = ""
ml_model = ""

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

def show_frame(frame):
    frame.tkraise()

def init_overlay():
    global xml
    e = model.init_overlay(xml)
    if e is not None:
        messagebox.showerror("Error", f"Make sure the XML file is correct.\n\n{e}")

def init_landmarks():
    global dir_path
    global combobox_var
    if dir_path != "" and combobox_var.get() != "Select amount of landmarks":
        e = model.init_landmarks(dir_path, int(combobox_var.get()))
        if e is not None:
            messagebox.showerror("Error", f"Make sure all images are '.JPG' or '.JPEG'.\nAlso make sure number of landmarks is set.\n\n{e}")
    else:
        messagebox.showerror("Error", "Select a folder, and the amount of landmarks to place.")

def init_training():
    global xml_train
    global threads
    global slider
    if xml_train != "" and threads.get().isdecimal():
        messagebox.showinfo("Training about to start!", model.getMessageBoxText1())
        model.init_training(xml_file=xml_train, threads=int(threads.get()), n_trials=int(slider.get()))

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

    # x.delete(1.0, "end")
    # x.insert("1.0", xml)

# def open_XML_test():
#     file_path = model.open_file()
#     global xml_test
#     xml_test = file_path
#     machinelearning_test_label.configure(text=xml_test)

    # x.delete(1.0, "end")
    # x.insert("1.0", xml) 

def ml_slider(value):
    slider_value_label.configure(text=f"Trials: {int(value)}")


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

home_label = ctk.CTkLabel(home_frame, text="Let's make\nmeasurements fun!", font=ctk.CTkFont(size=32, weight="bold"))
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

box_pictures = ctk.CTkTextbox(landmarks_frame, width=400, height=100, corner_radius=10)
box_pictures.grid(row=3, column=0, padx=(20, 0))

button_landmarks = ctk.CTkButton(landmarks_frame, text="Back", command=lambda: show_frame(home_frame), border_color="yellow", border_width=1, height=40, font=ctk.CTkFont(size=16), corner_radius=20)
button_landmarks.grid(row=6, column=0, pady=30, padx=(30, 0))

landmark_text2 = ctk.CTkLabel(landmarks_frame, text=model.getLandmarksPageText2(), font=ctk.CTkFont(size=13), wraplength=200)
landmark_text2.grid(row=3, column=2, rowspan=2)

combobox_var = ctk.StringVar(value="Select amount of landmarks")
landmark_combobox = ctk.CTkComboBox(master=landmarks_frame, state="readonly", values=[str(i) for i in range(1, 21)], variable=combobox_var, width=400, font=ctk.CTkFont(size=16))
landmark_combobox.grid(row=4, column=0, padx=(20, 0), sticky='n')

button_openMLmodel = ctk.CTkButton(landmarks_frame, text="Machine learning model\n(if you have one)", command=openMLmodel, height=70, width=200, border_color="yellow", border_width=1, font=ctk.CTkFont(size=16), corner_radius=20)
button_openMLmodel.grid(row=1, column=1, pady=0, sticky='s')

box_model = ctk.CTkLabel(landmarks_frame, width=400, height=60, corner_radius=10, text="")
box_model.grid(row=3, column=1, padx=(20), pady=10)

checkbox_var = ctk.BooleanVar()
checkbox = ctk.CTkCheckBox(landmarks_frame, text="Use the selected model", variable=checkbox_var)
checkbox.grid(row=3, column=1, padx=(20), pady=40, sticky='s')

landmark_init_landmark = ctk.CTkButton(landmarks_frame, text='Place landmarks', command=init_landmarks, border_width=1, height=70, border_color="yellow", width=180, font=ctk.CTkFont(size=16), corner_radius=20)
landmark_init_landmark.grid(row=6, column=2, padx=(0, 20), pady=30)


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

overlay_XML = ctk.CTkTextbox(overlay_frame, width=400, height=100, corner_radius=10, font=ctk.CTkFont(size=16))
overlay_XML.grid(row=2, column=0, padx=(80), columnspan=3)

overlay_init_overlay = ctk.CTkButton(overlay_frame, text='Look at landmarks', command=init_overlay, border_width=1, height=70, width=180, border_color="yellow", font=ctk.CTkFont(size=16), corner_radius=20)
overlay_init_overlay.grid(row=3, column=1, pady=10)

overlay_text1 = ctk.CTkLabel(overlay_frame, text="-Make sure the picture folder path corresponds to the XML file (see explaination on this if you are uncertain)\n\n-Press 'space' to scroll through the images", font=ctk.CTkFont(size=13), wraplength=200)
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

machinelearning_train_label = ctk.CTkLabel(machinelearning_frame, text='XML path will show here...', font=ctk.CTkFont(size=14, slant="italic"), wraplength=250)
machinelearning_train_label.grid(row=1, column=3, pady=0, columnspan=2)

# button_opentesting = ctk.CTkButton(machinelearning_frame, text="Select testing XML", command=open_XML_test, height=70, width=180, border_color="yellow", border_width=1, font=ctk.CTkFont(size=16), corner_radius=20)
# button_opentesting.grid(row=2, column=1, columnspan=3)

# machinelearning_test_label = ctk.CTkLabel(machinelearning_frame, text='Test path will show here...', font=ctk.CTkFont(size=14, slant="italic"), wraplength=250)
# machinelearning_test_label.grid(row=2, column=3, pady=0, columnspan=2)

# machinelearning_split = ctk.CTkButton(machinelearning_frame, text='Split dataset', command=init_splitting, height=70, border_width=1, border_color="yellow", font=ctk.CTkFont(size=16), corner_radius=20)
# machinelearning_split.grid(row=1, column=0, columnspan=2)

threads = ctk.StringVar(value="Threads to use")
ml_combobox = ctk.CTkComboBox(master=machinelearning_frame, state="readonly", values=[str(i) for i in range(1, 25)], variable=threads, width=400, font=ctk.CTkFont(size=14))
ml_combobox.grid(row=4, column=2)

slider = ctk.CTkSlider(machinelearning_frame, from_=10, to=100, number_of_steps=45, command=ml_slider)
slider.set(50)
slider.grid(row=6, column=2, sticky='n')

slider_value_label = ctk.CTkLabel(machinelearning_frame, text=f"Trials: {int(slider.get())}", font=ctk.CTkFont(size=12))
slider_value_label.grid(row=5, column=2, sticky='s')

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