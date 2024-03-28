from flask import Flask, request, send_file, abort
import sqlite3, os
from scanner import scanForHosts
from utils import getMacManufacturer
from waitress import serve

connection = sqlite3.connect('database.db')

with open('schema.sqlite') as f:
    connection.executescript(f.read())

def execute_query(q, params):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute(q, params)
    conn.commit()
    conn.close()

def fetch_query(q, params):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute(q, params)
    r = cur.fetchone()
    conn.close()
    return r

def fetch_query_all(q, params):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute(q, params)
    r = cur.fetchall()
    conn.close()
    return r

app = Flask(__name__, static_folder='static',  static_url_path='')

@app.route('/api/scan', methods=['GET'])
def scan_network():
    hosts = scanForHosts(os.getenv('NETWORK_RANGE', '192.168.1.1/24'))
    for h in hosts:
        h['online'] = True
        existing = fetch_query('SELECT * FROM device WHERE mac = ?', (h['mac'],))
        if (existing):
            h['name'] = existing[1]
            h['icon'] = existing[2]
            h['manufacturer'] = existing[3]
            execute_query('UPDATE device SET ip = ? WHERE mac = ?', (h['ip'], h['mac']))
        else:
            manufacturer = getMacManufacturer(h['mac'])
            h['name'] = 'Unknown'
            h['icon'] = 'desktop-classic'
            h['manufacturer'] = manufacturer
            execute_query('INSERT INTO device (mac, name, icon, manufacturer, ip) VALUES (?, ?, ?, ?, ?)', (h['mac'], 'Unknown', 'desktop-classic', manufacturer, h['ip']))
    
    offline = fetch_query_all(f'SELECT * FROM device WHERE mac NOT IN ({ ",".join( list("?" * len(hosts)) ) })', tuple([h['mac'] for h in hosts]))
    
    hosts.extend([ { 'name': e[1], 'icon': e[2], 'mac': e[0], 'ip': e[4], 'manufacturer': e[3], 'online': False } for e in offline ])

    return hosts, 200

@app.route('/api/set-metadata', methods=['POST'])
def set_metadata():
    r = request.json
    mac = r.get('mac', None)
    name = r.get('name', None)
    icon = r.get('icon', None)
    if (mac is None or name is None or icon is None):
        return  {}, 400
    else:
        execute_query('UPDATE device SET name = ?, icon = ? WHERE mac = ?', (name, icon, mac))
        return {}, 200

@app.route('/api/get-db', methods=['GET'])
def get_db():
    return send_file('database.db')

@app.route('/api/upload-db', methods=['POST'])
def upload_db():
    if 'db' not in request.files:
        return abort(400)
    else:
        request.files['db'].save(os.path.join(os.getcwd(), 'database.db'))
        return {}, 200

def page_not_found(e):
    return send_file('static/index.html'), 200
        
app.register_error_handler(404, page_not_found)

def is_docker():
    def text_in_file(text, filename):
        try:
            with open(filename, encoding='utf-8') as lines:
                return any(text in line for line in lines)
        except OSError:
            return False
    cgroup = '/proc/self/cgroup'
    return os.path.exists('/.dockerenv') or text_in_file('docker', cgroup)

if is_docker():
    serve(app, listen=f'*:{os.getenv("LISTEN_PORT", "8800")}')
else:
    app.run(debug=True, host='127.0.0.1', port=5800) 