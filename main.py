
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
import json
from datetime import datetime
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Store for scripts (in production, use a proper database)
SCRIPTS_FILE = 'scripts.json'
ORDERS_FILE = 'orders.json'

# Initialize data files
def init_data_files():
    if not os.path.exists(SCRIPTS_FILE):
        with open(SCRIPTS_FILE, 'w') as f:
            json.dump([], f)
    if not os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, 'w') as f:
            json.dump([], f)

def load_scripts():
    with open(SCRIPTS_FILE, 'r') as f:
        return json.load(f)

def save_scripts(scripts):
    with open(SCRIPTS_FILE, 'w') as f:
        json.dump(scripts, f, indent=2)

def load_orders():
    with open(ORDERS_FILE, 'r') as f:
        return json.load(f)

def save_orders(orders):
    with open(ORDERS_FILE, 'w') as f:
        json.dump(orders, f, indent=2)

@app.route('/')
def home():
    scripts = load_scripts()
    return render_template('index.html', scripts=scripts)

@app.route('/admin')
def admin():
    if not session.get('admin_authenticated'):
        return render_template('admin_login.html')
    
    scripts = load_scripts()
    orders = load_orders()
    return render_template('admin.html', scripts=scripts, orders=orders)

@app.route('/admin/login', methods=['POST'])
def admin_login():
    username = request.form.get('username')
    password = request.form.get('password')
    # Admin credentials
    if username == 'Zpofe0902' and password == '0902':
        session['admin_authenticated'] = True
        return redirect(url_for('admin'))
    return render_template('admin_login.html', error='Invalid credentials')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_authenticated', None)
    return redirect(url_for('home'))

@app.route('/admin/add_script', methods=['POST'])
def add_script():
    if not session.get('admin_authenticated'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    scripts = load_scripts()
    script = {
        'id': len(scripts) + 1,
        'name': request.form.get('name'),
        'description': request.form.get('description'),
        'price': float(request.form.get('price')),
        'category': request.form.get('category'),
        'features': request.form.get('features').split('\n'),
        'demo_link': request.form.get('demo_link', ''),
        'created_at': datetime.now().isoformat()
    }
    scripts.append(script)
    save_scripts(scripts)
    return redirect(url_for('admin'))

@app.route('/purchase/<int:script_id>', methods=['POST'])
def purchase_script(script_id):
    scripts = load_scripts()
    script = next((s for s in scripts if s['id'] == script_id), None)
    
    if not script:
        return jsonify({'error': 'Script not found'}), 404
    
    # In a real application, integrate with a payment processor
    order = {
        'id': len(load_orders()) + 1,
        'script_id': script_id,
        'script_name': script['name'],
        'buyer_email': request.form.get('email'),
        'buyer_discord': request.form.get('discord'),
        'price': script['price'],
        'status': 'pending',
        'created_at': datetime.now().isoformat()
    }
    
    orders = load_orders()
    orders.append(order)
    save_orders(orders)
    
    return jsonify({'message': 'Order placed successfully! You will be contacted shortly.', 'order_id': order['id']})

if __name__ == '__main__':
    init_data_files()
    app.run(host='0.0.0.0', port=5000, debug=True)
