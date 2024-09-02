import os
from flask import Flask, request, render_template, redirect, url_for
import requests
import json

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files.get('media')
        if file:
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            if 'check_ai' in request.form:
                params = {
                    'models': 'genai',
                    'api_user': '1745504981',
                    'api_secret': 'yBmqEJu5n87rbdDBLFR2FHHJsxJydnPD'
                }
                files = {'media': open(filepath, 'rb')}
                r = requests.post('https://api.sightengine.com/1.0/check.json', files=files, data=params)
                output = json.loads(r.text)
                print(output)
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

            elif 'check_deepfake' in request.form:
                # Check for deepfake
                params = {
                    'models': 'deepfake',
                    'api_user': '1745504981',
                    'api_secret': 'yBmqEJu5n87rbdDBLFR2FHHJsxJydnPD'
                }
                files = {'media': open(filepath, 'rb')}
                r = requests.post('https://api.sightengine.com/1.0/check.json', files=files, data=params)
                output = json.loads(r.text)
                print(output)
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

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
