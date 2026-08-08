from flask import Flask, request, jsonify
import os

app = Flask(__name__)
API_KEY = os.environ.get('API_KEY', '#2PIAUengaly')

@app.route('/api/v1/status', methods=['GET'])
def status():
    auth = request.headers.get('Authorization', '')
    if auth != f'Bearer {API_KEY}':
        return jsonify({'error': 'API Key required'}), 401
    return jsonify({'status': 'ok', 'service': 'platforme-osint', 'version': '1.0.0'})

@app.route('/api/v1/investigation', methods=['POST'])
def investigation():
    auth = request.headers.get('Authorization', '')
    if auth != f'Bearer {API_KEY}':
        return jsonify({'error': 'API Key required'}), 401
    data = request.get_json() or {}
    return jsonify({'status': 'running', 'task': data.get('task', 'default')})

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)