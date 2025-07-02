// Global variables
let currentKey = null;
let currentMelody = null;
let score = 0;
let totalAttempts = 0;
let keyStartTime = null;
let progressChart = null;

// Initialize VexFlow
const { Renderer, Stave, StaveNote, Voice, Formatter, Accidental } = VexFlow;

// Dark Mode Functions
function initDarkMode() {
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    if (!darkModeToggle) return;
    
    // Check for saved theme preference or default to light mode
    const currentTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', currentTheme);
    updateDarkModeButton(currentTheme);
    
    // Add click event listener
    darkModeToggle.addEventListener('click', toggleDarkMode);
}

function toggleDarkMode() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateDarkModeButton(newTheme);
}

function updateDarkModeButton(theme) {
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    if (darkModeToggle) {
        darkModeToggle.textContent = theme === 'dark' ? '☀️' : '🌙';
    }
}

// Stats Modal Functions
function openStatsModal() {
    document.getElementById('stats-modal').classList.remove('hidden');
    loadStatsModal();
    loadProgressChart();
}

function closeStatsModal() {
    document.getElementById('stats-modal').classList.add('hidden');
    if (progressChart) {
        progressChart.destroy();
        progressChart = null;
    }
}

async function loadStatsModal() {
    try {
        const response = await fetch('/api/stats');
        const stats = await response.json();
        
        // Update modal stats
        document.getElementById('modal-accuracy').textContent = (stats.key_practice_accuracy || 0) + '%';
        document.getElementById('modal-treble').textContent = (stats.treble_accuracy || 0) + '%';
        document.getElementById('modal-bass').textContent = (stats.bass_accuracy || 0) + '%';
        document.getElementById('modal-response-time').textContent = stats.avg_response_time || 0;
        
        // Update session progress
        updateSessionProgress(stats.current_session_progress || 0);
    } catch (error) {
        console.error('Error loading stats modal:', error);
    }
}

async function loadProgressChart() {
    try {
        const response = await fetch('/api/graph-data');
        const data = await response.json();
        
        const ctx = document.getElementById('progress-chart').getContext('2d');
        
        if (progressChart) {
            progressChart.destroy();
        }
        
        progressChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.map((d, i) => `Session ${i + 1}`),
                datasets: [{
                    label: 'Accuracy (%)',
                    data: data.map(d => d.accuracy),
                    borderColor: 'rgb(52, 152, 219)',
                    backgroundColor: 'rgba(52, 152, 219, 0.1)',
                    yAxisID: 'y'
                }, {
                    label: 'Response Time (ms)',
                    data: data.map(d => d.response_time),
                    borderColor: 'rgb(46, 204, 113)',
                    backgroundColor: 'rgba(46, 204, 113, 0.1)',
                    yAxisID: 'y1'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false,
                },
                scales: {
                    x: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Practice Sessions'
                        }
                    },
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        title: {
                            display: true,
                            text: 'Accuracy (%)'
                        },
                        min: 0,
                        max: 100
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: {
                            display: true,
                            text: 'Response Time (ms)'
                        },
                        grid: {
                            drawOnChartArea: false,
                        },
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error loading progress chart:', error);
    }
}

async function exportChart() {
    if (!progressChart) return;
    
    try {
        // Create a temporary canvas for high-res export
        const canvas = document.createElement('canvas');
        canvas.width = 1200;
        canvas.height = 800;
        const ctx = canvas.getContext('2d');
        
        // Draw white background
        ctx.fillStyle = 'white';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        // Draw the chart
        ctx.drawImage(progressChart.canvas, 0, 0, canvas.width, canvas.height);
        
        // Convert to blob and download
        canvas.toBlob(blob => {
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `piano_practice_progress_${new Date().toISOString().split('T')[0]}.png`;
            a.click();
            URL.revokeObjectURL(url);
        });
    } catch (error) {
        console.error('Error exporting chart:', error);
    }
}

function updateSessionProgress(current) {
    const percentage = (current / 10) * 100;
    
    // Update main progress bar
    const progressFill = document.getElementById('session-progress-fill');
    const progressText = document.getElementById('session-progress-text');
    if (progressFill) progressFill.style.width = percentage + '%';
    if (progressText) progressText.textContent = `${current}/10`;
    
    // Update small progress bar
    const progressSmall = document.getElementById('session-progress-small');
    const sessionCounter = document.getElementById('session-counter');
    if (progressSmall) progressSmall.style.width = percentage + '%';
    if (sessionCounter) sessionCounter.textContent = `${current}/10`;
}

// Session Management
function showSessionComplete(accuracy, avgTime) {
    document.getElementById('final-accuracy').textContent = accuracy + '%';
    document.getElementById('final-avg-time').textContent = Math.round(avgTime);
    document.getElementById('session-complete-modal').classList.remove('hidden');
}

function startNewSession() {
    document.getElementById('session-complete-modal').classList.add('hidden');
    // Reset counters
    score = 0;
    totalAttempts = 0;
    updateScoreDisplay();
    updateSessionProgress(0);
    generateNewKey();
}

function goHome() {
    window.location.href = '/';
}

// Statistics functions
async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        const stats = await response.json();
        
        // Update stats display
        document.getElementById('total-sessions').textContent = stats.total_sessions || 0;
        document.getElementById('accuracy').textContent = (stats.key_practice_accuracy || 0) + '%';
        document.getElementById('exercises-generated').textContent = stats.sight_reading_generated || 0;
        
        // Update clef-specific accuracy if elements exist
        const trebleAccuracy = document.getElementById('treble-accuracy');
        const bassAccuracy = document.getElementById('bass-accuracy');
        if (trebleAccuracy) trebleAccuracy.textContent = (stats.treble_accuracy || 0) + '%';
        if (bassAccuracy) bassAccuracy.textContent = (stats.bass_accuracy || 0) + '%';
        
        // Update session progress
        updateSessionProgress(stats.current_session_progress || 0);
        
        // Update recent sessions
        const recentContainer = document.getElementById('recent-sessions');
        if (recentContainer && stats.recent_sessions && stats.recent_sessions.length > 0) {
            recentContainer.innerHTML = stats.recent_sessions
                .reverse()
                .slice(0, 5)
                .map(session => {
                    const date = new Date(session.timestamp).toLocaleString();
                    const typeMap = {
                        'key_practice': '🎹 Key Practice',
                        'sight_reading_generated': '📖 Sight Reading',
                        'pdf_export': '📄 PDF Export'
                    };
                    
                    let details = '';
                    if (session.type === 'key_practice') {
                        const result = session.score === '1' ? '✅' : '❌';
                        const time = session.response_time ? ` (${session.response_time}ms)` : '';
                        details = `${result} ${session.correct_answer || 'Unknown'} (${session.clef || 'Unknown'})${time}`;
                    } else if (session.difficulty) {
                        details = `${session.difficulty} level`;
                    }
                    
                    return `
                        <div class="session-item">
                            <span>${typeMap[session.type] || session.type}</span>
                            <span>${details}</span>
                            <span>${date}</span>
                        </div>
                    `;
                }).join('');
        } else if (recentContainer) {
            recentContainer.innerHTML = '<p>No recent activity</p>';
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Key Practice Functions
function initKeyPractice() {
    // Add event listeners for key buttons
    document.querySelectorAll('.key-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            checkKeyAnswer(this.dataset.key);
        });
    });
    
    // Add keyboard event listeners
    document.addEventListener('keydown', function(e) {
        const key = e.key.toUpperCase();
        if (['C', 'D', 'E', 'F', 'G', 'A', 'B'].includes(key)) {
            checkKeyAnswer(key);
        }
    });
    
    // New key button
    document.getElementById('new-key-btn').addEventListener('click', generateNewKey);
}

async function generateNewKey() {
    try {
        const response = await fetch('/api/key/new');
        currentKey = await response.json();
        
        // Clear previous feedback
        hideFeedback();
        resetKeyButtons();
        
        // Draw the key on staff
        drawKeyOnStaff(currentKey);
        
    } catch (error) {
        console.error('Error generating new key:', error);
    }
}

function drawKeyOnStaff(keyData) {
    const container = document.getElementById('staff-display');
    
    // Add fade out transition
    container.style.opacity = '0.3';
    
    // Small delay to smooth the transition
    setTimeout(() => {
        container.innerHTML = ''; // Clear previous content
        
        // Responsive sizing
        const isMobile = window.innerWidth <= 768;
        const width = isMobile ? 350 : 600;
        const height = isMobile ? 200 : 300;
        const staveX = isMobile ? 50 : 75;
        const staveY = isMobile ? 40 : 60;
        const staveWidth = isMobile ? 250 : 450;
        const formatWidth = isMobile ? 200 : 350;
        
        // Create SVG renderer with responsive dimensions
        const renderer = new Renderer(container, Renderer.Backends.SVG);
        renderer.resize(width, height);
        const context = renderer.getContext();
        
        // Force white background on the SVG
        const svg = container.querySelector('svg');
        if (svg) {
            svg.style.backgroundColor = 'white';
            svg.style.borderRadius = '8px';
            svg.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)';
        }
        
        // Create stave with responsive size
        const stave = new Stave(staveX, staveY, staveWidth);
        
        // Add clef
        stave.addClef(keyData.clef);
        
        // Draw stave
        stave.setContext(context).draw();
        
        // Create note with proper octave
        const noteString = keyData.note + (keyData.accidental || '') + '/' + keyData.octave;
        const note = new StaveNote({
            clef: keyData.clef,
            keys: [noteString],
            duration: 'w'
        });
        
        // Add accidental if needed
        if (keyData.accidental) {
            note.addModifier(new Accidental(keyData.accidental), 0);
        }
        
        // Create voice and add note
        const voice = new Voice({ num_beats: 4, beat_value: 4 });
        voice.addTickables([note]);
        
        // Format and draw with responsive formatting area
        const formatter = new Formatter().joinVoices([voice]).format([voice], formatWidth);
        voice.draw(context, stave);
        
        // Fade back in
        container.style.opacity = '1';
    }, 100);
}

async function checkKeyAnswer(userAnswer) {
    if (!currentKey) return;
    
    try {
        const response = await fetch('/api/key/check', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ answer: userAnswer })
        });
        
        const result = await response.json();
        
        // Update score
        totalAttempts++;
        if (result.correct) {
            score++;
        }
        updateScoreDisplay();
        
        // Show feedback
        showFeedback(result);
        
        // Highlight button
        highlightKeyButton(userAnswer, result.correct);
        
        // Auto-generate new key after 2 seconds
        setTimeout(() => {
            generateNewKey();
        }, 2000);
        
    } catch (error) {
        console.error('Error checking answer:', error);
    }
}

function showFeedback(result) {
    const feedback = document.getElementById('feedback');
    const message = document.getElementById('feedback-message');
    const details = document.getElementById('feedback-details');
    
    feedback.classList.remove('hidden', 'correct', 'incorrect');
    
    if (result.correct) {
        feedback.classList.add('correct');
        message.textContent = '✅ Correct!';
        details.textContent = `You got ${result.correct_answer} right!`;
    } else {
        feedback.classList.add('incorrect');
        message.textContent = '❌ Incorrect';
        details.textContent = `The correct answer was ${result.correct_answer}, you answered ${result.user_answer}`;
    }
}

function hideFeedback() {
    document.getElementById('feedback').classList.add('hidden');
}

function highlightKeyButton(key, correct) {
    resetKeyButtons();
    const button = document.querySelector(`[data-key="${key}"]`);
    if (button) {
        button.classList.add(correct ? 'correct' : 'incorrect');
    }
}

function resetKeyButtons() {
    document.querySelectorAll('.key-btn').forEach(btn => {
        btn.classList.remove('correct', 'incorrect');
    });
}

function updateScoreDisplay() {
    document.getElementById('current-score').textContent = score;
    document.getElementById('total-attempts').textContent = totalAttempts;
    const accuracy = totalAttempts > 0 ? Math.round((score / totalAttempts) * 100) : 0;
    document.getElementById('accuracy-percent').textContent = accuracy;
}

// Sight Reading Functions
function initSightReading() {
    document.getElementById('generate-btn').addEventListener('click', generateMelody);
    document.getElementById('export-btn').addEventListener('click', exportPDF);
}

async function generateMelody() {
    const difficulty = document.getElementById('difficulty').value;
    const clef = document.getElementById('clef').value;
    
    try {
        const response = await fetch('/api/melody/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ difficulty, clef })
        });
        
        currentMelody = await response.json();
        
        // Display melody info
        document.getElementById('key-signature').textContent = currentMelody.key_signature;
        document.getElementById('time-signature').textContent = currentMelody.time_signature;
        document.getElementById('clef-type').textContent = currentMelody.clef;
        document.getElementById('melody-info').classList.remove('hidden');
        
        // Draw melody on staff
        drawMelodyOnStaff(currentMelody);
        
        // Enable export button
        document.getElementById('export-btn').disabled = false;
        
    } catch (error) {
        console.error('Error generating melody:', error);
    }
}

function drawMelodyOnStaff(melodyData) {
    const container = document.getElementById('melody-staff');
    
    // Add fade out transition
    container.style.opacity = '0.3';
    
    // Small delay to smooth the transition
    setTimeout(() => {
        container.innerHTML = ''; // Clear previous content
        
        // Responsive sizing
        const isMobile = window.innerWidth <= 768;
        const width = isMobile ? 350 : 1200;
        const height = isMobile ? 250 : 400;
        const staveX = isMobile ? 25 : 75;
        const staveY = isMobile ? 40 : 60;
        const measureWidth = isMobile ? 80 : 250;
        const measuresToShow = isMobile ? 4 : 4;
        
        // Create SVG renderer with responsive dimensions
        const renderer = new Renderer(container, Renderer.Backends.SVG);
        renderer.resize(width, height);
        const context = renderer.getContext();
        
        // Force white background on the SVG
        const svg = container.querySelector('svg');
        if (svg) {
            svg.style.backgroundColor = 'white';
            svg.style.borderRadius = '8px';
            svg.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)';
        }
        
        // Group notes by measure
        const measures = {};
        melodyData.melody.forEach(noteData => {
            if (!measures[noteData.measure]) {
                measures[noteData.measure] = [];
            }
            measures[noteData.measure].push(noteData);
        });
        
        // Draw measures with responsive dimensions
        let xPos = staveX;
        
        Object.keys(measures).slice(0, measuresToShow).forEach((measureNum, index) => {
            // Create stave with responsive width
            const stave = new Stave(xPos, staveY, measureWidth);
            
            // Add clef and time signature to first measure
            if (index === 0) {
                stave.addClef(melodyData.clef);
                stave.addTimeSignature(melodyData.time_signature);
            }
            
            stave.setContext(context).draw();
            
            // Create notes for this measure
            const notes = measures[measureNum].map(noteData => {
                const noteString = noteData.note + '/4';
                const duration = getDurationFromRhythm(noteData.rhythm);
                
                return new StaveNote({
                    clef: melodyData.clef,
                    keys: [noteString],
                    duration: duration
                });
            });
            
            // Create voice and add notes
            if (notes.length > 0) {
                const voice = new Voice({ num_beats: 4, beat_value: 4 });
                voice.addTickables(notes);
                
                // Format and draw with responsive formatting area
                const formatWidth = measureWidth - (isMobile ? 15 : 30);
                const formatter = new Formatter().joinVoices([voice]).format([voice], formatWidth);
                voice.draw(context, stave);
            }
            
            xPos += measureWidth;
        });
        
        // Fade back in
        container.style.opacity = '1';
    }, 150);
}

function getDurationFromRhythm(rhythm) {
    const rhythmMap = {
        'whole': 'w',
        'half': 'h',
        'quarter': 'q',
        'eighth': '8',
        'sixteenth': '16',
        'dotted_quarter': 'qd',
        'triplet': '8',
        'syncopated': '8'
    };
    return rhythmMap[rhythm] || 'q';
}

async function exportPDF() {
    if (!currentMelody) return;
    
    try {
        const response = await fetch('/api/melody/export', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(currentMelody)
        });
        
        if (response.ok) {
            // Download the PDF
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = `practice_sheet_${new Date().getTime()}.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } else {
            console.error('Error exporting PDF');
        }
        
    } catch (error) {
        console.error('Error exporting PDF:', error);
    }
}

// Utility functions
function formatTimestamp(timestamp) {
    return new Date(timestamp).toLocaleString();
}