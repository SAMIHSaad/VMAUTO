import click
from flask import Flask, request, jsonify, send_from_directory, redirect, make_response
from flask.cli import with_appcontext
from flask_mysqldb import MySQL
from flask_jwt_extended import create_access_token, jwt_required, JWTManager, get_jwt_identity, set_access_cookies, unset_jwt_cookies
from flask_jwt_extended.exceptions import InvalidHeaderError, NoAuthorizationError, CSRFError, RevokedTokenError, FreshTokenRequired, UserLookupError, UserClaimsVerificationError
from jwt import ExpiredSignatureError, InvalidTokenError, DecodeError
import bcrypt
import MySQLdb
import subprocess
import sys
import json
import atexit
import time
import threading
from hypervisor_manager import HypervisorManager
from hypervisor_providers import VMConfig
from ip_manager import get_available_ip

app = Flask(__name__, static_folder='frontend')

def check_mock_server_health():
    """Check if the mock server is running and accessible"""
    import requests
    try:
        response = requests.get('http://127.0.0.1:9441/api/nutanix/v3/clusters/list', timeout=5)
        return response.status_code == 200
    except Exception:
        return False

def start_nutanix_mock_server():
    """Start the Nutanix mock server in a background process."""
    global mock_server_process
    mock_server_process = None
    
    try:
        print("Starting Nutanix mock server...")
        
        # Check if mock server is already running
        if check_mock_server_health():
            print("✅ Nutanix mock server is already running and healthy")
            return
        
        # Use sys.executable to ensure we use the same python interpreter
        # Start the mock server with simple configuration
        mock_server_process = subprocess.Popen(
            [sys.executable, 'nutanix_mock_server.py'], 
            cwd=r'c:\Users\saads\OneDrive\Documents\Coding\Auto-Creation-VM'
        )
        
        print(f"Nutanix mock server started with PID: {mock_server_process.pid}")
        
        # Give the server a moment to start
        time.sleep(3)
        
        # Check if the process is still running and healthy
        if mock_server_process.poll() is None:
            # Check if the server is responding
            if check_mock_server_health():
                print("✅ Nutanix mock server is running and healthy")
            else:
                print("⚠️ Nutanix mock server is running but not responding to health checks")
        else:
            print("❌ Nutanix mock server failed to start")

        @atexit.register
        def terminate_mock_server():
            if mock_server_process and mock_server_process.poll() is None:
                print("Stopping Nutanix mock server...")
                mock_server_process.terminate()
                try:
                    mock_server_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    print("Force killing mock server...")
                    mock_server_process.kill()
                    mock_server_process.wait()
                print("Mock server stopped.")

    except Exception as e:
        print(f"Failed to start Nutanix mock server: {e}")
        import traceback
        traceback.print_exc()

# Start the mock server when the module is loaded
start_nutanix_mock_server()

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'autocreationvm'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# JWT Configuration
app.config['JWT_SECRET_KEY'] = 'super-secret'  # Change this in your application!
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_ACCESS_COOKIE_PATH'] = '/'
app.config['JWT_COOKIE_CSRF_PROTECT'] = False
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 300 # 5 minutes
jwt = JWTManager(app)



mysql = MySQL(app)

# Initialize Hypervisor Manager
hypervisor_manager = HypervisorManager()

@click.command('create-db')
def create_db_command():
    """Create the database."""
    try:
        db = MySQLdb.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD']
        )
        cursor = db.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {app.config['MYSQL_DB']}")
        db.close()
        click.echo('Database created.')
    except Exception as e:
        click.echo(f'Error creating database: {e}')

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    cur = mysql.connection.cursor()
    cur.execute("DROP TABLE IF EXISTS users")
    cur.execute("""
        CREATE TABLE users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            Nom VARCHAR(255) NOT NULL,
            Prenom VARCHAR(255) NOT NULL,
            Username VARCHAR(255) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL
        )
    """)
    mysql.connection.commit()
    cur.close()
    click.echo('Initialized the database.')

app.cli.add_command(create_db_command)
app.cli.add_command(init_db_command)

@app.route('/')
@jwt_required(optional=True)
def index():
    try:
        print("Entering index function.")
        print("Index function - Request Headers:", request.headers)
        current_user = get_jwt_identity()
        print(f"Current user from JWT: {current_user}")
        if current_user:
            print("User is authenticated, sending index.html.")
            return send_from_directory('frontend', 'index.html')
        else:
            print("User is not authenticated, sending login.html.")
            return send_from_directory('frontend', 'login.html')
    except Exception as e:
        print(f"An error occurred in the index function: {e}")
        return "An internal error occurred.", 500

@app.route('/<path:path>')
def serve_frontend(path):
    print(f"Serving frontend file: {path}")
    return send_from_directory('frontend', path)

@app.route('/api/register', methods=['POST'])
def register():
    print("Received registration request. Headers:", request.headers)
    if not request.headers.get('Content-Type', '').startswith('application/json'):
        print("Request is not JSON. Content-Type:", request.headers.get('Content-Type'))
        return jsonify({"message": "Unsupported Media Type: Content-Type must be application/json"}), 415
    
    data = request.get_json()
    
    # Check if data is None, which can happen if Content-Type is wrong or body is malformed
    if data is None:
        print("Failed to parse JSON data from request.")
        return jsonify({"message": "Bad Request: Could not parse JSON data"}), 400

    # Validate required fields
    required_fields = ['Nom', 'Prenom', 'Username', 'password']
    for field in required_fields:
        if not data.get(field):
            print(f"Missing required field: {field}")
            return jsonify({"message": f"Missing required field: {field}"}), 400

    nom = data['Nom']
    prenom = data['Prenom']
    username = data['Username']
    password = data['password'].encode('utf-8')
    hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())

    cur = mysql.connection.cursor()
    try:
        cur.execute("INSERT INTO users (Nom, Prenom, Username, password) VALUES (%s, %s, %s, %s)", (nom, prenom, username, hashed_password))
        mysql.connection.commit()
        cur.close()
        print(f"User registered successfully: {username}")
        return jsonify({'message': 'User registered successfully'}), 201
    except Exception as e:
        print(f"Registration error: {e}")
        cur.close()
        # Check if it's a duplicate key error
        if 'Duplicate entry' in str(e) or 'UNIQUE constraint failed' in str(e):
            return jsonify({'message': 'Username already exists'}), 409
        else:
            return jsonify({'message': 'Registration failed due to server error'}), 500

@app.route('/api/login', methods=['POST'])
def login():
    print("Received login request. Headers:", request.headers)
    if not request.headers.get('Content-Type', '').startswith('application/json'):
        print("Request is not JSON. Content-Type:", request.headers.get('Content-Type'))
        return jsonify({"message": "Unsupported Media Type: Content-Type must be application/json"}), 415
    
    data = request.get_json()
    
    # Check if data is None, which can happen if Content-Type is wrong or body is malformed
    if data is None:
        print("Failed to parse JSON data from request.")
        return jsonify({"message": "Bad Request: Could not parse JSON data"}), 400

    username = data.get('Username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"message": "Missing username or password"}), 400

    password = password.encode('utf-8')

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE Username = %s", [username])
    user = cur.fetchone()
    cur.close()

    if user and bcrypt.checkpw(password, user['password'].encode('utf-8')):
        # Handle NULL values from database and create clean user identity
        user_identity = {
            'Username': user['Username'] or 'Unknown User',
            'Nom': user['Nom'] or '',
            'Prenom': user['Prenom'] or ''
        }
        print(f"Login successful for user: {user_identity}")
        # Store only the username in JWT token (Flask-JWT-Extended requires string identity)
        access_token = create_access_token(identity=user_identity['Username'])
        response = jsonify({'message': 'Login successful'})
        set_access_cookies(response, access_token)
        return response
    else:
        return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/logout')
def logout():
    response = make_response(jsonify({"msg": "Logout successful"}), 200)
    unset_jwt_cookies(response)
    return response

@app.route('/api/profile')
@jwt_required()
def profile():
    try:
        username = get_jwt_identity()  # This is now just the username string
        print(f"Profile endpoint - username from JWT: {username}")
        print(f"Profile endpoint - username type: {type(username)}")
        
        if username:
            # Look up the full user data from database
            cur = mysql.connection.cursor()
            cur.execute("SELECT Username, Nom, Prenom FROM users WHERE Username = %s", [username])
            user = cur.fetchone()
            cur.close()
            
            if user:
                user_data = {
                    'Username': user['Username'] or 'Unknown User',
                    'Nom': user['Nom'] or '',
                    'Prenom': user['Prenom'] or ''
                }
                print(f"Profile endpoint - returning user data: {user_data}")
                return jsonify(logged_in_as=user_data), 200
            else:
                print(f"Profile endpoint - user not found in database: {username}")
                return jsonify(logged_in_as=None), 404
        else:
            print("Profile endpoint - no username in JWT")
            return jsonify(logged_in_as=None), 404
    except Exception as e:
        print(f"Profile endpoint error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Profile lookup failed', 'message': str(e)}), 500

# Hypervisor Management APIs

@app.route('/api/providers/status', methods=['GET'])
@jwt_required()
def get_providers_status():
    """Get status of all hypervisor providers"""
    try:
        status = hypervisor_manager.get_provider_status()
        return jsonify({'success': True, 'providers': status})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/providers', methods=['GET'])
@jwt_required()
def get_providers():
    """Get list of available providers"""
    try:
        providers = hypervisor_manager.get_available_providers()
        return jsonify({'success': True, 'providers': providers})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/templates', methods=['GET'])
@jwt_required()
def get_templates():
    """Get available templates"""
    try:
        provider = request.args.get('provider')
        templates = hypervisor_manager.get_templates(provider)
        return jsonify({'success': True, 'templates': templates})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/clusters', methods=['GET'])
@jwt_required()
def get_clusters():
    """Get available clusters"""
    try:
        provider = request.args.get('provider')
        clusters = hypervisor_manager.get_clusters(provider)
        return jsonify({'success': True, 'clusters': clusters})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/networks', methods=['GET'])
@jwt_required()
def get_networks():
    """Get available networks"""
    try:
        provider = request.args.get('provider')
        networks = hypervisor_manager.get_networks(provider)
        return jsonify({'success': True, 'networks': networks})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# VM Management APIs

@app.route('/api/vms', methods=['GET'])
@jwt_required()
def list_vms():
    """List all VMs"""
    try:
        provider_name = request.args.get('provider')
        
        if provider_name:
            # If a specific provider is requested, list VMs only from that provider
            vms = hypervisor_manager.list_vms(provider_name)
        else:
            # If no provider is specified, list VMs from all enabled providers
            vms = hypervisor_manager.list_vms()
        
        # Convert VMInfo objects to dictionaries
        vm_list = []
        for vm in vms:
            vm_dict = {
                'name': vm.name,
                'uuid': vm.uuid,
                'state': vm.state,
                'cpu': vm.cpu,
                'ram': vm.ram,
                'disk': vm.disk,
                'ip_address': vm.ip_address,
                'hypervisor': vm.hypervisor,
                'cluster': vm.cluster
            }
            vm_list.append(vm_dict)
        
        return jsonify({'success': True, 'vms': vm_list})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/vms/<vm_name>', methods=['GET'])
@jwt_required()
def get_vm_info(vm_name):
    """Get VM information"""
    try:
        provider = request.args.get('provider')
        vm_info = hypervisor_manager.get_vm_info(vm_name, provider)
        
        if vm_info:
            vm_dict = {
                'name': vm_info.name,
                'uuid': vm_info.uuid,
                'state': vm_info.state,
                'cpu': vm_info.cpu,
                'ram': vm_info.ram,
                'disk': vm_info.disk,
                'ip_address': vm_info.ip_address,
                'hypervisor': vm_info.hypervisor,
                'cluster': vm_info.cluster
            }
            return jsonify({'success': True, 'vm': vm_dict})
        else:
            return jsonify({'success': False, 'error': 'VM not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/vms', methods=['POST'])
@jwt_required()
def create_vm():
    """Create a new VM"""
    try:
        data = request.get_json()
        
        # Get available IP
        ip_address = get_available_ip()
        
        # Create VM configuration
        vm_config = VMConfig(
            name=data['vm_name'],
            cpu=int(data.get('cpu', 2)),
            ram=int(data.get('ram', 2048)),
            disk=int(data.get('disk', 20)),
            os_type=data.get('os_type', 'linux'),
            network=data.get('network'),
            ip_address=ip_address,
            template=data.get('template'),
            cluster=data.get('cluster')
        )
        
        provider = data.get('provider')
        
        # Check if provider is enabled
        status = hypervisor_manager.get_provider_status()
        if provider not in status:
            return jsonify({'success': False, 'error': f'Provider {provider} not found'}), 400
        
        if not status[provider]['enabled']:
            return jsonify({'success': False, 'error': f'Provider {provider} is not enabled. Please enable it in settings.'}), 400
        
        result = hypervisor_manager.create_vm(vm_config, provider)
        
        if result.get('success'):
            return jsonify(result)
        else:
            try:
                print("Create VM error:", result.get('error', ''))
                if 'stdout' in result and isinstance(result['stdout'], str):
                    # Print the tail to avoid flooding logs
                    print("Create VM stdout (tail):", result['stdout'][-2000:])
            except Exception:
                pass
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/vms/clone', methods=['POST'])
@jwt_required()
def clone_vm():
    """Clone a VM"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['vm_name', 'provider', 'source_vm']
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return jsonify({'success': False, 'error': f"Missing required fields: {', '.join(missing_fields)}"}), 400
        
        # Get available IP
        ip_address = get_available_ip()
        
        # Create VM configuration
        vm_config = VMConfig(
            name=data['vm_name'],
            cpu=int(data.get('cpu', 2)),
            ram=int(data.get('ram', 2048)),
            disk=int(data.get('disk', 20)),
            os_type=data.get('os_type', 'unknown'),
            network=data.get('network'),
            ip_address=ip_address,
            cluster=data.get('cluster')
        )
        
        provider = data.get('provider')
        
        # Check if provider is enabled
        status = hypervisor_manager.get_provider_status()
        if provider not in status:
            return jsonify({'success': False, 'error': f'Provider {provider} not found'}), 400
        
        if not status[provider]['enabled']:
            return jsonify({'success': False, 'error': f'Provider {provider} is not enabled. Please enable it in settings.'}), 400
        
        source_vm = data['source_vm']
        result = hypervisor_manager.clone_vm(source_vm, vm_config, provider)
        
        if result.get('success'):
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/vms/<vm_name>/start', methods=['POST'])
@jwt_required()
def start_vm(vm_name):
    """Start a VM"""
    try:
        provider = request.args.get('provider')
        success = hypervisor_manager.start_vm(vm_name, provider)
        
        if success:
            return jsonify({'success': True, 'message': f"VM '{vm_name}' started successfully"})
        else:
            return jsonify({'success': False, 'error': f"Failed to start VM '{vm_name}'"}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/vms/<vm_name>/stop', methods=['POST'])
@jwt_required()
def stop_vm(vm_name):
    """Stop a VM"""
    try:
        provider = request.args.get('provider')
        success = hypervisor_manager.stop_vm(vm_name, provider)
        
        if success:
            return jsonify({'success': True, 'message': f"VM '{vm_name}' stopped successfully"})
        else:
            return jsonify({'success': False, 'error': f"Failed to stop VM '{vm_name}'"}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/vms/<vm_name>/restart', methods=['POST'])
@jwt_required()
def restart_vm(vm_name):
    """Restart a VM"""
    try:
        provider = request.args.get('provider')
        success = hypervisor_manager.restart_vm(vm_name, provider)
        
        if success:
            return jsonify({'success': True, 'message': f"VM '{vm_name}' restarted successfully"})
        else:
            return jsonify({'success': False, 'error': f"Failed to restart VM '{vm_name}'"}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/vms/<vm_name>', methods=['DELETE'])
@jwt_required()
def delete_vm(vm_name):
    """Delete a VM"""
    try:
        provider = request.args.get('provider')
        success = hypervisor_manager.delete_vm(vm_name, provider)
        
        if success:
            return jsonify({'success': True, 'message': f"VM '{vm_name}' deleted successfully"})
        else:
            return jsonify({'success': False, 'error': f"Failed to delete VM '{vm_name}'"}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/vms/<vm_name>/console', methods=['POST'])
@jwt_required()
def open_vm_console(vm_name):
    """Open VM console"""
    try:
        provider = request.args.get('provider')
        result = hypervisor_manager.open_console(vm_name, provider)
        
        if result.get('success'):
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Configuration Management APIs

@app.route('/api/config/providers', methods=['POST'])
@jwt_required()
def update_provider_config():
    """Update provider configuration"""
    try:
        data = request.get_json()
        provider = data.get('provider')
        config = data.get('config')
        
        if not provider or not config:
            return jsonify({'success': False, 'error': 'Provider and config are required'}), 400
        
        # Update the configuration
        success = hypervisor_manager.update_provider_config(provider, config)
        
        if success:
            return jsonify({'success': True, 'message': f'{provider.title()} configuration updated successfully'})
        else:
            return jsonify({'success': False, 'error': 'Failed to update configuration'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/config/default-provider', methods=['POST'])
@jwt_required()
def set_default_provider():
    """Set default provider"""
    try:
        data = request.get_json()
        provider = data.get('provider')
        
        if not provider:
            return jsonify({'success': False, 'error': 'Provider is required'}), 400
        
        success = hypervisor_manager.set_default_provider(provider)
        
        if success:
            return jsonify({'success': True, 'message': f'Default provider set to {provider}'})
        else:
            return jsonify({'success': False, 'error': 'Failed to set default provider'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/config', methods=['GET'])
@jwt_required()
def get_config():
    """Get current configuration"""
    try:
        config = hypervisor_manager.get_config()
        return jsonify({'success': True, 'config': config})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Snapshot Management APIs

@app.route('/api/vms/<vm_name>/snapshots', methods=['POST'])
@jwt_required()
def create_snapshot(vm_name):
    """Create a VM snapshot"""
    try:
        data = request.get_json()
        snapshot_name = data['snapshot_name']
        provider = data.get('provider')
        
        success = hypervisor_manager.create_snapshot(vm_name, snapshot_name, provider)
        
        if success:
            return jsonify({'success': True, 'message': f"Snapshot '{snapshot_name}' created for VM '{vm_name}'"})
        else:
            return jsonify({'success': False, 'error': f"Failed to create snapshot '{snapshot_name}' for VM '{vm_name}'"}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/vms/<vm_name>/snapshots/<snapshot_name>/restore', methods=['POST'])
@jwt_required()
def restore_snapshot(vm_name, snapshot_name):
    """Restore a VM snapshot"""
    try:
        provider = request.args.get('provider')
        success = hypervisor_manager.restore_snapshot(vm_name, snapshot_name, provider)
        
        if success:
            return jsonify({'success': True, 'message': f"Snapshot '{snapshot_name}' restored for VM '{vm_name}'"})
        else:
            return jsonify({'success': False, 'error': f"Failed to restore snapshot '{snapshot_name}' for VM '{vm_name}'"}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/vms/<vm_name>/snapshots/<snapshot_name>', methods=['DELETE'])
@jwt_required()
def delete_snapshot(vm_name, snapshot_name):
    """Delete a VM snapshot"""
    try:
        provider = request.args.get('provider')
        success = hypervisor_manager.delete_snapshot(vm_name, snapshot_name, provider)
        
        if success:
            return jsonify({'success': True, 'message': f"Snapshot '{snapshot_name}' deleted for VM '{vm_name}'"})
        else:
            return jsonify({'success': False, 'error': f"Failed to delete snapshot '{snapshot_name}' for VM '{vm_name}'"}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Legacy endpoint for backward compatibility
@app.route('/clone_vm', methods=['POST'])
@jwt_required()
def legacy_clone_vm():
    """Legacy clone VM endpoint for backward compatibility"""
    try:
        vm_name = request.form['vm_name']
        cpu = request.form['cpu']
        ram = request.form['ram']
        disk = request.form['disk']
        os_type = request.form['os_type']
        
        # Get available IP
        ip_address = get_available_ip()
        
        # Create VM configuration
        vm_config = VMConfig(
            name=vm_name,
            cpu=int(cpu),
            ram=int(ram),
            disk=int(disk),
            os_type=os_type,
            ip_address=ip_address
        )
        
        # Use VMware provider for legacy compatibility
        result = hypervisor_manager.clone_vm("default_template", vm_config, "vmware")
        
        if result.get('success'):
            return f"VM '{vm_name}' created successfully!\n<pre>{result.get('message')}</pre>"
        else:
            return f"Error creating VM '{vm_name}':\n<pre>{result.get('error')}</pre>"
            
    except Exception as e:
        return f"Error creating VM '{vm_name}':\n<pre>{str(e)}</pre>"

# Mock Server Management Endpoints
@app.route('/api/mock-server/status', methods=['GET'])
@jwt_required()
def get_mock_server_status():
    """Get the status of the Nutanix mock server"""
    try:
        is_healthy = check_mock_server_health()
        is_running = mock_server_process and mock_server_process.poll() is None
        
        return jsonify({
            'success': True,
            'status': {
                'running': is_running,
                'healthy': is_healthy,
                'pid': mock_server_process.pid if is_running else None,
                'url': 'http://127.0.0.1:9441'
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/mock-server/restart', methods=['POST'])
@jwt_required()
def restart_mock_server():
    """Restart the Nutanix mock server"""
    try:
        global mock_server_process
        
        # Stop existing server if running
        if mock_server_process and mock_server_process.poll() is None:
            print("Stopping existing mock server...")
            mock_server_process.terminate()
            try:
                mock_server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                mock_server_process.kill()
                mock_server_process.wait()
        
        # Start new server
        start_nutanix_mock_server()
        
        # Wait a moment and check if it's healthy
        time.sleep(3)
        is_healthy = check_mock_server_health()
        
        return jsonify({
            'success': True,
            'message': 'Mock server restarted',
            'healthy': is_healthy
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.errorhandler(ExpiredSignatureError)
def handle_expired_token(e):
    return redirect('/login.html')

# JWT Error Handlers
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    """Handle expired JWT tokens"""
    return jsonify({'msg': 'Token has expired'}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    """Handle invalid JWT tokens (including 'Subject must be a string' errors)"""
    print(f"Invalid token error: {error}")
    return jsonify({'msg': 'Invalid token format. Please log in again.'}), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    """Handle missing JWT tokens"""
    return jsonify({'msg': 'Authorization token is required'}), 401

@app.errorhandler(InvalidHeaderError)
def handle_invalid_header_error(e):
    """Handle JWT invalid header errors"""
    print(f"JWT Invalid header error: {e}")
    return jsonify({'msg': 'Invalid authorization header format'}), 401

@app.errorhandler(NoAuthorizationError)
def handle_no_authorization_error(e):
    """Handle JWT no authorization errors"""
    print(f"JWT No authorization error: {e}")
    return jsonify({'msg': 'Authorization token is required'}), 401

@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    """Handle JWT CSRF errors"""
    print(f"JWT CSRF error: {e}")
    return jsonify({'msg': 'CSRF token error'}), 401

@app.errorhandler(RevokedTokenError)
def handle_revoked_token_error(e):
    """Handle JWT revoked token errors"""
    print(f"JWT Revoked token error: {e}")
    return jsonify({'msg': 'Token has been revoked'}), 401

@app.errorhandler(InvalidTokenError)
def handle_invalid_token_error(e):
    """Handle general JWT invalid token errors"""
    print(f"JWT Invalid token error: {e}")
    return jsonify({'msg': 'Invalid token. Please log in again.'}), 401

@app.errorhandler(DecodeError)
def handle_decode_error(e):
    """Handle JWT decode errors"""
    print(f"JWT Decode error: {e}")
    return jsonify({'msg': 'Token decode error. Please log in again.'}), 401

# Handle generic JWT processing errors
@app.errorhandler(422)
def handle_unprocessable_entity(e):
    """Handle JWT unprocessable entity errors (like invalid header padding)"""
    print(f"JWT Unprocessable entity error: {e}")
    # Check if this is a JWT-related error
    error_description = str(e.description) if hasattr(e, 'description') else str(e)
    if any(jwt_error in error_description.lower() for jwt_error in ['padding', 'token', 'jwt', 'header']):
        return jsonify({'msg': 'Invalid token format. Please log in again.'}), 401
    # If not JWT-related, return the original error
    return jsonify({'msg': 'Unprocessable entity'}), 422

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)