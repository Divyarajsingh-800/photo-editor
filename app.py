<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Photo Editor and Comparison</title>
  <style>
    body {
      margin: 0;
      padding: 20px;
      font-family: 'Segoe UI', sans-serif;
      background: radial-gradient(circle at top, #0f0c29, #302b63, #24243e);
      color: #fff;
      text-align: center;
    }

    h1 {
      font-size: 3em;
      margin-bottom: 20px;
      text-shadow: 0 0 15px #0ff;
    }

    .canvas-container {
      display: flex;
      justify-content: center;
      gap: 20px;
      margin-bottom: 20px;
      flex-wrap: wrap;
    }

    .canvas-wrapper {
      background: rgba(255, 255, 255, 0.05);
      padding: 10px;
      border-radius: 12px;
      box-shadow: 0 0 15px rgba(0,255,255,0.3);
    }

    canvas {
      border: 3px solid #0ff;
      display: block;
      background-color: #000;
      max-width: 100%;
    }

    input[type="file"],
    button,
    input[type="range"] {
      margin: 10px;
      padding: 10px;
      font-size: 1em;
      border-radius: 6px;
      border: none;
      outline: none;
      background-color: #0ff;
      color: #000;
      transition: background-color 0.3s ease;
    }

    input[type="range"] {
      width: 200px;
    }

    button:hover,
    input[type="file"]:hover {
      background-color: #00e6e6;
      cursor: pointer;
    }

    .controls {
      margin-top: 20px;
    }

    .slider-container {
      display: flex;
      justify-content: center;
      flex-wrap: wrap;
      gap: 15px;
      margin-top: 10px;
    }

    .slider-box {
      display: flex;
      flex-direction: column;
      align-items: center;
      color: #0ff;
    }
  </style>
</head>
<body>
  <h1>Photo Editor and Comparison</h1>
  <input type="file" id="upload" accept="image/*">

  <div class="canvas-container">
    <div class="canvas-wrapper">
      <h2>Original</h2>
      <canvas id="originalCanvas" width="400" height="400"></canvas>
    </div>
    <div class="canvas-wrapper">
      <h2>Filtered</h2>
      <canvas id="filteredCanvas" width="400" height="400"></canvas>
    </div>
  </div>

  <div class="controls">
    <button onclick="applyFilter('blur')">Blur</button>
    <button onclick="applyFilter('sharpen')">Sharpen</button>
    <button onclick="applyFilter('invert')">Invert</button>
    <button onclick="applyFilter('grayscale')">Grayscale</button>
    <button onclick="resetFiltered()">Reset</button>
    <button onclick="downloadImage()">Download</button>
  </div>

  <div class="slider-container">
    <div class="slider-box">
      <label for="brightness">Brightness</label>
      <input type="range" id="brightness" min="0" max="200" value="100">
    </div>
    <div class="slider-box">
      <label for="contrast">Contrast</label>
      <input type="range" id="contrast" min="0" max="200" value="100">
    </div>
    <div class="slider-box">
      <label for="opacity">Opacity</label>
      <input type="range" id="opacity" min="0" max="100" value="100">
    </div>
  </div>

  <p>Hold mouse on filtered image to preview original</p>

  <script>
    const upload = document.getElementById('upload');
    const originalCanvas = document.getElementById('originalCanvas');
    const filteredCanvas = document.getElementById('filteredCanvas');
    const origCtx = originalCanvas.getContext('2d');
    const filtCtx = filteredCanvas.getContext('2d');

    const brightnessSlider = document.getElementById('brightness');
    const contrastSlider = document.getElementById('contrast');
    const opacitySlider = document.getElementById('opacity');

    let img = new Image();
    let originalImageData = null;

    function adjustCanvasSizes(width, height) {
      originalCanvas.width = filteredCanvas.width = width;
      originalCanvas.height = filteredCanvas.height = height;
    }

    upload.addEventListener('change', function (e) {
      if (e.target.files && e.target.files[0]) {
        const reader = new FileReader();
        reader.onload = function (event) {
          img.onload = function () {
            const scale = Math.min(600 / img.width, 600 / img.height, 1);
            const width = img.width * scale;
            const height = img.height * scale;
            adjustCanvasSizes(width, height);
            origCtx.drawImage(img, 0, 0, width, height);
            filtCtx.drawImage(img, 0, 0, width, height);
            originalImageData = filtCtx.getImageData(0, 0, width, height);
          };
          img.src = event.target.result;
        };
        reader.readAsDataURL(e.target.files[0]);
      }
    });

    function resetFiltered() {
      if (originalImageData) {
        filtCtx.putImageData(originalImageData, 0, 0);
        applyAdjustments();
      }
    }

    function applyFilter(type) {
      if (!originalImageData) return;

      let imageData = filtCtx.getImageData(0, 0, filteredCanvas.width, filteredCanvas.height);
      switch (type) {
        case 'blur':
          imageData = convolution(imageData, [1 / 9, 1 / 9, 1 / 9, 1 / 9, 1 / 9, 1 / 9, 1 / 9, 1 / 9, 1 / 9]);
          break;
        case 'sharpen':
          imageData = convolution(imageData, [0, -1, 0, -1, 5, -1, 0, -1, 0]);
          break;
        case 'invert':
          imageData = invert(imageData);
          break;
        case 'grayscale':
          imageData = grayscale(imageData);
          break;
      }
      filtCtx.putImageData(imageData, 0, 0);
      originalImageData = filtCtx.getImageData(0, 0, filteredCanvas.width, filteredCanvas.height);
      applyAdjustments();
    }

    function invert(imageData) {
      const data = imageData.data;
      for (let i = 0; i < data.length; i += 4) {
        data[i] = 255 - data[i];
        data[i + 1] = 255 - data[i + 1];
        data[i + 2] = 255 - data[i + 2];
      }
      return imageData;
    }

    function grayscale(imageData) {
      const data = imageData.data;
      for (let i = 0; i < data.length; i += 4) {
        const avg = (data[i] + data[i + 1] + data[i + 2]) / 3;
        data[i] = data[i + 1] = data[i + 2] = avg;
      }
      return imageData;
    }

    function convolution(imageData, kernel) {
      const side = Math.round(Math.sqrt(kernel.length));
      const halfSide = Math.floor(side / 2);
      const src = imageData.data;
      const sw = imageData.width;
      const sh = imageData.height;
      const output = filtCtx.createImageData(sw, sh);
      const dst = output.data;

      for (let y = 0; y < sh; y++) {
        for (let x = 0; x < sw; x++) {
          const dstOff = (y * sw + x) * 4;
          let r = 0, g = 0, b = 0;
          for (let cy = 0; cy < side; cy++) {
            for (let cx = 0; cx < side; cx++) {
              const scy = y + cy - halfSide;
              const scx = x + cx - halfSide;
              if (scy >= 0 && scy < sh && scx >= 0 && scx < sw) {
                const srcOff = (scy * sw + scx) * 4;
                const wt = kernel[cy * side + cx];
                r += src[srcOff] * wt;
                g += src[srcOff + 1] * wt;
                b += src[srcOff + 2] * wt;
              }
            }
          }
          dst[dstOff] = r;
          dst[dstOff + 1] = g;
          dst[dstOff + 2] = b;
          dst[dstOff + 3] = src[dstOff + 3];
        }
      }
      return output;
    }

    function applyAdjustments() {
      const brightness = brightnessSlider.value;
      const contrast = contrastSlider.value;
      const opacity = opacitySlider.value / 100;
      filteredCanvas.style.filter = `brightness(${brightness}%) contrast(${contrast}%) opacity(${opacity})`;
    }

    brightnessSlider.addEventListener("input", applyAdjustments);
    contrastSlider.addEventListener("input", applyAdjustments);
    opacitySlider.addEventListener("input", applyAdjustments);

    filteredCanvas.addEventListener("mousedown", () => {
      filteredCanvas.style.display = "none";
    });
    filteredCanvas.addEventListener("mouseup", () => {
      filteredCanvas.style.display = "block";
    });

    function downloadImage() {
      const link = document.createElement('a');
      link.download = 'edited-image.png';
      link.href = filteredCanvas.toDataURL();
      link.click();
    }
  </script>
</body>
</html>
