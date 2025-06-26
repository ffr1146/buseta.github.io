from flask import Flask, render_template, request, jsonify
from bus_eta import get_bus_eta
from datetime import datetime
import pytz

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/eta')
def get_eta():
    route = request.args.get('route')
    stop_id = request.args.get('stop_id')
    company = request.args.get('company', 'KMB')
    
    if not route or not stop_id:
        return jsonify({'error': 'Missing route or stop_id parameter'}), 400
    
    etas = get_bus_eta(route, stop_id, company)
    
    if not etas:
        return jsonify({'error': 'No ETA data found'}), 404
    
    # Format the response
    hk_tz = pytz.timezone('Asia/Hong_Kong')
    formatted_etas = []
    for eta in etas:
        eta_time = datetime.fromisoformat(eta['eta'].replace('Z', '+00:00'))
        local_time = eta_time.astimezone(hk_tz)
        formatted_etas.append({
            'route': eta['route'],
            'eta': local_time.strftime('%H:%M:%S'),
            'remarks': eta['rmk_en'],
            'direction': eta['dir']
        })
    
    return jsonify({'data': formatted_etas})

if __name__ == '__main__':
    app.run(debug=True)
