let canvas = document.getElementById("imageCanvas");
let ctx = canvas.getContext("2d");
let selectFolderButton = document.getElementById("selectFolderButton");
let folderPathSpan = document.getElementById("folderPath");
let selectSaveFolderButton = document.getElementById("selectSaveFolderButton");
let saveFolderPathSpan = document.getElementById("saveFolderPath");
let loadXMLButton = document.getElementById("loadXMLButton");
let prevButton = document.getElementById("prevButton");
let skipButton = document.getElementById("skipButton");
let nextButton = document.getElementById("nextButton");
let saveButton = document.getElementById("saveButton");
let counterTextSpan = document.getElementById("counterText");

// Global state variables
let folder = "";
let saveFolder = "";
let loadedXMLPath = null;  // path of the loaded XML file (if any)
let imageList = [];
let currentImageIndex = 0;
let currentImage = new Image();
let landmarksData = {};    // keys: image paths, values: arrays of {x, y} in original image coordinates
let imageDimensions = {};  // keys: image paths, values: {width, height}

// Variables for scaling and zoom transformation
let baseScale = 1;
let zoomFactor = 1;
let currentScaleFactor = 1;
let offsetX = 0;
let offsetY = 0;

// Last known mouse coordinates on canvas (for zoom centering)
let lastMouseX = 0;
let lastMouseY = 0;

// --- Select image folder handler ---
selectFolderButton.addEventListener("click", async () => {
  folder = await eel.select_folder()();
  if (folder) {
    folderPathSpan.textContent = folder;
    imageList = await eel.get_image_list(folder)();
    currentImageIndex = 0;
    landmarksData = {};
    imageDimensions = {};
    if (imageList.length > 0) {
      loadImage();
      updateCounter();
    } else {
      alert("No valid image files found in this folder.");
    }
  }
});

// --- Select save folder handler ---
selectSaveFolderButton.addEventListener("click", async () => {
  saveFolder = await eel.select_save_folder()();
  if (saveFolder) {
    saveFolderPathSpan.textContent = saveFolder;
  }
});

// --- Load XML file handler ---
loadXMLButton.addEventListener("click", async () => {
  if (!folder) {
    alert("Please select an image folder first.");
    return;
  }
  let xmlFilePath = await eel.select_xml_file()();
  if (xmlFilePath) {
    loadedXMLPath = xmlFilePath;
    let xmlContent = await eel.get_xml_data(xmlFilePath)();
    parseAndLoadXML(xmlContent);
    alert("XML loaded successfully.");
    // Redraw current image with any loaded landmarks.
    drawImage();
  }
});

// --- Parse XML content and update landmarksData and imageDimensions ---
function parseAndLoadXML(xmlString) {
  let parser = new DOMParser();
  let xmlDoc = parser.parseFromString(xmlString, "text/xml");
  let imageNodes = xmlDoc.getElementsByTagName("image");
  for (let i = 0; i < imageNodes.length; i++) {
    let imageNode = imageNodes[i];
    let fileAttr = imageNode.getAttribute("file");
    // Only load if the image belongs to the current folder (simple check)
    if (!fileAttr.startsWith(folder)) continue;
    // Initialize array for landmarks
    landmarksData[fileAttr] = [];
    let boxNode = imageNode.getElementsByTagName("box")[0];
    if (boxNode) {
      let w = parseInt(boxNode.getAttribute("width"));
      let h = parseInt(boxNode.getAttribute("height"));
      // Recover original dimensions (we stored width-1, so add 1 back)
      imageDimensions[fileAttr] = {
        width: w + 1,
        height: h + 1
      };
      let partNodes = boxNode.getElementsByTagName("part");
      for (let j = 0; j < partNodes.length; j++) {
        let part = partNodes[j];
        let x = parseFloat(part.getAttribute("x"));
        let y = parseFloat(part.getAttribute("y"));
        landmarksData[fileAttr].push({ x, y });
      }
    }
  }
}

// --- Update canvas size and compute base scale ---
function updateCanvasSize() {
  let container = document.getElementById("container");
  let availableWidth = container.clientWidth;
  let availableHeight = container.clientHeight;
  baseScale = Math.min(availableWidth / currentImage.naturalWidth, availableHeight / currentImage.naturalHeight);
  currentScaleFactor = baseScale * zoomFactor;
  canvas.width = currentImage.naturalWidth * currentScaleFactor;
  canvas.height = currentImage.naturalHeight * currentScaleFactor;
  let imagePath = imageList[currentImageIndex];
  imageDimensions[imagePath] = {
    width: currentImage.naturalWidth,
    height: currentImage.naturalHeight
  };
}

// --- Draw image and landmarks using transformation ---
function drawImage() {
  ctx.resetTransform();
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.setTransform(currentScaleFactor, 0, 0, currentScaleFactor, offsetX, offsetY);
  ctx.drawImage(currentImage, 0, 0);
  let imagePath = imageList[currentImageIndex];
  let points = landmarksData[imagePath];
  if (points) {
    points.forEach(point => {
      ctx.beginPath();
      ctx.arc(point.x, point.y, 8 / currentScaleFactor, 0, 2 * Math.PI);
      ctx.fillStyle = "red";
      ctx.fill();
      ctx.strokeStyle = "blue";
      ctx.stroke();
    });
  }
  ctx.resetTransform();
}

// --- Update counter display (outside image) ---
function updateCounter() {
  counterTextSpan.textContent = `Image ${currentImageIndex + 1} of ${imageList.length}`;
}

// --- Load image data and set up canvas ---
function loadImage() {
  if (currentImageIndex < 0 || currentImageIndex >= imageList.length) {
    alert("No more images.");
    return;
  }
  let imagePath = imageList[currentImageIndex];
  if (!landmarksData[imagePath]) {
    landmarksData[imagePath] = [];
  }
  zoomFactor = 1;
  offsetX = 0;
  offsetY = 0;
  eel.get_image_data(imagePath)(function(dataUrl) {
    currentImage = new Image();
    currentImage.onload = function() {
      updateCanvasSize();
      drawImage();
      updateCounter();
    };
    currentImage.src = dataUrl;
  });
}

// --- Record mouse position on canvas ---
canvas.addEventListener("mousemove", function(e) {
  let rect = canvas.getBoundingClientRect();
  lastMouseX = e.clientX - rect.left;
  lastMouseY = e.clientY - rect.top;
});

// --- Canvas click event: add a landmark ---
canvas.addEventListener("click", function(e) {
  let rect = canvas.getBoundingClientRect();
  let x = e.clientX - rect.left;
  let y = e.clientY - rect.top;
  let imagePath = imageList[currentImageIndex];
  // Convert canvas coordinates to original image coordinates using inverse transform
  let originalX = (x - offsetX) / currentScaleFactor;
  let originalY = (y - offsetY) / currentScaleFactor;
  landmarksData[imagePath].push({ x: originalX, y: originalY });
  drawImage();
});

// --- Right-click: remove last landmark ---
canvas.addEventListener("contextmenu", function(e) {
  e.preventDefault();
  let imagePath = imageList[currentImageIndex];
  if (landmarksData[imagePath].length > 0) {
    landmarksData[imagePath].pop();
    drawImage();
  }
  return false;
});

// --- Keyboard events for zooming ---
// Pressing "w" zooms in centered on the current mouse pointer.
document.addEventListener("keydown", function(e) {
  if (e.key === "w") {
    if (zoomFactor === 1) {
      zoomFactor = 2;  // Adjust zoom level as desired
      offsetX = lastMouseX * (1 - zoomFactor);
      offsetY = lastMouseY * (1 - zoomFactor);
      currentScaleFactor = baseScale * zoomFactor;
      canvas.width = currentImage.naturalWidth * currentScaleFactor;
      canvas.height = currentImage.naturalHeight * currentScaleFactor;
      drawImage();
    }
  }
});

document.addEventListener("keyup", function(e) {
  if (e.key === "w") {
    if (zoomFactor !== 1) {
      zoomFactor = 1;
      offsetX = 0;
      offsetY = 0;
      updateCanvasSize();
      drawImage();
    }
  }
});

// --- Previous Image button handler ---
prevButton.addEventListener("click", function() {
  if (currentImageIndex > 0) {
    currentImageIndex--;
    loadImage();
  } else {
    alert("This is the first image.");
  }
});

// --- Skip Image button handler ---
// Discards annotations for the current image.
skipButton.addEventListener("click", function() {
  let imagePath = imageList[currentImageIndex];
  delete landmarksData[imagePath];
  loadNextImage();
});

// --- Next Image button handler ---
// Moves to the next image while preserving annotations.
nextButton.addEventListener("click", function() {
  loadNextImage();
});

// --- Load the next image ---
function loadNextImage() {
  currentImageIndex++;
  if (currentImageIndex < imageList.length) {
    loadImage();
  } else {
    alert("All images processed.");
    ctx.resetTransform();
    ctx.clearRect(0, 0, canvas.width, canvas.height);
  }
}

// --- Save XML button handler ---
// If an XML file was loaded, overwrite it; otherwise, use the selected save folder.
saveButton.addEventListener("click", async function() {
  if (loadedXMLPath) {
    let result = await eel.save_xml_edit(landmarksData, imageDimensions, loadedXMLPath)();
    alert(result);
  } else {
    if (!saveFolder) {
      alert("Please select a save folder.");
      return;
    }
    let result = await eel.save_xml(landmarksData, imageDimensions, folder, saveFolder)();
    alert(result);
  }
});
