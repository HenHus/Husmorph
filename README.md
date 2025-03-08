# HUSMORPH v2.0 (early release for MacOS)

## Major updates in the new early release version!

HUSMORPH is a graphical user interface (GUI) designed for landmark placement on images. It supports both manual placement and automated machine learning-based predictions. This versatile tool can be used right out of the box or by running the scripts provided in this repository for more customized workflows.

## Important!

The software is currently very big, and requires 1GB storage.

The startup time is long. Be patient, it can take up to 1 min before the software is running.

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

**[Download here](https://drive.google.com/file/d/1IC0XUQLshbcBHlt7jbdVgdt0UKDWJ3I_/view?usp=drivesdk)**

---

### macOS with silicon chip (M1, M2, M3, M4 models)
- **File:** DMG installer.
- **Instructions:** Download the file, drag the application to your `Applications` folder, and launch `Husmorph` from there.

   > **Note:** Mac-users may have to right-click, and then press `open` the first time opening the software to bypass security warnings. Otherwise, it can be found in settings -> security on your computer.

**[Download here (v2.0 early release)](https://drive.google.com/file/d/1EeeiWF8GwBHTh2vyoDpooLWOXrgU_RS9/view?usp=sharing)**

**[Download here (v1)](https://drive.google.com/file/d/1Weko3YBif2mEi5Uz-tU1BdMo0vcGYBuT/view?usp=share_link)**




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

Feel free to report issues, or suggest new features! This tool is designed to be flexible and useful for researchers and developers alike.
