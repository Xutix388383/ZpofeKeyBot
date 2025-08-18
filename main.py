
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
    
    # Admin credentials from environment variables with fallbacks
    admin_username = os.getenv('ADMIN_USERNAME', 'Zpofe0902')
    admin_password = os.getenv('ADMIN_PASSWORD', '0902')
    
    if username == admin_username and password == admin_password:
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

def try_port(port):
    """Try to start the Flask app on a specific port"""
    try:
        print(f"🚀 Attempting to start Flask server on port {port}...")
        app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
        return True
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"⚠️ Port {port} is already in use")
            return False
        else:
            print(f"❌ Error starting server on port {port}: {e}")
            return False
    except Exception as e:
        print(f"❌ Unexpected error on port {port}: {e}")
        return False

def start_server_with_fallback():
    """Start server with fallback ports and error handling"""
    preferred_ports = [5000, 8080, 3000, 8000, 9000, 7000, 6000, 4000]
    
    print("🌟 Starting Flask Marketplace Server...")
    print("📊 Server will handle script marketplace web interface")
    
    for port in preferred_ports:
        try:
            print(f"🔍 Checking port {port} availability...")
            import socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('0.0.0.0', port))
                print(f"✅ Port {port} is available")
            
            print(f"🚀 Starting Flask server on 0.0.0.0:{port}")
            print(f"🌐 Web interface will be accessible at: http://localhost:{port}")
            print("📝 Available endpoints:")
            print("   • / - Homepage with script marketplace")
            print("   • /admin - Admin panel for managing scripts")
            print("   • /purchase/<script_id> - Purchase endpoint")
            
            app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
            break
            
        except OSError as e:
            if "Address already in use" in str(e):
                print(f"⚠️ Port {port} is already in use, trying next port...")
                continue
            else:
                print(f"❌ Network error on port {port}: {e}")
                continue
        except KeyboardInterrupt:
            print("\n🛑 Server stopped by user")
            break
        except Exception as e:
            print(f"❌ Unexpected error on port {port}: {e}")
            continue
    else:
        print("❌ Could not start server on any available port!")
        print("💡 Tried ports:", preferred_ports)
        print("🔧 Troubleshooting tips:")
        print("   • Check if other services are using these ports")
        print("   • Restart your repl")
        print("   • Check for permission issues")
        exit(1)

if __name__ == '__main__':
    try:
        print("🔧 Checking environment variables...")
        
        # Check admin credentials
        admin_username = os.getenv('ADMIN_USERNAME')
        admin_password = os.getenv('ADMIN_PASSWORD')
        
        if admin_username and admin_password:
            print(f"✅ Admin credentials found in environment")
        else:
            print(f"⚠️ Using default admin credentials")
            print("💡 Set ADMIN_USERNAME and ADMIN_PASSWORD environment variables to customize")
        
        print("🚀 Starting Flask marketplace server...")
        init_data_files()
        start_server_with_fallback()
    except KeyboardInterrupt:
        print("\n🛑 Server shutdown requested")
    except Exception as e:
        print(f"❌ Fatal error starting marketplace server: {e}")
        print("🔧 Please check your configuration and try again")
        exit(1)
