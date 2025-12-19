# === File: scripts/call_llm.py ===
import json
from api.api_1shot import get_waypoints

def call_llm(start, goal, obstacle_file, output_path):
    with open(obstacle_file) as f:
        obstacles = json.load(f)['obstacles']
    waypoints = get_waypoints(start, goal, obstacles)
    with open(output_path, 'w') as f:
        json.dump({"waypoints": waypoints}, f, indent=2)