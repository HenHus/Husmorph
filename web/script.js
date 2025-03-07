// UI element references
let canvas = document.getElementById("imageCanvas");
let ctx = canvas.getContext("2d");
let selectFolderButton = document.getElementById("selectFolderButton");
let folderPathSpan = document.getElementById("folderPath");
let selectSaveFolderButton = document.getElementById("selectSaveFolderButton");
let saveFolderPathSpan = document.getElementById("saveFolderPath");
let loadXMLButton = document.getElementById("loadXMLButton");
let prevButton = document.getElementById("prevButton");
let nextButton = document.getElementById("nextButton");
let saveButton = document.getElementById("saveButton");
let counterTextSpan = document.getElementById("counterText");
let maxLandmarksSelect = document.getElementById("maxLandmarksSelect");

// Global state variables
let folder = "";
let saveFolder = "";
let loadedXMLPath = null; // Stores the path of a loaded XML file (if any)
let imageList = [];
let currentImageIndex = 0;
let currentImage = new Image();
let landmarksData = {};   // { imagePath: [{x, y}, ...] }
let imageDimensions = {}; // { imagePath: {width, height} }
let maxLandmarks = parseInt(maxLandmarksSelect.value);

// Variables for scaling and zooming
let baseScale = 1;
let zoomFactor = 1;
let currentScaleFactor = 1;
let offsetX = 0;
let offsetY = 0;
let lastMouseX = 0;
let lastMouseY = 0;

// Update maxLandmarks from drop-down
maxLandmarksSelect.addEventListener("change", function() {
  maxLandmarks = parseInt(this.value);
});

// --- Folder Selection ---
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

// --- Save Folder Selection ---
selectSaveFolderButton.addEventListener("click", async () => {
  saveFolder = await eel.select_save_folder()();
  if (saveFolder) {
    saveFolderPathSpan.textContent = saveFolder;
  }
});

// --- Load XML file ---
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
    drawImage(); // redraw current image with loaded landmarks
  }
});

// --- Parse XML and update landmarksData and imageDimensions ---
function parseAndLoadXML(xmlString) {
  let parser = new DOMParser();
  let xmlDoc = parser.parseFromString(xmlString, "text/xml");
  let imageNodes = xmlDoc.getElementsByTagName("image");
  for (let i = 0; i < imageNodes.length; i++) {
    let imageNode = imageNodes[i];
    let fileAttr = imageNode.getAttribute("file");
    if (!fileAttr.startsWith(folder)) continue; // Only load images from the current folder
    landmarksData[fileAttr] = [];
    let boxNode = imageNode.getElementsByTagName("box")[0];
    if (boxNode) {
      let w = parseInt(boxNode.getAttribute("width"));
      let h = parseInt(boxNode.getAttribute("height"));
      // Add 1 back to recover original dimensions
      imageDimensions[fileAttr] = { width: w + 1, height: h + 1 };
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

// --- Update canvas size ---
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

// --- Draw image and numbered landmarks ---
function drawImage() {
  ctx.resetTransform();
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.setTransform(currentScaleFactor, 0, 0, currentScaleFactor, offsetX, offsetY);
  ctx.drawImage(currentImage, 0, 0);
  let imagePath = imageList[currentImageIndex];
  let points = landmarksData[imagePath] || [];
  points.forEach((point, index) => {
    ctx.beginPath();
    ctx.arc(point.x, point.y, 8 / currentScaleFactor, 0, 2 * Math.PI);
    ctx.fillStyle = "red";
    ctx.fill();
    ctx.strokeStyle = "blue";
    ctx.stroke();
    // Draw landmark number centered in the circle
    ctx.fillStyle = "white";
    ctx.font = `${12 / currentScaleFactor}px Arial`;
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(index + 1, point.x, point.y);
  });
  ctx.resetTransform();
}

// --- Update counter ---
function updateCounter() {
  counterTextSpan.textContent = `Image ${currentImageIndex + 1} of ${imageList.length}`;
}

// --- Load image ---
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

// --- Record mouse position ---
canvas.addEventListener("mousemove", function(e) {
  let rect = canvas.getBoundingClientRect();
  lastMouseX = e.clientX - rect.left;
  lastMouseY = e.clientY - rect.top;
});

// --- Canvas click event: add landmark if below maxLandmarks ---
canvas.addEventListener("click", function(e) {
  let rect = canvas.getBoundingClientRect();
  let x = e.clientX - rect.left;
  let y = e.clientY - rect.top;
  let imagePath = imageList[currentImageIndex];
  if (landmarksData[imagePath].length < maxLandmarks) {
    let originalX = (x - offsetX) / currentScaleFactor;
    let originalY = (y - offsetY) / currentScaleFactor;
    landmarksData[imagePath].push({ x: originalX, y: originalY });
    drawImage();
  } else {
    alert("Maximum number of landmarks reached for this image.");
  }
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

// --- Navigation buttons ---
prevButton.addEventListener("click", function() {
  if (currentImageIndex > 0) {
    currentImageIndex--;
    loadImage();
  } else {
    alert("This is the first image.");
  }
});

nextButton.addEventListener("click", function() {
  currentImageIndex++;
  if (currentImageIndex < imageList.length) {
    loadImage();
  } else {
    alert("All images processed.");
    ctx.resetTransform();
    ctx.clearRect(0, 0, canvas.width, canvas.height);
  }
});

// --- Keyboard events for zooming ---
// Press "w" to zoom in centered on mouse pointer.
document.addEventListener("keydown", function(e) {
  if (e.key === "w") {
    if (zoomFactor === 1) {
      zoomFactor = 4;
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

// --- Save XML button ---
// If an XML file was loaded, overwrite it; otherwise use the selected save folder.
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
