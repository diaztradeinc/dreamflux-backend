
let currentMode = 'text';

function toggleAdvanced() {
  const adv = document.getElementById('advanced');
  adv.style.display = adv.style.display === 'none' ? 'block' : 'none';
}

function switchMode(mode) {
  currentMode = mode;
  document.getElementById('textMode').classList.toggle('active', mode === 'text');
  document.getElementById('imageMode').classList.toggle('active', mode === 'image');
  document.getElementById('imageInputs').classList.toggle('hidden', mode !== 'image');
}

const aspectRatios = {
  "1:1": [768, 768],
  "4:5": [768, 960],
  "3:4": [768, 1024],
  "2:3": [768, 1152],
  "16:9": [1024, 576],
  "9:16": [576, 1024],
  "3:2": [1024, 682],
  "21:9": [1024, 438],
  "5:4": [800, 640],
  "4:3": [960, 720]
};

function applyAspectRatio(ratio) {
  const [w, h] = aspectRatios[ratio];
  document.getElementById('width').value = w;
  document.getElementById('height').value = h;
}

function generateImage() {
  const loader = document.getElementById('loader');
  const gallery = document.getElementById('gallery');
  loader.style.display = 'block';
  gallery.innerHTML = '';

  const prompt = document.getElementById('prompt').value;
  const negative_prompt = document.getElementById('negative').value;
  const steps = parseInt(document.getElementById('steps').value);
  const cfg_scale = parseFloat(document.getElementById('guidance').value);
  const width = parseInt(document.getElementById('width').value);
  const height = parseInt(document.getElementById('height').value);
  const seed = parseInt(document.getElementById('seed').value);
  const model = document.getElementById('model').value;
  const style_preset = document.getElementById('style').value;
  const clip_guidance_preset = document.getElementById('clip_guidance').value;
  const image_strength = parseFloat(document.getElementById('image_strength').value);
  const imageFile = document.getElementById('image-prompt').files[0];

  const backend = "https://dreamflux-backend-production.up.railway.app";

  if (currentMode === 'text') {
    const payload = {
      prompt,
      negative_prompt,
      steps,
      cfg_scale,
      width,
      height,
      seed,
      model,
      style_preset,
      clip_guidance_preset
    };

    fetch(`${backend}/generate-text`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
      .then(res => res.json())
      .then(data => handleResult(data, loader, gallery))
      .catch(err => handleError(err, loader));
  }

  if (currentMode === 'image') {
    if (
      !imageFile ||
      !(imageFile instanceof File) ||
      !imageFile.name ||
      imageFile.size === 0
    ) {
      loader.style.display = 'none';
      alert("Please upload a valid image for image-to-image mode.");
      return;
    }

    const formData = new FormData();
    formData.append("prompt", prompt);
    formData.append("negative_prompt", negative_prompt);
    formData.append("steps", steps);
    formData.append("cfg_scale", cfg_scale);
    formData.append("width", width);
    formData.append("height", height);
    formData.append("seed", seed);
    formData.append("model", model);
    formData.append("style_preset", style_preset);
    formData.append("image_strength", image_strength);
    formData.append("init_image", imageFile);

    fetch(`${backend}/generate-image`, {
      method: 'POST',
      body: formData
    })
      .then(res => res.json())
      .then(data => handleResult(data, loader, gallery))
      .catch(err => handleError(err, loader));
  }
}

function handleResult(data, loader, gallery) {
  loader.style.display = 'none';
  const img = document.createElement('img');

  if (data.image_url) {
    img.src = data.image_url;
  } else if (data.image_base64) {
    img.src = data.image_base64;
  } else {
    alert("No image returned.");
    return;
  }

  img.alt = 'Generated Image';
  gallery.appendChild(img);
}

function handleError(err, loader) {
  loader.style.display = 'none';
  alert('Generation failed: ' + err.message);
}
