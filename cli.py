import argparse
from bus_eta import get_bus_eta
import json
from datetime import datetime

def format_eta(eta_data):
    """Format ETA data for CLI output"""
    formatted = []
    for eta in eta_data:
        eta_time = datetime.fromisoformat(eta['eta'].replace('Z', '+00:00'))
        local_time = eta_time.astimezone()
        formatted.append({
            'route': eta['route'],
            'direction': eta['dir'],
            'eta': local_time.strftime('%H:%M:%S'),
            'remarks': eta['rmk_en']
        })
    return formatted

def main():
    parser = argparse.ArgumentParser(description='Hong Kong Bus ETA Checker')
    parser.add_argument('route', help='Bus route number')
    parser.add_argument('stop_id', help='Bus stop ID')
    parser.add_argument('--company', default='KMB', help='Bus company (default: KMB)')
    parser.add_argument('--json', action='store_true', help='Output in JSON format')
    
    args = parser.parse_args()
    
    etas = get_bus_eta(args.route, args.stop_id, args.company)
    
    if not etas:
        print("No ETA data found.")
        return
    
    if args.json:
        print(json.dumps(format_eta(etas), indent=2)
    else:
        print(f"\nBus ETAs for route {args.route} at stop {args.stop_id}:")
        for eta in format_eta(etas):
            print(f"{eta['eta']} - {eta['remarks']} (Direction: {eta['direction']})")

if __name__ == "__main__":
    main()
