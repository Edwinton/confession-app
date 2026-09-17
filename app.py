from flask import Flask, render_template
import json
import os

app = Flask(__name__)

@app.route('/')
def index():
    data_path = os.path.join(os.path.dirname(__file__), 'data', 'sins.json')
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return render_template('index.html', data=data)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)