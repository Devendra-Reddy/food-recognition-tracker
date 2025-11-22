(function(){
  const fileInput = document.getElementById('file-input');
  const preview = document.getElementById('preview');
  const analyzeBtn = document.getElementById('btn-analyze');
  const result = document.getElementById('result');

  const camOpenBtn = document.getElementById('btn-open-camera');
  const camCancelBtn = document.getElementById('btn-cancel-camera');
  const camCaptureBtn = document.getElementById('btn-capture');
  const camPreview = document.getElementById('camera-preview');
  const camActions = document.getElementById('camera-actions');

  function setPreview(file){
    const url = URL.createObjectURL(file);
    preview.src = url;
    preview.style.display = 'block';
  }

  fileInput.addEventListener('change', () => {
    if (fileInput.files && fileInput.files[0]) {
      setPreview(fileInput.files[0]);
    }
  });

  async function openCamera(){
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' }, audio: false });
      window.__foodCamStream = stream;
      camPreview.srcObject = stream;
      camPreview.style.display = 'block';
      camActions.style.display = 'block';
    } catch (e) {
      alert('Camera access denied or not available.');
      console.error(e);
    }
  }
  function stopCamera(){
    if (window.__foodCamStream){
      window.__foodCamStream.getTracks().forEach(t=>t.stop());
      window.__foodCamStream = null;
    }
    camPreview.srcObject = null;
    camPreview.style.display = 'none';
    camActions.style.display = 'none';
  }
  async function capturePhotoToFile(){
    const canvas = document.createElement('canvas');
    const w = camPreview.videoWidth || 1280, h = camPreview.videoHeight || 720;
    const maxW = 1280, scale = Math.min(1, maxW / w);
    canvas.width = Math.round(w * scale); canvas.height = Math.round(h * scale);
    const ctx = canvas.getContext('2d');
    ctx.drawImage(camPreview, 0, 0, canvas.width, canvas.height);
    return new Promise(resolve => {
      canvas.toBlob(b => resolve(new File([b], 'camera.jpg', {type:'image/jpeg'})), 'image/jpeg', 0.92);
    });
  }

  camOpenBtn.addEventListener('click', openCamera);
  camCancelBtn.addEventListener('click', stopCamera);
  camCaptureBtn.addEventListener('click', async () => {
    const file = await capturePhotoToFile();
    stopCamera();
    const dt = new DataTransfer();
    dt.items.add(file);
    fileInput.files = dt.files;
    setPreview(file);
  });

  function buildFormData(file){
    const fd = new FormData();
    fd.append('file', file);
    const mm = document.getElementById('use-multimodel-checkbox');
    fd.append('use_multi_model', mm && mm.checked ? 'true' : 'false');
    const qv = document.getElementById('quantity-value').value;
    const qu = document.getElementById('quantity-unit').value;
    if (qv) fd.append('quantity_value', qv);
    if (qu) fd.append('quantity_unit', qu);
    return fd;
  }

  async function analyze(){
    const f = fileInput.files && fileInput.files[0];
    if (!f) { alert('Please select or capture an image first.'); return; }
    analyzeBtn.disabled = true; result.textContent = 'Analyzing…';
    try {
      const fd = buildFormData(f);
      const res = await fetch('/analyze', { method:'POST', body: fd });
      const j = await res.json();
      result.textContent = JSON.stringify(j, null, 2);
      // preview dashboard JSON short
      try {
        const dres = await fetch('/api/agent-dashboard/data'); 
        const dj = await dres.json();
        document.getElementById('dashboard-preview').textContent = JSON.stringify(dj, null, 2);
      } catch {}
    } catch (e) {
      result.textContent = 'Error: ' + e.message;
    } finally {
      analyzeBtn.disabled = false;
    }
  }
  analyzeBtn.addEventListener('click', analyze);

  document.getElementById('btn-refresh-dashboard').addEventListener('click', async () => {
    const dres = await fetch('/api/agent-dashboard/data');
    const dj = await dres.json();
    document.getElementById('dashboard-preview').textContent = JSON.stringify(dj, null, 2);
  });
})();
