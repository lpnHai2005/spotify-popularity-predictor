document.addEventListener('DOMContentLoaded', () => {
    // 1. Fetch Genres
    fetchGenres();

    // 2. Setup Slider Event Listeners
    setupSliders();

    // 3. Handle Form Submission
    const form = document.getElementById('prediction-form');
    form.addEventListener('submit', handlePredict);
});

async function fetchGenres() {
    const genreSelect = document.getElementById('track_genre');
    try {
        const response = await fetch('/metadata');
        const data = await response.json();
        
        if (data.genres && data.genres.length > 0) {
            genreSelect.innerHTML = '<option value="" disabled selected>Select a Genre</option>';
            data.genres.forEach(genre => {
                const option = document.createElement('option');
                option.value = genre;
                option.textContent = genre.charAt(0).toUpperCase() + genre.slice(1);
                genreSelect.appendChild(option);
            });
        } else {
            genreSelect.innerHTML = '<option value="" disabled>No genres found</option>';
        }
    } catch (error) {
        console.error('Error fetching metadata:', error);
        genreSelect.innerHTML = '<option value="" disabled>Error loading genres</option>';
    }
}

function setupSliders() {
    const inputs = [
        'duration_min', 'tempo', 'danceability', 'energy', 
        'valence', 'loudness', 'acousticness', 'instrumentalness', 
        'liveness', 'speechiness', 'key', 'time_signature'
    ];

    inputs.forEach(id => {
        const input = document.getElementById(id);
        const display = document.getElementById(`val_${id}`);
        
        if (input && display) {
            input.addEventListener('input', (e) => {
                // Formatting based on type
                if (['danceability', 'energy', 'valence', 'acousticness', 'instrumentalness', 'liveness', 'speechiness'].includes(id)) {
                    display.textContent = parseFloat(e.target.value).toFixed(2);
                } else if (id === 'loudness' || id === 'duration_min' || id === 'tempo') {
                    display.textContent = parseFloat(e.target.value).toFixed(1);
                } else {
                    display.textContent = e.target.value;
                }
            });
        }
    });
}

async function handlePredict(e) {
    e.preventDefault();
    
    // UI Loading state
    const btnText = document.querySelector('.btn-text');
    const loader = document.getElementById('loader');
    const btn = document.getElementById('btn-predict');
    
    btnText.textContent = 'Predicting...';
    loader.style.display = 'block';
    btn.disabled = true;

    const formData = new FormData(e.target);
    const data = {
        track_genre: formData.get('track_genre'),
        duration_min: parseFloat(formData.get('duration_min')),
        explicit: parseInt(formData.get('explicit')),
        tempo: parseFloat(formData.get('tempo')),
        danceability: parseFloat(formData.get('danceability')),
        energy: parseFloat(formData.get('energy')),
        valence: parseFloat(formData.get('valence')),
        loudness: parseFloat(formData.get('loudness')),
        acousticness: parseFloat(formData.get('acousticness')),
        instrumentalness: parseFloat(formData.get('instrumentalness')),
        liveness: parseFloat(formData.get('liveness')),
        speechiness: parseFloat(formData.get('speechiness')),
        key: parseInt(formData.get('key')),
        mode: parseInt(formData.get('mode')),
        time_signature: parseInt(formData.get('time_signature'))
    };

    try {
        const response = await fetch('/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();
        
        if (response.ok) {
            updateScoreUI(result.predicted_popularity);
        } else {
            alert(`Error: ${result.detail}`);
        }
    } catch (error) {
        console.error('Prediction error:', error);
        alert('Failed to connect to the server.');
    } finally {
        // Reset UI Loading state
        btnText.textContent = 'Predict Popularity';
        loader.style.display = 'none';
        btn.disabled = false;
    }
}

function updateScoreUI(score) {
    const scoreValue = document.getElementById('score-value');
    const progressCircle = document.getElementById('progress-circle');
    const verdict = document.getElementById('prediction-verdict');
    
    // Animate numbers
    let currentScore = 0;
    const duration = 1000;
    const steps = 30;
    const stepTime = Math.abs(Math.floor(duration / steps));
    
    const targetScore = Math.min(100, Math.max(0, score)); // Clamp 0-100
    
    const timer = setInterval(() => {
        currentScore += (targetScore / steps);
        if (currentScore >= targetScore) {
            currentScore = targetScore;
            clearInterval(timer);
        }
        scoreValue.textContent = Math.round(currentScore);
    }, stepTime);

    // Animate Circle
    // Circle circumference is 2 * pi * r = 2 * 3.14159 * 45 = ~283
    const circumference = 283;
    const offset = circumference - (targetScore / 100) * circumference;
    progressCircle.style.strokeDashoffset = offset;

    // Update Verdict
    if (score >= 75) {
        verdict.textContent = "🔥 Potential Viral Hit!";
        verdict.style.color = "#E67E22";
        progressCircle.style.stroke = "#E67E22";
    } else if (score >= 50) {
        verdict.textContent = "👍 Solid Popularity";
        verdict.style.color = "#1DB954";
        progressCircle.style.stroke = "#1DB954";
    } else if (score >= 30) {
        verdict.textContent = "🎧 Niche Audience";
        verdict.style.color = "#2E86AB";
        progressCircle.style.stroke = "#2E86AB";
    } else {
        verdict.textContent = "💤 Low Popularity";
        verdict.style.color = "#E74C3C";
        progressCircle.style.stroke = "#E74C3C";
    }
}
