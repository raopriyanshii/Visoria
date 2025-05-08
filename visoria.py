from flask import Flask, request, render_template_string, jsonify
import cohere
import os

# Replace with your API key - ideally from environment variable
api_key = os.environ.get('COHERE_API_KEY', 't1yORoLTWYb5NLVAgKTJlSra5iK27kMYw0irtjeD')

# Initialize the Cohere client
try:
    co = cohere.Client(api_key)
except Exception as e:
    print(f"Error initializing Cohere client: {e}")
    co = None

# Create a Flask web application
app = Flask(__name__)

def analyze_dream(dream_description):
    """Analyze a dream description using Cohere's generation capabilities"""
    if not co:
        return {"error": "Cohere client not initialized properly"}
    
    try:
        # Using generation instead of classification for more flexibility
        prompt = f"""
        Analyze the following dream and provide insights about its emotional tone, 
        themes, and potential meanings based on general dream psychology principles.
        
        DREAM: {dream_description}
        
        Please provide:
        1. The primary emotional tone (positive, negative, neutral)
        2. Main theme or symbol
        3. A psychological explanation
        4. General advice based on this dream
        """
        
        response = co.generate(
            prompt=prompt,
            max_tokens=300,
            temperature=0.7,
            k=0,
            model='command'  # or another appropriate model
        )
        
        # Get the generated text
        analysis_text = response.generations[0].text
        
        # Parse the response - this is a simplified approach
        lines = analysis_text.strip().split('\n')
        
        emotion = "neutral"
        theme = "unknown"
        explanation = ""
        advice = ""
        
        for line in lines:
            line = line.strip()
            if "emotional tone" in line.lower() and ":" in line:
                emotion_part = line.split(":", 1)[1].strip().lower()
                if "positive" in emotion_part:
                    emotion = "positive"
                elif "negative" in emotion_part:
                    emotion = "negative"
                else:
                    emotion = "neutral"
            
            if "theme" in line.lower() and ":" in line:
                theme = line.split(":", 1)[1].strip()
            
            if "explanation" in line.lower() and ":" in line:
                explanation = line.split(":", 1)[1].strip()
            
            if "advice" in line.lower() and ":" in line:
                advice = line.split(":", 1)[1].strip()
        
        # If parsing failed, use the whole text
        if not explanation and not advice:
            explanation = analysis_text
        
        # Provide the analysis result
        analysis = {
            "emotion": emotion,
            "theme": theme,
            "confidence": 85,  # Default confidence since we're not using classification
            "explanation": explanation,
            "general_advice": advice or get_advice(emotion)
        }
        
        return analysis
    except Exception as e:
        print(f"Error analyzing dream: {e}")
        return {"error": str(e)}

def get_advice(emotion_type):
    """Provide advice based on the emotional tone of the dream"""
    if emotion_type == "positive":
        return "This positive dream suggests alignment with your goals and desires. Consider how you can bring more of these feelings into your waking life."
    elif emotion_type == "negative":
        return "This challenging dream may be highlighting issues that need attention. Consider journaling about these emotions and what they might represent in your life."
    else:
        return "This dream contains meaningful symbols from your subconscious. Reflect on how they relate to your current life circumstances."

# HTML template for the web interface
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Dream Analyzer</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
            background-color: #f5f5f5;
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }
        .container {
            background-color: white;
            padding: 25px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        textarea {
            width: 100%;
            height: 150px;
            padding: 12px;
            border: 1px solid #ccc;
            border-radius: 4px;
            resize: vertical;
            font-family: inherit;
            font-size: 16px;
            box-sizing: border-box;
            margin-bottom: 15px;
        }
        button {
            background-color: #4CAF50;
            color: white;
            padding: 12px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            display: block;
            margin: 0 auto;
            transition: background-color 0.3s;
        }
        button:hover {
            background-color: #45a049;
        }
        #result {
            margin-top: 25px;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 4px;
            background-color: #f9f9f9;
            display: none;
            animation: fadeIn 0.5s;
        }
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        .result-item {
            margin-bottom: 15px;
        }
        .result-label {
            font-weight: bold;
            margin-right: 8px;
        }
        .emotion-positive {
            color: #4CAF50;
            font-weight: bold;
        }
        .emotion-negative {
            color: #f44336;
            font-weight: bold;
        }
        .emotion-neutral {
            color: #2196F3;
            font-weight: bold;
        }
        .confidence {
            font-style: italic;
            color: #666;
        }
        #loading {
            text-align: center;
            display: none;
            margin: 20px 0;
        }
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #3498db;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .error {
            color: #f44336;
            font-weight: bold;
            padding: 10px;
            background: #ffebee;
            border-radius: 4px;
            margin-top: 20px;
            display: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Dream Analyzer</h1>
        <p>Describe your dream in detail below, and our AI will analyze its potential meanings and emotions.</p>
        
        <textarea id="dreamDescription" placeholder="I was flying over mountains and felt incredibly free..."></textarea>
        <button onclick="analyzeDream()">Analyze Dream</button>
        
        <div id="loading">
            <div class="spinner"></div>
            <p>Analyzing your dream...</p>
        </div>
        
        <div id="error" class="error"></div>
        
        <div id="result">
            <h2>Dream Analysis Results</h2>
            <div class="result-item">
                <span class="result-label">Emotional Tone:</span>
                <span id="emotion"></span>
            </div>
            <div class="result-item">
                <span class="result-label">Theme:</span>
                <span id="theme"></span>
            </div>
            <div class="result-item">
                <span class="result-label">Interpretation:</span>
                <span id="explanation"></span>
            </div>
            <div class="result-item">
                <span class="result-label">Advice:</span>
                <span id="advice"></span>
            </div>
        </div>
    </div>

    <script>
        function analyzeDream() {
            const dreamText = document.getElementById('dreamDescription').value;
            if (!dreamText) {
                showError('Please enter a dream description');
                return;
            }
            
            // Show loading spinner
            document.getElementById('loading').style.display = 'block';
            document.getElementById('result').style.display = 'none';
            document.getElementById('error').style.display = 'none';
            
            fetch('/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ dream: dreamText }),
            })
            .then(response => response.json())
            .then(data => {
                // Hide loading spinner
                document.getElementById('loading').style.display = 'none';
                
                if (data.error) {
                    showError(data.error);
                    return;
                }
                
                document.getElementById('emotion').className = 'emotion-' + data.emotion;
                document.getElementById('emotion').textContent = data.emotion;
                document.getElementById('theme').textContent = data.theme;
                document.getElementById('explanation').textContent = data.explanation;
                document.getElementById('advice').textContent = data.general_advice;
                document.getElementById('result').style.display = 'block';
            })
            .catch(error => {
                console.error('Error:', error);
                document.getElementById('loading').style.display = 'none';
                showError('Error analyzing dream. Please try again.');
            });
        }
        
        function showError(message) {
            const errorElement = document.getElementById('error');
            errorElement.textContent = message;
            errorElement.style.display = 'block';
        }
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    dream_text = data.get('dream', '')
    analysis = analyze_dream(dream_text)
    return jsonify(analysis)

if __name__ == '__main__':
    # Get port from environment variable or default to 5000
    port = int(os.environ.get('PORT', 5000))
    
    # Print startup message
    host = '0.0.0.0'  # Listen on all network interfaces
    print(f"Dream Analyzer Web App starting on http://{host}:{port}/")
    print(f"Access from your browser using 'http://localhost:{port}/'")
    print("Press Ctrl+C to quit")
    
    # Start the Flask app
    app.run(host=host, port=port, debug=True)
