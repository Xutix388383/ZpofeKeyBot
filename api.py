
from flask import Flask, request, jsonify
import os
import json
import time
import secrets
import string

app = Flask(__name__)

# Configuration
RAILWAY_PROJECT_ID = os.getenv('RAILWAY_PROJECT_ID', 'your-project-id')
RAILWAY_SERVICE_ID = os.getenv('RAILWAY_SERVICE_ID', 'your-service-id')

# Load data files
def load_json_file(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    return {}

def save_json_file(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

# API Routes
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "ZpofeHub API",
        "timestamp": time.time(),
        "railway_project": RAILWAY_PROJECT_ID,
        "railway_service": RAILWAY_SERVICE_ID
    })

@app.route('/api/verify-key', methods=['POST'])
def verify_key():
    data = request.get_json()
    if not data or 'key' not in data:
        return jsonify({"error": "Key required"}), 400
    
    key = data['key']
    hwid = data.get('hwid')
    
    keys = load_json_file('keys.json')
    
    if key not in keys:
        return jsonify({"error": "Invalid key"}), 401
    
    key_data = keys[key]
    
    # Check if key is expired
    if key_data.get('expires_at') and time.time() > key_data['expires_at']:
        return jsonify({"error": "Key expired"}), 401
    
    # Check HWID binding
    if key_data.get('hwid') and key_data['hwid'] != hwid:
        return jsonify({"error": "HWID mismatch"}), 401
    
    # Bind HWID if not already bound
    if not key_data.get('hwid') and hwid:
        keys[key]['hwid'] = hwid
        keys[key]['used'] = True
        save_json_file('keys.json', keys)
    
    return jsonify({
        "success": True,
        "message": "Key verified successfully",
        "key_type": key_data.get('type', 'perm'),
        "bound": bool(key_data.get('hwid'))
    })

@app.route('/api/script', methods=['GET'])
def get_script():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Authorization required"}), 401
    
    key = auth_header.replace('Bearer ', '')
    keys = load_json_file('keys.json')
    
    if key not in keys:
        return jsonify({"error": "Invalid key"}), 401
    
    # Return your script loadstring here
    return jsonify({
        "success": True,
        "script": "loadstring(game:HttpGet(\"https://pastebin.com/raw/DmRu7yE0\"))()",
        "message": "Script loaded successfully"
    })

@app.route('/webhook', methods=['POST'])
def webhook():
    """Railway webhook endpoint"""
    data = request.get_json()
    
    # Log webhook data
    print(f"Webhook received: {data}")
    
    # Process webhook data as needed
    return jsonify({"status": "received"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
