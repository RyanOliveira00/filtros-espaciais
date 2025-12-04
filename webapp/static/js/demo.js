// Demo Page JavaScript

let currentSessionId = null;

// Elements
const dropZone = document.getElementById('dropZone');
const imageInput = document.getElementById('imageInput');
const uploadedImageDiv = document.getElementById('uploadedImage');
const step2 = document.getElementById('step2');
const step3 = document.getElementById('step3');
const processBtn = document.getElementById('processBtn');

// Noise controls
const noiseTypeRadios = document.getElementsByName('noiseType');
const saltPepperControls = document.getElementById('saltPepperControls');
const gaussianControls = document.getElementById('gaussianControls');
const saltPepperIntensity = document.getElementById('saltPepperIntensity');
const intensityValue = document.getElementById('intensityValue');
const gaussianSigma = document.getElementById('gaussianSigma');
const sigmaValue = document.getElementById('sigmaValue');

// Drop zone events
dropZone.addEventListener('click', () => imageInput.click());

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('border-purple-500');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('border-purple-500');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('border-purple-500');
    if (e.dataTransfer.files.length) {
        handleFile(e.dataTransfer.files[0]);
    }
});

imageInput.addEventListener('change', (e) => {
    if (e.target.files.length) {
        handleFile(e.target.files[0]);
    }
});

// Noise type change
noiseTypeRadios.forEach(radio => {
    radio.addEventListener('change', (e) => {
        if (e.target.value === 'salt_pepper') {
            saltPepperControls.classList.remove('hidden');
            gaussianControls.classList.add('hidden');
        } else {
            saltPepperControls.classList.add('hidden');
            gaussianControls.classList.remove('hidden');
        }
    });
});

// Sliders
saltPepperIntensity.addEventListener('input', (e) => {
    intensityValue.textContent = e.target.value;
});

gaussianSigma.addEventListener('input', (e) => {
    sigmaValue.textContent = e.target.value;
});

// Handle file upload
async function handleFile(file) {
    if (!file.type.startsWith('image/')) {
        alert('Por favor, selecione uma imagem válida');
        return;
    }

    if (file.size > 5 * 1024 * 1024) {
        alert('Imagem muito grande! Tamanho máximo: 5MB');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            currentSessionId = data.session_id;
            displayUploadedImage(data);
            showStep2();
        } else {
            alert('Erro ao fazer upload: ' + data.error);
        }
    } catch (error) {
        console.error('Erro:', error);
        alert('Erro ao fazer upload da imagem');
    }
}

function displayUploadedImage(data) {
    document.getElementById('originalPreview').src = data.image;
    document.getElementById('fileName').textContent = data.filename;
    document.getElementById('imageDims').textContent = `${data.shape[1]}×${data.shape[0]} pixels`;
    uploadedImageDiv.classList.remove('hidden');
    uploadedImageDiv.classList.add('fade-in');
}

function showStep2() {
    step2.classList.remove('hidden');
    step2.classList.add('fade-in');
    step2.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Process image
processBtn.addEventListener('click', async () => {
    if (!currentSessionId) {
        alert('Nenhuma imagem carregada!');
        return;
    }

    const noiseType = document.querySelector('input[name="noiseType"]:checked').value;
    const formData = new FormData();
    formData.append('session_id', currentSessionId);
    formData.append('noise_type', noiseType);

    if (noiseType === 'salt_pepper') {
        const intensity = parseInt(saltPepperIntensity.value) / 100;
        formData.append('salt_prob', intensity);
        formData.append('pepper_prob', intensity);
    } else {
        formData.append('gaussian_sigma', gaussianSigma.value);
    }

    // Show loading
    step3.classList.remove('hidden');
    document.getElementById('loading').classList.remove('hidden');
    document.getElementById('results').classList.add('hidden');
    step3.scrollIntoView({ behavior: 'smooth', block: 'start' });

    try {
        const response = await fetch('/api/process', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            displayResults(data);
            await loadCharts();
        } else {
            alert('Erro ao processar: ' + data.error);
        }
    } catch (error) {
        console.error('Erro:', error);
        alert('Erro ao processar imagem');
    } finally {
        document.getElementById('loading').classList.add('hidden');
    }
});

function displayResults(data) {
    // Original vs Noisy
    document.getElementById('resultOriginal').src = document.getElementById('originalPreview').src;
    document.getElementById('resultNoisy').src = data.noisy_image;
    document.getElementById('noiseTypeLabel').textContent =
        data.noise_type === 'salt_pepper' ? 'Sal e Pimenta' : 'Gaussiano';

    // Best filter
    document.getElementById('bestFilterName').textContent = data.stats.best_filter;
    document.getElementById('bestMSE').textContent = data.stats.best_mse.toFixed(4);
    document.getElementById('bestPSNR').textContent = data.stats.best_psnr.toFixed(4);

    // Filters grid
    const filtersGrid = document.getElementById('filtersGrid');
    filtersGrid.innerHTML = '';

    for (const [filterName, filterData] of Object.entries(data.filters)) {
        const filterCard = createFilterCard(filterName, filterData);
        filtersGrid.appendChild(filterCard);
    }

    // Metrics table
    const tableBody = document.getElementById('metricsTableBody');
    tableBody.innerHTML = '';

    for (const [filterName, filterData] of Object.entries(data.filters)) {
        const row = createTableRow(filterName, filterData);
        tableBody.appendChild(row);
    }

    // Export button
    document.getElementById('exportCSV').onclick = () => {
        window.location.href = `/api/export/${currentSessionId}`;
    };

    // Show results
    document.getElementById('results').classList.remove('hidden');
    document.getElementById('results').classList.add('fade-in');
}

function createFilterCard(filterName, filterData) {
    const card = document.createElement('div');
    card.className = 'bg-gray-50 rounded-lg p-4 hover:shadow-md transition';
    card.innerHTML = `
        <h3 class="font-semibold mb-2">${filterName}</h3>
        <img src="${filterData.image}" class="rounded mb-2 w-full" alt="${filterName}">
        <div class="text-sm text-gray-600">
            <p>MSE: <span class="font-semibold">${filterData.mse}</span></p>
            <p>PSNR: <span class="font-semibold">${filterData.psnr} dB</span></p>
        </div>
    `;
    return card;
}

function createTableRow(filterName, filterData) {
    const row = document.createElement('tr');
    const quality = filterData.psnr > 35 ? 'Excelente' : filterData.psnr > 30 ? 'Boa' : 'Regular';
    const qualityColor = filterData.psnr > 35 ? 'text-green-600' : filterData.psnr > 30 ? 'text-blue-600' : 'text-orange-600';

    row.innerHTML = `
        <td class="px-6 py-4 whitespace-nowrap font-medium">${filterName}</td>
        <td class="px-6 py-4 whitespace-nowrap">${filterData.mse}</td>
        <td class="px-6 py-4 whitespace-nowrap">${filterData.psnr}</td>
        <td class="px-6 py-4 whitespace-nowrap">
            <span class="${qualityColor} font-semibold">${quality}</span>
        </td>
    `;
    return row;
}

async function loadCharts() {
    try {
        const response = await fetch(`/api/charts/${currentSessionId}`);
        const data = await response.json();

        if (data.success) {
            Plotly.newPlot('chartMSE', data.charts.mse.data, data.charts.mse.layout);
            Plotly.newPlot('chartPSNR', data.charts.psnr.data, data.charts.psnr.layout);
            Plotly.newPlot('chartComparison', data.charts.comparison.data, data.charts.comparison.layout);
        }
    } catch (error) {
        console.error('Erro ao carregar gráficos:', error);
    }
}
