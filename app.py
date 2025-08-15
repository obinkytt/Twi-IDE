from flask import Flask, render_template, request, jsonify
import subprocess
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run', methods=['POST'])
def run_code():
    code = request.json['code']
    with open("temp_code.py", "w", encoding="utf-8") as f:
        f.write(code)
    
    try:
        output = subprocess.check_output(['python', 'temp_code.py'], stderr=subprocess.STDOUT, text=True)
    except subprocess.CalledProcessError as e:
        output = e.output

    return jsonify({'output': output})

if __name__ == '__main__':
    app.run(debug=True)
