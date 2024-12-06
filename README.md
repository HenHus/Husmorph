*As of now, the code is not cleaned up, but it's working so I decided to upload the tool anyways. Enjoy :)*

*This README file is also under construction and will be updated.*


# HUSMORPH

Grapichal user interface for landmark placement; both manually and with machine learning

## Installation and setup

Python is required for the tool to work, the tool were built with python 3.11.X. And environment like conda is also recommended, but not nessecary ([Anaconda](https://www.anaconda.com/download/success)).

Then, in a python terminal window, use the following command line to install the other necessary modules:

    pip install -r Requirements.txt

*This has to be done after the tool is downloaded, and the terminal needs to be opened at the same path as the tool.*

To open the graphical user interface, just run the Main.py file. This could be done in different ways. One way is to open the whole folder in [VS code](https://code.visualstudio.com) (similar to R studio) and run the script from there, or run directly from the terminal (in the folder containing the files). The command for running the script varies slightly, but here is a few that may work for you:

    python Main.py

or

    py Main.py

or

    python3 Main.py



# Using the tool

The `Main.py` does everything, the other files should be ignored unless you know what you are doing. All features should also be used through the graphical user interface.

## Setting landmarks on images

By pressing **Set landmarks on images**, another window pops up. In the window you would start by selecting the image folder that you have.

**I strongly recommend that the image folder is in the same folder as the rest of these files before you start.**

The images can be any resolution, but all the images should be the same resolution. If the images are going to be used for machine learning, keep the resolution at 2 000 000 pixels or lower (around 1920x1080).

The selected folder will appear in the box.

Select how many landmarks you want on each image from the menu.

Once these 2 things are selected, you can go ahead and **place landmarks**. Make sure that the 'Use the selected model' option is **not** selected.

Another pop-up window will be opened, and all the images in the folder you selected will be displayed one at the time.

1. **Left click** on the image to place a landmark
2. **Right click** anywhere on the image to delete the last placed landmark
3. Once you have placed the number of landmarks you selected in the graphical interface, simply **left click** anywhere on the image to go to the next image
4. If you want to skip an image (for some reason), you can press **tab** to go straight to the next image and skip the current one.

Once all images have been processed, the pop-up will automatically close, and all the data is saved to a XML file in this folder.


## Visualizing landmarks

Simply open the XML file that you want.

*Note that the image folder itself can't be removed. It still has to stay where it is in order to display the landmarks.*

Press **space** to go through the images.

## Machine learning

Select the XML file that contains the landmarks you want to predict in the future using machine learning.

You have to select how many *threads* you want your computer to use. The more the threads, the faster the training goes. However I recommend saving at least one or two threads from your computer's total threads.

*If you don't know how many threads you computer has, go with around 5 threads on a regular laptop that it not that old.*

Select how many *trials* you would like to have. A *trial* is a set of parameters used to find the best parameters for your dataset. The more trials, the higher the success to find the best possible machine learning model for you. However, twice as many trials also means twice as long time to complete the training.

*Imagine a rifle shooter. He might perform okay in the start, but if you give him some time to train, he will overall get better and better. At one point he might also hit the perfect shot in the center of the target.*

Once a model is created, you can try to predict landmarks in the '**Set landmarks on images**' - tab in the interface, and select the model that were created. Also remember to select the folder of images to predict landmarks on.

**Make sure the images for prediction has the same resolution as the images used to train the model.**

## Exporting

As of now, it's possible to export the XML data to CSV format. Other export formats will be added in the future.