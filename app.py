import os
from flask import Flask, request, render_template, redirect, url_for
import requests
import json

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Load API credentials from environment variables
API_USER = os.getenv('SIGHTENGINE_API_USER', '1745504981')
API_SECRET = os.getenv('SIGHTENGINE_API_SECRET', 'yBmqEJu5n87rbdDBLFR2FHHJsxJydnPD')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files.get('media')
        if file:
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            if 'check_ai' in request.form:
                try:
                    params = {
                        'models': 'genai',
                        'api_user': API_USER,
                        'api_secret': API_SECRET
                    }
                    with open(filepath, 'rb') as f:
                        files = {'media': f}
                        r = requests.post('https://api.sightengine.com/1.0/check.json', files=files, data=params)
                        r.raise_for_status()
                        output = r.json()
                    
                    ai_generated_score = output['type']['ai_generated']
                    ai_generated_percentage = ai_generated_score * 100

                    if ai_generated_percentage >= 60:
                        classification = "It's an AI Generated Image 😅🤖"
                    elif ai_generated_percentage >= 40:
                        classification = "Likely Fake 🤔💭"
                    elif ai_generated_percentage >= 20:
                        classification = "Likely Real 🤞🌟"
                    else:
                        classification = "Real ✅👍"

                    return render_template('result.html', percentage=ai_generated_percentage, classification=classification, image_url=filename)

                except requests.RequestException as e:
                    return f"Error processing AI image: {e}", 500

            elif 'check_deepfake' in request.form:
                try:
                    params = {
                        'models': 'deepfake',
                        'api_user': API_USER,
                        'api_secret': API_SECRET
                    }
                    with open(filepath, 'rb') as f:
                        files = {'media': f}
                        r = requests.post('https://api.sightengine.com/1.0/check.json', files=files, data=params)
                        r.raise_for_status()
                        output = r.json()
                    
                    deepfake_score = output['type']['deepfake']
                    deepfake_percentage = deepfake_score * 100

                    if deepfake_percentage >= 50:
                        classification = "Deepfake 🚨👀"
                    elif deepfake_percentage >= 40:
                        classification = "Likely Fake 🤔💭"
                    elif deepfake_percentage >= 20:
                        classification = "Likely Real 🤞🌟"
                    else:
                        classification = "Not Deepfake 🎉🙌"

                    return render_template('result.html', percentage=deepfake_percentage, classification=classification, image_url=filename)

                except requests.RequestException as e:
                    return f"Error processing Deepfake image: {e}", 500

    return render_template('index.html')

if __name__ == '__main__':
    # Use the PORT environment variable if it's set, otherwise default to 5000
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
