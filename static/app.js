// OmniVoice Studio - Frontend Controller
let currentModel = 'kokoro-82m';
let mediaRecorder = null;
let recordedChunks = [];

document.addEventListener('DOMContentLoaded', () => {
  initSystemInfo();
  initModels();
  initSamples();
  initHistory();
  initEventListeners();
});

// Fetch hardware & system telemetry
async function initSystemInfo() {
  try {
    const res = await fetch('/api/system');
    const data = await res.json();
    document.getElementById('hwText').innerHTML = `${data.arch} &bull; ${data.ram_available_gb}GB / ${data.ram_total_gb}GB RAM &bull; MPS: ${data.mps_available ? 'Active' : 'Off'}`;
    document.getElementById('diskText').innerText = `Storage: ${data.project_disk_free_gb} GB Free`;
  } catch (err) {
    console.error('Failed to load system info:', err);
  }
}

// Fetch available models and voices
async function initModels() {
  try {
    const res = await fetch('/api/models');
    const data = await res.json();

    // Populate Kokoro voices
    const kokoro = data.models.find(m => m.id === 'kokoro-82m');
    if (kokoro && kokoro.voices) {
      const kokoroVoiceSelect = document.getElementById('kokoroVoice');
      const kokoroBlendSelect = document.getElementById('kokoroBlendVoice');
      kokoroVoiceSelect.innerHTML = '';
      kokoroBlendSelect.innerHTML = '';

      Object.entries(kokoro.voices).forEach(([id, name]) => {
        const opt1 = new Option(name, id);
        const opt2 = new Option(name, id);
        if (id === 'af_bella') opt1.selected = true;
        if (id === 'af_sarah') opt2.selected = true;
        kokoroVoiceSelect.appendChild(opt1);
        kokoroBlendSelect.appendChild(opt2);
      });
    }

    // Populate Piper voices
    const piper = data.models.find(m => m.id === 'piper');
    if (piper && piper.voices) {
      const piperVoiceSelect = document.getElementById('piperVoice');
      piperVoiceSelect.innerHTML = '';
      piper.voices.forEach(v => {
        const label = `${v.name} ${v.installed ? '' : '(Not downloaded)'}`;
        const opt = new Option(label, v.id);
        if (v.id === 'ru_RU-denis-medium') opt.selected = true;
        piperVoiceSelect.appendChild(opt);
      });
    }

    // Populate Silero speakers
    const silero = data.models.find(m => m.id === 'silero');
    if (silero && silero.voices) {
      const sileroSpeakerSelect = document.getElementById('sileroSpeaker');
      sileroSpeakerSelect.innerHTML = '';
      Object.entries(silero.voices).forEach(([id, name]) => {
        const opt = new Option(name, id);
        if (id === 'aidar') opt.selected = true;
        sileroSpeakerSelect.appendChild(opt);
      });
    }

    // Update model status dots
    data.models.forEach(m => {
      const card = document.querySelector(`.model-card[data-model="${m.id}"]`);
      if (card) {
        const dot = card.querySelector('.status-indicator');
        if (dot) {
          dot.className = m.installed ? 'status-indicator ready' : 'status-indicator missing';
          dot.title = m.installed ? 'Ready to synthesize' : 'Weights not yet downloaded';
        }
      }
    });

  } catch (err) {
    console.error('Failed to load models:', err);
  }
}

// Fetch reference samples for XTTS and Fish Speech
async function initSamples() {
  try {
    const res = await fetch('/api/samples');
    const data = await res.json();
    const xttsSelect = document.getElementById('xttsSpeakerWav');
    const fishSelect = document.getElementById('fishSpeakerWav');
    xttsSelect.innerHTML = '';
    fishSelect.innerHTML = '';

    const defaultNone = new Option('-- No Reference Voice (Default) --', '');
    fishSelect.appendChild(defaultNone);

    data.samples.forEach(s => {
      const opt1 = new Option(`${s.filename} (${s.size_kb} KB)`, s.filename);
      const opt2 = new Option(`${s.filename} (${s.size_kb} KB)`, s.filename);
      if (s.filename.includes('female_en')) opt1.selected = true;
      xttsSelect.appendChild(opt1);
      fishSelect.appendChild(opt2);
    });
  } catch (err) {
    console.error('Failed to load samples:', err);
  }
}

// Fetch recent generation history
async function initHistory() {
  try {
    const res = await fetch('/api/history');
    const data = await res.json();
    const tbody = document.getElementById('historyTableBody');

    if (!data.history || data.history.length === 0) {
      tbody.innerHTML = '<tr><td colspan="6" class="empty-state">No audio generated yet. Enter text above and click Synthesize.</td></tr>';
      return;
    }

    tbody.innerHTML = '';
    data.history.forEach(item => {
      const tr = document.createElement('tr');
      const timeStr = item.formatted_date ? item.formatted_date.split(' ')[1] : '--';
      const textPreview = item.text.length > 50 ? item.text.substring(0, 50) + '...' : item.text;
      
      tr.innerHTML = `
        <td style="font-family: 'JetBrains Mono', monospace; font-size: 0.75rem;">${timeStr}</td>
        <td><span class="card-badge onnx">${item.model}</span></td>
        <td title="${escapeHtml(item.text)}">${escapeHtml(textPreview)}</td>
        <td>${item.duration}s</td>
        <td><span style="color: var(--accent-cyan); font-family: 'JetBrains Mono';">${item.rtf}x</span></td>
        <td>
          <button class="chip-btn play-hist-btn" data-url="${item.url}">Play</button>
          <a href="${item.url}" download="${item.filename}" class="chip-btn" style="text-decoration: none;">Download</a>
        </td>
      `;
      tbody.appendChild(tr);
    });

    // Wire play buttons
    document.querySelectorAll('.play-hist-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const url = e.target.getAttribute('data-url');
        playAudio(url, 'History Playback');
      });
    });

  } catch (err) {
    console.error('Failed to load history:', err);
  }
}

function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

function playAudio(url, metaTitle = '') {
  const playerCard = document.getElementById('playerCard');
  const audioElement = document.getElementById('audioElement');
  const downloadBtn = document.getElementById('downloadAudioBtn');
  const metaPill = document.getElementById('genMetaPill');

  playerCard.style.display = 'block';
  audioElement.src = url;
  audioElement.play().catch(e => console.log('Autoplay deferred:', e));
  downloadBtn.href = url;
  if (metaTitle) {
    metaPill.innerText = metaTitle;
  }
  playerCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Wire up event listeners
function initEventListeners() {
  // Model Card Switching
  document.querySelectorAll('.model-card').forEach(card => {
    card.addEventListener('click', () => {
      document.querySelectorAll('.model-card').forEach(c => c.classList.remove('active'));
      card.classList.add('active');
      const modelId = card.getAttribute('data-model');
      switchModel(modelId);
    });
  });

  // Textarea char count
  const textarea = document.getElementById('textInput');
  const charCount = document.getElementById('charCount');
  textarea.addEventListener('input', () => {
    charCount.innerText = textarea.value.length;
  });

  // Slider value badges
  bindSlider('kokoroSpeed', 'kokoroSpeedVal', 'x');
  bindSlider('kokoroBlendRatio', 'kokoroBlendRatioVal', '', (v) => `${Math.round((1 - v) * 100)}% / ${Math.round(v * 100)}%`);
  bindSlider('piperSpeed', 'piperSpeedVal', 'x');
  bindSlider('piperNoise', 'piperNoiseVal', '');
  bindSlider('piperNoiseW', 'piperNoiseWVal', '');
  bindSlider('sileroSpeed', 'sileroSpeedVal', 'x');
  bindSlider('xttsTemp', 'xttsTempVal', '');
  bindSlider('xttsRep', 'xttsRepVal', '');
  bindSlider('xttsTopP', 'xttsTopPVal', '');
  bindSlider('xttsSpeed', 'xttsSpeedVal', 'x');
  bindSlider('fishTemp', 'fishTempVal', '');
  bindSlider('fishTopP', 'fishTopPVal', '');
  bindSlider('fishSpeed', 'fishSpeedVal', 'x');

  // Kokoro Voice Mix Toggle
  const kokoroMixToggle = document.getElementById('kokoroMixToggle');
  const kokoroMixControls = document.getElementById('kokoroMixControls');
  kokoroMixToggle.addEventListener('change', () => {
    kokoroMixControls.style.display = kokoroMixToggle.checked ? 'block' : 'none';
  });

  // Presets
  document.getElementById('presetEnBtn').addEventListener('click', () => {
    textarea.value = "Welcome to OmniVoice Studio! This local neural speech engine combines Kokoro, Piper, Silero, and XTTS running natively on Apple Silicon.";
    charCount.innerText = textarea.value.length;
  });

  document.getElementById('presetRuBtn').addEventListener('click', () => {
    textarea.value = "Привет! Это локальный комбайн синтеза речи с быстрым переключением между моделями на русском и английском языках.";
    charCount.innerText = textarea.value.length;
    if (currentModel === 'kokoro-82m') {
      switchModel('piper');
    }
  });

  document.getElementById('presetAccentBtn').addEventListener('click', () => {
    textarea.value = "Замок на двери был надёжно закрыт, а вдали на холме возвышался старинный замок.";
    charCount.innerText = textarea.value.length;
    switchModel('silero');
  });

  // Emotion chip insertion
  document.querySelectorAll('.emotion-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      const tag = chip.getAttribute('data-tag');
      insertAtCursor(textarea, tag + ' ');
      charCount.innerText = textarea.value.length;
    });
  });

  // Auto-Accentuate button
  document.getElementById('autoAccentBtn').addEventListener('click', async () => {
    const text = textarea.value.trim();
    if (!text) return;
    const btn = document.getElementById('autoAccentBtn');
    btn.disabled = true;
    btn.innerHTML = '<span>Processing accents...</span>';

    try {
      // Synthesize with auto_accent=true returns processed text in metadata
      const res = await fetch('/api/tts/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model: 'silero',
          text: text,
          auto_accent: true
        })
      });
      const data = await res.json();
      if (data.success && data.data.processed_text) {
        textarea.value = data.data.processed_text;
        charCount.innerText = textarea.value.length;
        playAudio(data.data.url, `Silero Accents &bull; ${data.data.duration}s`);
        initHistory();
      }
    } catch (err) {
      alert('Error accenting text: ' + err.message);
    } finally {
      btn.disabled = false;
      btn.innerHTML = `<svg viewBox="0 0 24 24" width="14" height="14" stroke="currentColor" stroke-width="2" fill="none"><path d="m5 13 4 4L19 7"/></svg><span>Auto-Accentuate Russian Stresses (+)</span>`;
    }
  });

  // Synthesize Button
  document.getElementById('synthesizeBtn').addEventListener('click', handleSynthesize);

  // Refresh history
  document.getElementById('refreshHistoryBtn').addEventListener('click', initHistory);

  // Sample Upload
  const fileInput = document.getElementById('sampleFileInput');
  document.getElementById('uploadSampleBtn').addEventListener('click', () => fileInput.click());
  fileInput.addEventListener('change', handleSampleUpload);

  // Microphone Recording
  const micBtn = document.getElementById('micRecordBtn');
  const stopBtn = document.getElementById('stopRecBtn');
  micBtn.addEventListener('click', startRecording);
  stopBtn.addEventListener('click', stopRecording);
}

function switchModel(modelId) {
  currentModel = modelId;

  // Update card active styles
  document.querySelectorAll('.model-card').forEach(c => {
    if (c.getAttribute('data-model') === modelId) {
      c.classList.add('active');
    } else {
      c.classList.remove('active');
    }
  });

  // Update active badge title
  const names = {
    'kokoro-82m': 'Kokoro-82M',
    'piper': 'Piper TTS',
    'silero': 'Silero TTS v4',
    'xtts-v2': 'Coqui XTTS-v2',
    'fish-speech': 'Fish Speech',
  };
  document.getElementById('activeEngineBadge').innerText = names[modelId] || modelId;

  // Toggle engine settings panels
  document.querySelectorAll('.engine-panel').forEach(p => p.style.display = 'none');
  const targetPanel = document.getElementById(`panel-${modelId}`);
  if (targetPanel) targetPanel.style.display = 'block';

  // Toggle emotion tags bar
  document.getElementById('emotionTagsBar').style.display = (modelId === 'fish-speech') ? 'flex' : 'none';

  // Toggle accent bar
  document.getElementById('accentBar').style.display = (modelId === 'silero') ? 'flex' : 'none';
}

function bindSlider(sliderId, badgeId, suffix = '', formatter = null) {
  const slider = document.getElementById(sliderId);
  const badge = document.getElementById(badgeId);
  if (!slider || !badge) return;

  slider.addEventListener('input', () => {
    if (formatter) {
      badge.innerText = formatter(parseFloat(slider.value));
    } else {
      badge.innerText = `${slider.value}${suffix}`;
    }
  });
}

function insertAtCursor(myField, myValue) {
  if (myField.selectionStart || myField.selectionStart === 0) {
    var startPos = myField.selectionStart;
    var endPos = myField.selectionEnd;
    myField.value = myField.value.substring(0, startPos) + myValue + myField.value.substring(endPos, myField.value.length);
    myField.selectionStart = startPos + myValue.length;
    myField.selectionEnd = startPos + myValue.length;
  } else {
    myField.value += myValue;
  }
  myField.focus();
}

async function handleSynthesize() {
  const text = document.getElementById('textInput').value.trim();
  if (!text) {
    alert('Please enter some text to synthesize.');
    return;
  }

  const synthBtn = document.getElementById('synthesizeBtn');
  const synthText = document.getElementById('synthText');
  const synthIcon = document.getElementById('synthIcon');

  synthBtn.disabled = true;
  synthText.innerText = 'Synthesizing...';

  const startTime = Date.now();
  const timerInterval = setInterval(() => {
    const sec = ((Date.now() - startTime) / 1000).toFixed(1);
    synthText.innerText = `Synthesizing (${sec}s)...`;
  }, 200);

  // Construct payload according to active model
  const payload = {
    model: currentModel,
    text: text
  };

  if (currentModel === 'kokoro-82m') {
    payload.voice = document.getElementById('kokoroVoice').value;
    payload.lang = document.getElementById('kokoroLang').value;
    payload.speed = parseFloat(document.getElementById('kokoroSpeed').value);
    if (document.getElementById('kokoroMixToggle').checked) {
      payload.blend_voice = document.getElementById('kokoroBlendVoice').value;
      payload.blend_ratio = parseFloat(document.getElementById('kokoroBlendRatio').value);
    }
  } else if (currentModel === 'piper') {
    payload.voice_id = document.getElementById('piperVoice').value;
    payload.speed = parseFloat(document.getElementById('piperSpeed').value);
    payload.noise_scale = parseFloat(document.getElementById('piperNoise').value);
    payload.noise_w_scale = parseFloat(document.getElementById('piperNoiseW').value);
  } else if (currentModel === 'silero') {
    payload.speaker = document.getElementById('sileroSpeaker').value;
    payload.sample_rate = parseInt(document.getElementById('sileroSampleRate').value);
    payload.auto_accent = document.getElementById('sileroAutoAccent').checked;
    payload.speed = parseFloat(document.getElementById('sileroSpeed').value);
  } else if (currentModel === 'xtts-v2') {
    payload.speaker_wav = document.getElementById('xttsSpeakerWav').value;
    payload.language = document.getElementById('xttsLang').value;
    payload.temperature = parseFloat(document.getElementById('xttsTemp').value);
    payload.repetition_penalty = parseFloat(document.getElementById('xttsRep').value);
    payload.top_p = parseFloat(document.getElementById('xttsTopP').value);
    payload.speed = parseFloat(document.getElementById('xttsSpeed').value);
  } else if (currentModel === 'fish-speech') {
    payload.speaker_wav = document.getElementById('fishSpeakerWav').value || null;
    payload.temperature = parseFloat(document.getElementById('fishTemp').value);
    payload.top_p = parseFloat(document.getElementById('fishTopP').value);
    payload.speed = parseFloat(document.getElementById('fishSpeed').value);
  }

  try {
    const res = await fetch('/api/tts/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    const data = await res.json();
    clearInterval(timerInterval);

    if (!res.ok || !data.success) {
      throw new Error(data.detail || 'Synthesis failed');
    }

    const r = data.data;
    const metaTitle = `${r.model.toUpperCase()} &bull; Duration: ${r.duration}s &bull; RTF: ${r.rtf}x &bull; Gen: ${r.elapsed_time}s`;
    playAudio(r.url, metaTitle);
    initHistory();
  } catch (err) {
    clearInterval(timerInterval);
    alert('Synthesis error: ' + err.message);
  } finally {
    synthBtn.disabled = false;
    synthText.innerText = 'Synthesize Speech';
  }
}

// Upload custom sample
async function handleSampleUpload(e) {
  const file = e.target.files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append('file', file);

  try {
    const res = await fetch('/api/samples/upload', {
      method: 'POST',
      body: formData
    });
    const data = await res.json();
    if (data.success) {
      await initSamples();
      document.getElementById('xttsSpeakerWav').value = data.filename;
      alert(`Voice sample uploaded successfully: ${data.filename}`);
    } else {
      alert('Upload failed: ' + data.detail);
    }
  } catch (err) {
    alert('Upload error: ' + err.message);
  }
}

// Microphone recording for voice cloning
async function startRecording() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    recordedChunks = [];
    mediaRecorder = new MediaRecorder(stream);
    
    mediaRecorder.ondataavailable = e => {
      if (e.data.size > 0) recordedChunks.push(e.data);
    };

    mediaRecorder.onstop = async () => {
      const blob = new Blob(recordedChunks, { type: 'audio/wav' });
      const file = new File([blob], `mic_sample_${Date.now()}.wav`, { type: 'audio/wav' });
      const formData = new FormData();
      formData.append('file', file);

      const res = await fetch('/api/samples/upload', {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      if (data.success) {
        await initSamples();
        document.getElementById('xttsSpeakerWav').value = data.filename;
        alert(`Microphone audio recorded and ready for cloning!`);
      }
      stream.getTracks().forEach(t => t.stop());
    };

    mediaRecorder.start();
    document.getElementById('recordingStatus').style.display = 'flex';
  } catch (err) {
    alert('Microphone access error: ' + err.message);
  }
}

function stopRecording() {
  if (mediaRecorder && mediaRecorder.state !== 'inactive') {
    mediaRecorder.stop();
    document.getElementById('recordingStatus').style.display = 'none';
  }
}
