let canvas = document.getElementById("imageCanvas");
let ctx = canvas.getContext("2d");
let selectFolderButton = document.getElementById("selectFolderButton");
let folderPathSpan = document.getElementById("folderPath");
let selectSaveFolderButton = document.getElementById("selectSaveFolderButton");
let saveFolderPathSpan = document.getElementById("saveFolderPath");
let prevButton = document.getElementById("prevButton");
let skipButton = document.getElementById("skipButton");
let nextButton = document.getElementById("nextButton");
let saveButton = document.getElementById("saveButton");
let counterTextSpan = document.getElementById("counterText");

// Global state variables
let folder = "";
let saveFolder = "";
let imageList = [];
let currentImageIndex = 0;
let currentImage = new Image();
let landmarksData = {};    // keys: image paths, values: arrays of {x, y} in original image coordinates
let imageDimensions = {};  // keys: image paths, values: {width, height}
const maxLandmarks = 5;

// Variables for scaling and zoom transformation
let baseScale = 1;         // Scale to fit image inside container
let zoomFactor = 1;        // Additional zoom factor (1 = normal, 2 = zoomed in)
let currentScaleFactor = 1; // baseScale * zoomFactor
let offsetX = 0;           // Translation offset in canvas coordinates
let offsetY = 0;
let waitingForNextClick = false;

// Last known mouse coordinates on canvas (used for zooming)
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

// --- Update canvas size and compute base scale ---
function updateCanvasSize() {
  let container = document.getElementById("container");
  let availableWidth = container.clientWidth;
  let availableHeight = container.clientHeight;
  baseScale = Math.min(availableWidth / currentImage.naturalWidth, availableHeight / currentImage.naturalHeight);
  currentScaleFactor = baseScale * zoomFactor;
  // Set canvas size to the full image size (scaled)
  canvas.width = currentImage.naturalWidth * currentScaleFactor;
  canvas.height = currentImage.naturalHeight * currentScaleFactor;
  // Save original image dimensions for XML
  let imagePath = imageList[currentImageIndex];
  imageDimensions[imagePath] = {
    width: currentImage.naturalWidth,
    height: currentImage.naturalHeight
  };
}

// --- Draw the image and landmarks using transformation ---
function drawImage() {
  // Clear the canvas
  ctx.resetTransform();
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  
  // Set transform: scale and translation
  ctx.setTransform(currentScaleFactor, 0, 0, currentScaleFactor, offsetX, offsetY);
  
  // Draw the image at (0,0) in image (natural) coordinates
  ctx.drawImage(currentImage, 0, 0);
  
  // Draw landmarks (each landmark is in original image coordinates)
  let imagePath = imageList[currentImageIndex];
  let points = landmarksData[imagePath];
  if (points) {
    points.forEach(point => {
      ctx.beginPath();
      // To keep the landmark size roughly constant on screen, adjust radius by inverse of currentScaleFactor.
      ctx.arc(point.x, point.y, 8 / currentScaleFactor, 0, 2 * Math.PI);
      ctx.fillStyle = "red";
      ctx.fill();
      ctx.strokeStyle = "blue";
      ctx.stroke();
    });
  }
  
  // Reset transform for any further drawing if needed
  ctx.resetTransform();
}

// --- Update counter display (outside the image) ---
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
  waitingForNextClick = false;
  if (!landmarksData[imagePath]) {
    landmarksData[imagePath] = [];
  }
  // Reset zoom and translation when switching images
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

// --- Canvas click event: add landmark or load next image ---
canvas.addEventListener("click", function(e) {
  let rect = canvas.getBoundingClientRect();
  let x = e.clientX - rect.left;
  let y = e.clientY - rect.top;
  let imagePath = imageList[currentImageIndex];
  let points = landmarksData[imagePath];
  
  if (waitingForNextClick) {
    loadNextImage();
    return;
  }
  
  if (points.length < maxLandmarks) {
    // Convert canvas coordinates to original image coordinates using inverse transform
    let originalX = (x - offsetX) / currentScaleFactor;
    let originalY = (y - offsetY) / currentScaleFactor;
    points.push({ x: originalX, y: originalY });
    drawImage();
    if (points.length === maxLandmarks) {
      waitingForNextClick = true;
    }
  }
});

// --- Right-click: remove last landmark ---
canvas.addEventListener("contextmenu", function(e) {
  e.preventDefault();
  let imagePath = imageList[currentImageIndex];
  let points = landmarksData[imagePath];
  if (points.length > 0) {
    points.pop();
    waitingForNextClick = false;
    drawImage();
  }
  return false;
});

// --- Keyboard events for skipping and zooming ---
// Pressing Tab to skip the image (discard landmarks)
document.addEventListener("keydown", function(e) {
  if (e.key === "Tab") {
    e.preventDefault();
    skipImage();
  } else if (e.key === "w") {
    // Zoom in when "w" is pressed: adjust zoomFactor and compute offset so that the current mouse position stays fixed.
    if (zoomFactor === 1) {
      zoomFactor = 2;  // Adjust zoom level as desired
      // Calculate new offset so that the point under the mouse remains at the same canvas position.
      // Using the formula: offset = mouse * (1 - zoomFactor)
      offsetX = lastMouseX * (1 - zoomFactor);
      offsetY = lastMouseY * (1 - zoomFactor);
      currentScaleFactor = baseScale * zoomFactor;
      // Adjust canvas size to reflect zoom (optional – canvas may become larger than container)
      canvas.width = currentImage.naturalWidth * currentScaleFactor;
      canvas.height = currentImage.naturalHeight * currentScaleFactor;
      drawImage();
    }
  }
});

document.addEventListener("keyup", function(e) {
  if (e.key === "w") {
    // Revert zoom to normal when "w" is released.
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
// Goes back one image (if available), preserving annotations.
prevButton.addEventListener("click", function() {
  if (currentImageIndex > 0) {
    currentImageIndex--;
    loadImage();
  } else {
    alert("This is the first image.");
  }
});

// --- Skip Image button handler ---
// Skips current image (discarding its annotations)
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
    alert("All images processed. You can now save the landmarks.");
    ctx.resetTransform();
    ctx.clearRect(0, 0, canvas.width, canvas.height);
  }
}

// --- Save XML button handler ---
saveButton.addEventListener("click", async function() {
  if (!saveFolder) {
    alert("Please select a save folder.");
    return;
  }
  let result = await eel.save_xml(landmarksData, imageDimensions, folder, saveFolder)();
  alert(result);
});
