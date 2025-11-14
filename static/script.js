const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const previewSection = document.getElementById('previewSection');
const previewImage = document.getElementById('previewImage');
const resultsSection = document.getElementById('resultsSection');
const loading = document.getElementById('loading');
const error = document.getElementById('error');
const resultLabel = document.getElementById('resultLabel');
const confidenceFill = document.getElementById('confidenceFill');
const confidenceText = document.getElementById('confidenceText');
const explanation = document.getElementById('explanation');
const usernameElement = document.getElementById('username');
const logoutBtn = document.getElementById('logoutBtn');

async function fetchUser() {
    try {
        const response = await fetch('/api/user');
        if (response.ok) {
            const data = await response.json();
            usernameElement.textContent = `Welcome, ${data.username}`;
        }
    } catch (err) {
        console.error('Error fetching user:', err);
    }
}

logoutBtn.addEventListener('click', async () => {
    try {
        const response = await fetch('/api/logout', { method: 'POST' });
        if (response.ok) {
            window.location.href = '/login';
        }
    } catch (err) {
        console.error('Error logging out:', err);
    }
});

fetchUser();

uploadArea.addEventListener('click', () => fileInput.click());

uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFile(e.target.files[0]);
    }
});

function handleFile(file) {
    if (!file.type.startsWith('image/')) {
        showError('Please upload an image file');
        return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
        previewImage.src = e.target.result;
        previewSection.style.display = 'block';
        resultsSection.style.display = 'none';
        error.style.display = 'none';
    };
    reader.readAsDataURL(file);

    uploadImage(file);
}

async function uploadImage(file) {
    loading.style.display = 'block';
    resultsSection.style.display = 'none';
    error.style.display = 'none';

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/predict', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Error analyzing image');
        }

        displayResults(data);
    } catch (err) {
        showError(err.message);
    } finally {
        loading.style.display = 'none';
    }
}

function displayResults(data) {
    resultLabel.textContent = data.label;
    resultLabel.className = 'result-label ' + data.label.toLowerCase();
    
    confidenceFill.style.width = data.confidence + '%';
    confidenceFill.textContent = data.confidence + '%';
    confidenceText.textContent = `Confidence: ${data.confidence}%`;
    
    explanation.textContent = data.explanation;
    
    resultsSection.style.display = 'block';
}

function showError(message) {
    error.textContent = message;
    error.style.display = 'block';
    loading.style.display = 'none';
}
