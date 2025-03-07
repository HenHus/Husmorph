/* ===================== LANDMARKING FUNCTIONALITY ===================== */

// Get UI element references (landmarking)
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
let maxLandmarksSelect = document.getElementById("maxLandmarksSelect");
let counterTextSpan = document.getElementById("counterText");

// Global state for landmarking
let folder = "";
let saveFolder = "";
let loadedXMLPath = null;
let imageList = [];
let currentImageIndex = 0;
let currentImage = new Image();
let landmarksData = {};    // { imagePath: [{x,y}, ...] }
let imageDimensions = {};  // { imagePath: {width, height} }
let maxLandmarks = parseInt(maxLandmarksSelect.value);

// Zooming & transform variables
// Here the canvas drawing buffer is set to the image’s natural size.
// CSS (in index.html) makes it responsive.
let baseScale = 1;       // We will set this to 1 because our canvas buffer is natural size.
let zoomFactor = 1;      // 1 means no zoom; becomes 4 when "w" is pressed.
let currentScaleFactor = baseScale * zoomFactor; // current applied scale factor.
let offsetX = 0, offsetY = 0;  // transform offsets.
let storedOffsetX = 0, storedOffsetY = 0;  // to store offsets before zoom.
let lastMouseX = 0, lastMouseY = 0; // in displayed (CSS) coordinates.

// Update maxLandmarks from the drop-down.
maxLandmarksSelect.addEventListener("change", function() {
  maxLandmarks = parseInt(this.value);
});

// For landmarking, we set the canvas drawing buffer to the image’s natural size.
// The CSS in index.html ensures the canvas is scaled relative to its container.
// (We assume no extra scaling in updateCanvasSize here.)
function loadImage() {
  if (currentImageIndex < 0 || currentImageIndex >= imageList.length) {
    alert("No more images.");
    return;
  }
  let imagePath = imageList[currentImageIndex];
  if (!landmarksData[imagePath]) {
    landmarksData[imagePath] = [];
  }
  // Reset zoom.
  zoomFactor = 1;
  offsetX = 0;
  offsetY = 0;
  currentScaleFactor = baseScale * zoomFactor;
  
  eel.get_image_data(imagePath)(function(dataUrl) {
    currentImage = new Image();
    currentImage.onload = function() {
      // Set canvas drawing buffer to natural dimensions.
      canvas.width = currentImage.naturalWidth;
      canvas.height = currentImage.naturalHeight;
      // baseScale remains 1.
      offsetX = 0;
      offsetY = 0;
      currentScaleFactor = 1;
      drawImage();
      updateCounter();
      // Save original image dimensions.
      imageDimensions[imagePath] = {
        width: currentImage.naturalWidth,
        height: currentImage.naturalHeight
      };
    };
    currentImage.src = dataUrl;
  });
}

function drawImage() {
  // Clear and set transform.
  ctx.resetTransform();
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.setTransform(currentScaleFactor, 0, 0, currentScaleFactor, offsetX, offsetY);
  ctx.drawImage(currentImage, 0, 0);
  // Draw landmarks (landmarks are stored in image’s natural coordinates).
  let imagePath = imageList[currentImageIndex];
  let points = landmarksData[imagePath] || [];
  points.forEach((point, index) => {
    ctx.beginPath();
    ctx.arc(point.x, point.y, 8 / currentScaleFactor, 0, 2 * Math.PI);
    ctx.fillStyle = "red";
    ctx.fill();
    ctx.strokeStyle = "blue";
    ctx.stroke();
    ctx.fillStyle = "white";
    ctx.font = `${12 / currentScaleFactor}px Arial`;
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(index + 1, point.x, point.y);
  });
  ctx.resetTransform();
}

function updateCounter() {
  counterTextSpan.textContent = `Image ${currentImageIndex + 1} of ${imageList.length}`;
}

// Convert displayed (CSS) click coordinates to natural canvas coordinates.
// Since the canvas drawing buffer is at natural size, and the canvas is scaled by CSS,
// we use the ratio between canvas.width and canvas.offsetWidth.
function getNaturalCoordinates(e) {
  let rect = canvas.getBoundingClientRect();
  // e.offsetX/Y may not be reliable; use clientX relative to rect.
  let clickX = e.clientX - rect.left;
  let clickY = e.clientY - rect.top;
  let ratioX = canvas.width / rect.width;
  let ratioY = canvas.height / rect.height;
  return {
    x: clickX * ratioX,
    y: clickY * ratioY
  };
}

// Landmarking click: add landmark if under maxLandmarks.
canvas.addEventListener("click", function(e) {
  let coords = getNaturalCoordinates(e);
  // Invert current transform: natural coordinates = (displayCoord - offset) / currentScaleFactor.
  let imageX = (coords.x - offsetX) / currentScaleFactor;
  let imageY = (coords.y - offsetY) / currentScaleFactor;
  let imagePath = imageList[currentImageIndex];
  if (landmarksData[imagePath].length < maxLandmarks) {
    landmarksData[imagePath].push({ x: imageX, y: imageY });
    drawImage();
  } else {
    alert("Maximum number of landmarks reached for this image.");
  }
});

// Right-click removes the last landmark.
canvas.addEventListener("contextmenu", function(e) {
  e.preventDefault();
  let imagePath = imageList[currentImageIndex];
  if (landmarksData[imagePath].length > 0) {
    landmarksData[imagePath].pop();
    drawImage();
  }
  return false;
});

// Navigation buttons.
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

// Save XML button.
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

// Record last mouse position (in displayed coordinates) for zooming.
canvas.addEventListener("mousemove", function(e) {
  let rect = canvas.getBoundingClientRect();
  lastMouseX = e.clientX - rect.left;
  lastMouseY = e.clientY - rect.top;
});

/* ------------------------- ZOOMING WITH "w" ------------------------- */
// We want to zoom 4× so that the image coordinate under the mouse becomes centered.
// We do not change the canvas drawing buffer size.
document.addEventListener("keydown", function(e) {
  if (e.key === "w" && zoomFactor === 1) {
    zoomFactor = 4;
    // Store the current offsets for later restoration.
    storedOffsetX = offsetX;
    storedOffsetY = offsetY;
    // Get the natural coordinate of the point under the mouse.
    let rect = canvas.getBoundingClientRect();
    let ratioX = canvas.width / rect.width;
    let ratioY = canvas.height / rect.height;
    let natX = (lastMouseX * ratioX - offsetX) / currentScaleFactor;
    let natY = (lastMouseY * ratioY - offsetY) / currentScaleFactor;
    // New scale.
    let newScale = baseScale * zoomFactor;
    currentScaleFactor = newScale;
    // We want the point (natX, natY) to map to the center of the canvas.
    offsetX = (canvas.width / 2) - (natX * newScale);
    offsetY = (canvas.height / 2) - (natY * newScale);
    drawImage();
  }
});
document.addEventListener("keyup", function(e) {
  if (e.key === "w" && zoomFactor !== 1) {
    zoomFactor = 1;
    // Revert offsets.
    offsetX = 0;
    offsetY = 0;
    currentScaleFactor = baseScale;
    drawImage();
  }
});

/* ===================== MACHINE LEARNING FUNCTIONALITY ===================== */

// ML UI elements
const xmlUpload = document.getElementById("xmlUpload");
const trialsRange = document.getElementById("trialsRange");
const threadsRange = document.getElementById("threadsRange");
const trialsValue = document.getElementById("trialsValue");
const threadsValue = document.getElementById("threadsValue");
const startButton = document.getElementById("startButton");

// Update slider displays.
trialsRange.addEventListener("input", function() {
  trialsValue.textContent = this.value;
});
threadsRange.addEventListener("input", function() {
  threadsValue.textContent = this.value;
});

// Read uploaded XML file.
function readXMLFile(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (e) => resolve(e.target.result);
    reader.onerror = (e) => reject(e);
    reader.readAsText(file);
  });
}

// Start ML process.
startButton.addEventListener("click", async () => {
  if (xmlUpload.files.length === 0) {
    alert("Please upload an XML file.");
    return;
  }
  const xmlFile = xmlUpload.files[0];
  let xmlContent;
  try {
    xmlContent = await readXMLFile(xmlFile);
  } catch (err) {
    alert("Error reading XML file.");
    return;
  }
  const trials = parseInt(trialsRange.value);
  const threads = parseInt(threadsRange.value);
  // Call your Python function via Eel (adjust function name/parameters as needed).
  eel.start_machine_learning(xmlContent, trials, threads)(function(result) {
    alert(result);
  });
});

/* ===================== FOLDER INITIALIZATION ===================== */
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
selectSaveFolderButton.addEventListener("click", async () => {
  saveFolder = await eel.select_save_folder()();
  if (saveFolder) {
    saveFolderPathSpan.textContent = saveFolder;
  }
});
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
    drawImage();
  }
});
