/**
 * Ergonomic Posture Analysis System
 * Main Application JavaScript
 */

// DOM Elements
const elements = {
    uploadArea: document.getElementById('upload-area'),
    fileInput: document.getElementById('file-input'),
    previewContainer: document.getElementById('preview-container'),
    previewImage: document.getElementById('preview-image'),
    clearBtn: document.getElementById('clear-btn'),
    analyzeBtn: document.getElementById('analyze-btn'),

    uploadSection: document.getElementById('upload-section'),
    resultsSection: document.getElementById('results-section'),

    loadingOverlay: document.getElementById('loading-overlay'),
    loadingStatus: document.getElementById('loading-status'),

    // Score elements
    rulaScore: document.getElementById('rula-score'),
    rulaActionLevel: document.getElementById('rula-action-level'),
    rulaDescription: document.getElementById('rula-description'),
    rulaCard: document.getElementById('rula-card'),

    rebaScore: document.getElementById('reba-score'),
    rebaRiskLevel: document.getElementById('reba-risk-level'),
    rebaDescription: document.getElementById('reba-description'),
    rebaCard: document.getElementById('reba-card'),

    warningBanner: document.getElementById('warning-banner'),
    warningText: document.getElementById('warning-text'),
    riskStatement: document.getElementById('risk-statement'),

    annotatedImage: document.getElementById('annotated-image'),
    anglesGrid: document.getElementById('angles-grid'),
    rulaDetails: document.getElementById('rula-details'),
    rebaDetails: document.getElementById('reba-details'),
    recommendations: document.getElementById('recommendations'),

    newAnalysisBtn: document.getElementById('new-analysis-btn'),
    downloadPdfBtn: document.getElementById('download-pdf-btn')
};

// State
let currentFile = null;
let analysisResult = null;

// Initialize
document.addEventListener('DOMContentLoaded', init);

function init() {
    setupEventListeners();
    setupTabs();
    setupSettings();
    loadTheme();
    setupPWA();
}

// =========================================
// PWA FUNCTIONALITY
// =========================================

let deferredPrompt = null;

function setupPWA() {
    // Register service worker
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/static/sw.js')
            .then((registration) => {
                console.log('Service Worker registered:', registration.scope);
            })
            .catch((error) => {
                console.log('Service Worker registration failed:', error);
            });
    }

    // Handle install prompt
    window.addEventListener('beforeinstallprompt', (e) => {
        e.preventDefault();
        deferredPrompt = e;
        showInstallButton();
    });

    // Handle successful install
    window.addEventListener('appinstalled', () => {
        console.log('ErgoAssess installed successfully!');
        hideInstallButton();
        deferredPrompt = null;
    });
}

function showInstallButton() {
    // Create install button if it doesn't exist
    if (!document.getElementById('install-btn')) {
        const headerActions = document.querySelector('.header-actions');
        if (headerActions) {
            const installBtn = document.createElement('button');
            installBtn.id = 'install-btn';
            installBtn.className = 'settings-btn';
            installBtn.title = 'Install App';
            installBtn.innerHTML = `
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                    <polyline points="7 10 12 15 17 10"/>
                    <line x1="12" y1="15" x2="12" y2="3"/>
                </svg>
            `;
            installBtn.addEventListener('click', installApp);
            headerActions.insertBefore(installBtn, headerActions.firstChild);
        }
    }
}

function hideInstallButton() {
    const installBtn = document.getElementById('install-btn');
    if (installBtn) {
        installBtn.remove();
    }
}

async function installApp() {
    if (!deferredPrompt) {
        alert('App is already installed or cannot be installed on this device.');
        return;
    }

    deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;

    if (outcome === 'accepted') {
        console.log('User accepted the install prompt');
    } else {
        console.log('User dismissed the install prompt');
    }

    deferredPrompt = null;
}

function setupEventListeners() {
    // Upload area click
    elements.uploadArea.addEventListener('click', () => {
        elements.fileInput.click();
    });

    // File input change
    elements.fileInput.addEventListener('change', handleFileSelect);

    // Drag and drop
    elements.uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        elements.uploadArea.classList.add('dragover');
    });

    elements.uploadArea.addEventListener('dragleave', () => {
        elements.uploadArea.classList.remove('dragover');
    });

    elements.uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        elements.uploadArea.classList.remove('dragover');

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFile(files[0]);
        }
    });

    // Clear button
    elements.clearBtn.addEventListener('click', clearImage);

    // Analyze button
    elements.analyzeBtn.addEventListener('click', analyzePosture);

    // New analysis button
    elements.newAnalysisBtn.addEventListener('click', resetToUpload);

    // Download PDF button
    elements.downloadPdfBtn.addEventListener('click', downloadPDF);
}

function setupTabs() {
    const tabs = document.querySelectorAll('.tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // Remove active from all tabs and contents
            tabs.forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

            // Add active to clicked tab and corresponding content
            tab.classList.add('active');
            const tabId = `tab-${tab.dataset.tab}`;
            document.getElementById(tabId).classList.add('active');
        });
    });
}

function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        handleFile(file);
    }
}

function handleFile(file) {
    // Validate file type
    const validTypes = ['image/jpeg', 'image/jpg', 'image/png'];
    if (!validTypes.includes(file.type)) {
        alert('Please upload a JPEG or PNG image.');
        return;
    }

    // Validate file size (16MB max)
    if (file.size > 16 * 1024 * 1024) {
        alert('File size must be less than 16MB.');
        return;
    }

    currentFile = file;

    // Show preview
    const reader = new FileReader();
    reader.onload = (e) => {
        elements.previewImage.src = e.target.result;
        elements.uploadArea.style.display = 'none';
        elements.previewContainer.style.display = 'block';
        elements.analyzeBtn.disabled = false;
    };
    reader.readAsDataURL(file);
}

function clearImage() {
    currentFile = null;
    elements.previewImage.src = '';
    elements.previewContainer.style.display = 'none';
    elements.uploadArea.style.display = 'block';
    elements.analyzeBtn.disabled = true;
    elements.fileInput.value = '';
}

async function analyzePosture() {
    if (!currentFile) return;

    // Show loading
    showLoading('Initializing analysis...');

    // Prepare form data
    const formData = new FormData();
    formData.append('image', currentFile);
    formData.append('is_static', document.getElementById('is-static').checked);
    formData.append('is_repetitive', document.getElementById('is-repetitive').checked);
    formData.append('load_kg', document.getElementById('load-weight').value);
    formData.append('coupling', document.getElementById('coupling').value);

    try {
        updateLoadingStatus('Detecting pose landmarks...');

        const response = await fetch('/api/analyze', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || 'Analysis failed');
        }

        updateLoadingStatus('Processing results...');

        analysisResult = result;
        displayResults(result);

    } catch (error) {
        console.error('Analysis error:', error);
        alert('Analysis failed: ' + error.message);
    } finally {
        hideLoading();
    }
}

function displayResults(result) {
    // Hide upload, show results
    elements.uploadSection.style.display = 'none';
    elements.resultsSection.style.display = 'block';

    // RULA Score
    elements.rulaScore.textContent = result.rula.score;
    elements.rulaScore.style.color = result.rula.color;
    elements.rulaActionLevel.textContent = `Action Level ${result.rula.action_level}`;
    elements.rulaActionLevel.style.backgroundColor = result.rula.color;
    elements.rulaActionLevel.style.color = 'white';
    elements.rulaDescription.textContent = result.rula.action_description;

    // REBA Score
    elements.rebaScore.textContent = result.reba.score;
    elements.rebaScore.style.color = result.reba.color;
    elements.rebaRiskLevel.textContent = `${result.reba.risk_level} Risk`;
    elements.rebaRiskLevel.style.backgroundColor = result.reba.color;
    elements.rebaRiskLevel.style.color = 'white';
    elements.rebaDescription.textContent = result.reba.risk_description;

    // Warning banner
    if (result.warning) {
        elements.warningBanner.style.display = 'flex';
        elements.warningText.textContent = result.warning;
    } else {
        elements.warningBanner.style.display = 'none';
    }

    // Risk statement
    elements.riskStatement.textContent = result.recommendations.overall_risk_statement;

    // Annotated image
    elements.annotatedImage.src = result.annotated_image;

    // Populate angles
    displayAngles(result.angles);

    // Populate RULA details
    displayRULADetails(result.rula);

    // Populate REBA details
    displayREBADetails(result.reba);

    // Populate recommendations
    displayRecommendations(result.recommendations);

    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function displayAngles(angles) {
    let html = '';

    for (const [region, values] of Object.entries(angles)) {
        if (typeof values === 'object') {
            html += `
                <div class="angle-group">
                    <h4>${region.replace(/_/g, ' ')}</h4>
            `;

            for (const [key, value] of Object.entries(values)) {
                let displayValue;
                if (typeof value === 'boolean') {
                    displayValue = value ? 'Yes' : 'No';
                } else if (typeof value === 'number') {
                    displayValue = `${value.toFixed(1)}°`;
                } else {
                    displayValue = value;
                }

                html += `
                    <div class="angle-item">
                        <span class="angle-name">${key.replace(/_/g, ' ')}</span>
                        <span class="angle-value">${displayValue}</span>
                    </div>
                `;
            }

            html += '</div>';
        }
    }

    elements.anglesGrid.innerHTML = html;
}

function displayRULADetails(rula) {
    const components = rula.details.components;
    let html = '';

    // Group A
    html += `
        <div class="detail-section">
            <h4>Group A - Upper Limb (Score A: ${rula.details.group_scores.score_a})</h4>
    `;

    for (const part of ['upper_arm', 'lower_arm', 'wrist', 'wrist_twist']) {
        if (components[part]) {
            html += createDetailItem(part, components[part]);
        }
    }

    html += `
            <div class="detail-text">
                <strong>Table A:</strong> ${rula.details.group_scores.score_a_raw} + 
                Muscle Use: ${rula.details.modifiers.muscle_use_a} + 
                Force: ${rula.details.modifiers.force_load_a} = ${rula.details.group_scores.score_a}
            </div>
        </div>
    `;

    // Group B
    html += `
        <div class="detail-section">
            <h4>Group B - Neck/Trunk/Legs (Score B: ${rula.details.group_scores.score_b})</h4>
    `;

    for (const part of ['neck', 'trunk', 'legs']) {
        if (components[part]) {
            html += createDetailItem(part, components[part]);
        }
    }

    html += `
            <div class="detail-text">
                <strong>Table B:</strong> ${rula.details.group_scores.score_b_raw} + 
                Muscle Use: ${rula.details.modifiers.muscle_use_b} + 
                Force: ${rula.details.modifiers.force_load_b} = ${rula.details.group_scores.score_b}
            </div>
        </div>
    `;

    // Justifications
    html += `
        <div class="detail-section">
            <h4>Score Justifications</h4>
    `;

    for (const [part, just] of Object.entries(rula.justifications)) {
        html += `
            <div class="detail-text">
                <strong>${part.replace(/_/g, ' ').toUpperCase()}:</strong> ${just.detailed_reasoning}
            </div>
        `;
    }

    html += '</div>';

    elements.rulaDetails.innerHTML = html;
}

function displayREBADetails(reba) {
    const groupA = reba.details.group_a;
    const groupB = reba.details.group_b;
    let html = '';

    // Group A
    html += `
        <div class="detail-section">
            <h4>Group A - Trunk/Neck/Legs (Score A: ${groupA.score_a})</h4>
    `;

    for (const part of ['trunk', 'neck', 'legs']) {
        if (groupA[part]) {
            html += createDetailItem(part, groupA[part]);
        }
    }

    html += `
            <div class="detail-text">
                <strong>Table A:</strong> ${groupA.score_a_raw} + 
                Load/Force: ${groupA.load_force} = ${groupA.score_a}
            </div>
        </div>
    `;

    // Group B
    html += `
        <div class="detail-section">
            <h4>Group B - Arms/Wrist (Score B: ${groupB.score_b})</h4>
    `;

    for (const part of ['upper_arm', 'lower_arm', 'wrist']) {
        if (groupB[part]) {
            html += createDetailItem(part, groupB[part]);
        }
    }

    html += `
            <div class="detail-text">
                <strong>Table B:</strong> ${groupB.score_b_raw} + 
                Coupling: ${groupB.coupling} = ${groupB.score_b}
            </div>
        </div>
    `;

    // Final calculation
    html += `
        <div class="detail-section">
            <h4>Final Score Calculation</h4>
            <div class="detail-text">
                <strong>Table C Score:</strong> ${reba.details.score_c}<br>
                <strong>Activity Score:</strong> +${reba.details.activity_score}<br>
                <strong>Final REBA Score:</strong> ${reba.details.final_score}
            </div>
        </div>
    `;

    elements.rebaDetails.innerHTML = html;
}

function createDetailItem(name, data) {
    return `
        <div class="detail-text">
            <span class="detail-score">${data.final_score}</span>
            <strong>${name.replace(/_/g, ' ')}:</strong> 
            ${data.threshold} 
            ${data.modifiers && data.modifiers.length > 0 ? `(${data.modifiers.join(', ')})` : ''}
        </div>
    `;
}

function displayRecommendations(recommendations) {
    let html = '';

    // Immediate actions
    if (recommendations.immediate_actions && recommendations.immediate_actions.length > 0) {
        html += `
            <div class="recommendation-section" style="border-left: 4px solid var(--color-danger);">
                <h4>🚨 Immediate Actions Required</h4>
        `;

        for (const rec of recommendations.immediate_actions) {
            html += createRecommendationItem(rec);
        }

        html += '</div>';
    }

    // Short-term actions
    if (recommendations.short_term_actions && recommendations.short_term_actions.length > 0) {
        html += `
            <div class="recommendation-section" style="border-left: 4px solid var(--color-warning);">
                <h4>⚠️ Short-Term Improvements (1-2 weeks)</h4>
        `;

        for (const rec of recommendations.short_term_actions.slice(0, 5)) {
            html += createRecommendationItem(rec);
        }

        html += '</div>';
    }

    // Long-term actions
    if (recommendations.long_term_actions && recommendations.long_term_actions.length > 0) {
        html += `
            <div class="recommendation-section" style="border-left: 4px solid var(--color-info);">
                <h4>📋 Long-Term Considerations</h4>
        `;

        for (const rec of recommendations.long_term_actions) {
            html += createRecommendationItem(rec);
        }

        html += '</div>';
    }

    // Workstation adjustments
    if (recommendations.workstation_adjustments && recommendations.workstation_adjustments.length > 0) {
        html += `
            <div class="recommendation-section" style="border-left: 4px solid var(--color-primary);">
                <h4>🖥️ Workstation Adjustments</h4>
        `;

        for (const rec of recommendations.workstation_adjustments) {
            html += createRecommendationItem(rec);
        }

        html += '</div>';
    }

    // Monitoring plan
    if (recommendations.monitoring_plan) {
        html += `
            <div class="monitoring-plan">
                <h4>📅 Monitoring Plan</h4>
                <p>${recommendations.monitoring_plan}</p>
            </div>
        `;
    }

    elements.recommendations.innerHTML = html;
}

function createRecommendationItem(rec) {
    let actionsHtml = '';
    if (rec.actions && rec.actions.length > 0) {
        actionsHtml = '<ul class="recommendation-actions">';
        for (const action of rec.actions.slice(0, 4)) {
            actionsHtml += `<li>${action}</li>`;
        }
        actionsHtml += '</ul>';
    }

    return `
        <div class="recommendation-item">
            <div class="recommendation-title">${rec.title}</div>
            <div class="recommendation-description">${rec.description}</div>
            ${actionsHtml}
        </div>
    `;
}

function resetToUpload() {
    elements.resultsSection.style.display = 'none';
    elements.uploadSection.style.display = 'block';
    clearImage();
    analysisResult = null;

    // Reset tabs
    document.querySelectorAll('.tab').forEach((t, i) => {
        t.classList.toggle('active', i === 0);
    });
    document.querySelectorAll('.tab-content').forEach((c, i) => {
        c.classList.toggle('active', i === 0);
    });
}

async function downloadPDF() {
    if (!currentFile) {
        alert('No image available for PDF generation.');
        return;
    }

    showLoading('Generating PDF report...');

    const formData = new FormData();
    formData.append('image', currentFile);
    formData.append('is_static', document.getElementById('is-static').checked);
    formData.append('is_repetitive', document.getElementById('is-repetitive').checked);
    formData.append('load_kg', document.getElementById('load-weight').value);
    formData.append('coupling', document.getElementById('coupling').value);

    try {
        const response = await fetch('/api/report/generate', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'PDF generation failed');
        }

        // Get filename from header or use default
        const contentDisposition = response.headers.get('Content-Disposition');
        let filename = 'ergonomic_assessment.pdf';
        if (contentDisposition) {
            const match = contentDisposition.match(/filename="?(.+)"?/);
            if (match) {
                filename = match[1];
            }
        }

        // Download the PDF
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        a.remove();

    } catch (error) {
        console.error('PDF generation error:', error);
        alert('PDF generation failed: ' + error.message);
    } finally {
        hideLoading();
    }
}

function showLoading(message) {
    elements.loadingStatus.textContent = message;
    elements.loadingOverlay.style.display = 'flex';
}

function updateLoadingStatus(message) {
    elements.loadingStatus.textContent = message;
}

function hideLoading() {
    elements.loadingOverlay.style.display = 'none';
}

// =========================================
// SETTINGS & THEME MANAGEMENT
// =========================================

function setupSettings() {
    const settingsBtn = document.getElementById('settings-btn');
    const settingsModal = document.getElementById('settings-modal');
    const settingsOverlay = document.getElementById('settings-overlay');
    const settingsClose = document.getElementById('settings-close');
    const themeDarkBtn = document.getElementById('theme-dark');
    const themeLightBtn = document.getElementById('theme-light');

    // Open settings
    settingsBtn.addEventListener('click', () => {
        settingsModal.style.display = 'flex';
    });

    // Close settings
    settingsClose.addEventListener('click', closeSettings);
    settingsOverlay.addEventListener('click', closeSettings);

    // Close on Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && settingsModal.style.display === 'flex') {
            closeSettings();
        }
    });

    // Theme toggle buttons
    themeDarkBtn.addEventListener('click', () => setTheme('dark'));
    themeLightBtn.addEventListener('click', () => setTheme('light'));

    function closeSettings() {
        settingsModal.style.display = 'none';
    }
}

function loadTheme() {
    // Load saved theme or default to dark
    const savedTheme = localStorage.getItem('ergo-theme') || 'dark';
    setTheme(savedTheme);
}

function setTheme(theme) {
    // Update data attribute on document
    document.documentElement.setAttribute('data-theme', theme);

    // Save to localStorage
    localStorage.setItem('ergo-theme', theme);

    // Update button states
    const themeDarkBtn = document.getElementById('theme-dark');
    const themeLightBtn = document.getElementById('theme-light');

    if (theme === 'dark') {
        themeDarkBtn.classList.add('active');
        themeLightBtn.classList.remove('active');
    } else {
        themeDarkBtn.classList.remove('active');
        themeLightBtn.classList.add('active');
    }
}

