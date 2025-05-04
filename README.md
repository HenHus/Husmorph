# HUSMORPH v2.0

## Major updates in the new 2.0 version!

HUSMORPH is a graphical user interface (GUI) designed for landmark placement on images. It supports both manual placement and automated machine learning-based predictions. This versatile tool can be used right out of the box or by running the scripts provided in this repository for more customized workflows.

## Important!

The startup time may long. Be patient, it can take up to 1 min before the software is running.

## Features
- Intuitive interface for manual landmark placement on images.
- Machine learning functionality to predict landmarks automatically.
- Support for data visualization and exporting results to commonly used formats.
- Platform compatibility with Windows and macOS.

---

## Downloads

You can download the application using the links below. The files are hosted on my personal Google Drive for easy access. The files were too big for GitHub.

### Windows
- **File:** Downloadable ZIP archive.
- **Instructions:** Extract the archive, and run the `Husmorph` executable from the folder.



**[Download here (v2.0)](https://drive.google.com/file/d/1z1Fpo48Ta9zeB7hWuZQfbJTmoHQoKKzR/view?usp=sharing)**

**[Download here (v1)](https://drive.google.com/file/d/1IC0XUQLshbcBHlt7jbdVgdt0UKDWJ3I_/view?usp=drivesdk)**

---

### macOS with silicon chip (M1, M2, M3, M4 models)
- **File:** DMG installer.
- **Instructions:** Download the file, drag the application to your `Applications` folder, and launch `Husmorph` from there.

   > **Note:** To open the software for the first time, Mac-users may have to go to System settings -> Privacy & Security and press 'Open anyways' for Husmorph. If the computer needs you to verify even more things, approve it. I promise that the software is safe to use.



**[Download here (v2.1)](https://drive.google.com/file/d/1_kKzySsoFYihC22DNxA3dbxRAAR8EXI2/view?usp=sharing)**

**[Download here (v2.0)](https://drive.google.com/file/d/1_64J_vCBjXSUNO5vsO_IeK7kIzJYTMxl/view?usp=share_link)**

**[Download here (v1)](https://drive.google.com/file/d/1Weko3YBif2mEi5Uz-tU1BdMo0vcGYBuT/view?usp=share_link)**

---

## What's new?

### Version 2.1 (MacOS only right now)
- Placed landmarks can now be dragged around, both in regular window and in zoomed window
- Added exporting to tps format
- Added import of tps format (has to include information about image SIZE)
- Added the scale bar scripts (python, [Anaconda](https://www.anaconda.com/download/success) recommended). These will have to be edited to fit your dataset/scale bar.


### Version 2.0
- Changed graphical technology. The application is now running in a web-based format using chrome
- Everything is now in a single page, in different sections
- Landmark annotation and viewing is merged into one new section:
   - The images doesn't appear in a new window anymore
   - You can iterate back and forth in your image folder
   - It's possible to upload existing landmark data along with the images, edit the data, and save it back to the same file
   - Added hotkeys:
      - Hold **W** to zoom in on a spesific area
      - Press **A** to go to previous image
      - Press **D** to go to next image
      - Press **S** to save the landmark data
   - Landmarks are numbered
   - It is now possible to change number of landmarks placed on each individual image
- Improved user experience

---

# Using the Tool (v2.0)

## Landmarking - view and placement

### Setup
1. **Image Requirements:**
   - Images can have any resolution
   - For machine learning purposes, ensure the resolution is 2MP or lower (e.g., < 1920x1080).
2. Upload the image folder you like to use. Once selected, the images will appear beneath in the same section.
3. Pick a save destination for your XML file, which will contain the landmark data.
4. Specify the number of landmarks to place on each image.

### Usage - landmarking

 **Controls:**
  - **Left-click** to place a landmark.
  - HOLD **Left-click** on a landmark to move it around.
  - **Right-click** to delete the last placed landmark.
  - Press '**W**' to zoom in on an area to precisely place a landmark.
  - Once all landmarks are placed for an image, press '**D**' to proceed to the next image, '**A**' to go back to the previous image, or use the buttons underneath the image.
  - Press '**S**' to save the landmarks to the chosen location, or use the '**Save XML**' button.

---

### Usage - viewing and editing

   XML file containing data to the uploaded can at any time be uploaded using the '**Upload existing XML**' button. Then, previously annotated landmarks can be viewed and edited in the same way with the same controls as above, and saved to the same uploaded XML file.

## Machine Learning Training

Husmorph includes a built-in machine learning pipeline to predict landmarks automatically. To use this functionality, you first need to train the model on your dataset, enabling it to make accurate predictions for landmark placement in future images.

#### Training a Model
1. Select an XML file containing landmark data for training.
2. Set the number of *threads* your computer should use.
   - **General recommendation:** Save 1–2 threads for system processes. For a typical laptop, use ~5 threads. Check your system for amount for cores, and use ~80% of these.
3. Specify the number of *trials* for parameter optimization.
   - More trials increase the likelihood of finding the optimal model but also increase training time. We recommend between 50-100 trials.

   > **Analogy:** Think of a rifle shooter improving over time. Each trial fine-tunes the shooter’s accuracy, increasing the likelihood of hitting the target center.
4. Choose the folder where the trained model will be saved. During training, this folder will temporarily store intermediate files. The best model from each trial (based on cross-validation) is saved in this folder. The filenames indicate the mean deviation from cross-validation, allowing to compare trials fairly and monitor performance.

**Note**: the software becomes unresponsive once training has started.

**Note**: follow in the TERMINAL window to follow the training!

## Predict landmarks

Once training is complete, the model can be used for prediction by uploading a image folder, and the model under this section. The results can be displayed in the '**Landmarking - view and placement**' section, by uploading the same image folder there, along with the XML file containing the predicted data.

---

### Exporting Data

Currently, we only support exporting landmark data from XML to CSV format. Support for additional formats is planned for future updates.

---

## Notes and Best Practices
- Always use consistent image resolutions within a dataset, especially when using machine learning models.
- Keep the original image folder intact if you plan to visualize landmarks later.
- For optimal machine learning performance, balance the number of trials and threads based on your system's capabilities. For good performance, we recommend at least 150 images.

---

# Using the Tool (v1)

### Setting Landmarks on Images

1. Click **Set landmarks on images** to open the landmark placement window.
2. **Image Requirements:**
   - Images can have any resolution, but all images in the folder must share the same resolution.
   - For machine learning purposes, ensure the resolution is 2,000,000 pixels or lower (e.g., around 1920x1080).
3. Select the folder containing your images. The selected folder path will be displayed.
4. Specify the number of landmarks to place on each image.
5. Ensure the "Use the selected model" option is **unchecked**, then click **Place landmarks**.

#### Landmark Placement Workflow
- A new window will open, displaying each image in your selected folder one at a time.
- **Controls:**
  1. **Left-click** to place a landmark.
  2. **Right-click** to delete the last placed landmark.
  3. Once all landmarks are placed for an image, **left-click** to proceed to the next image.
  4. To skip an image, press **Tab**.
- After processing all images, the window will close automatically, and the data will be saved to an XML file in the same parent folder as your images.

---

### Visualizing Landmarks

- Open the XML file containing the landmark data you want to view.
- Ensure the original image folder remains in its original location (the images must be accessible for visualization). The XML file references the images by their original path, so if the images are moved, the landmarks cannot be overlaid correctly.
- Use **Spacebar** to navigate through the images while viewing their landmarks.
- Press `c` to cancel, and go back to the program.
---

### Machine Learning

Husmorph includes a built-in machine learning pipeline to predict landmarks automatically. To use this functionality, you first need to train the model on your dataset, enabling it to make accurate predictions for landmark placement in future images.

#### Training a Model
1. Select an XML file containing landmark data for training.
2. Set the number of *threads* your computer should use.
   - **Note:** The program auto-detects your computer's capabilities, and estimates how many threads you should use
   - **General recommendation:** Save 1–2 threads for system processes. For a typical laptop, use ~5 threads.
3. Specify the number of *trials* for parameter optimization.
   - More trials increase the likelihood of finding the optimal model but also increase training time.

   > **Analogy:** Think of a rifle shooter improving over time. Each trial fine-tunes the shooter’s accuracy, increasing the likelihood of hitting the target center.
4. Choose the folder where the trained model will be saved. During training, this folder will temporarily store intermediate files. The best model from each trial (based on cross-validation) is saved in this folder. The filenames indicate the mean deviation from cross-validation, allowing to compare trials fairly and monitor performance.

**Note**: the software becomes unresponsive once training has started.

5. Once training is complete, the model can be used in the **Set landmarks on images** tab. Remember to:
   - Select a new set of images
   - Select the created model
   - Use images with the same resolution as those used for training for best results

Feel free to report issues, or suggest new features! This tool is designed to be flexible and useful for researchers and developers alike.
