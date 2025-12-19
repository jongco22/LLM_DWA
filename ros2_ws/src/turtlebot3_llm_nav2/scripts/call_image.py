# /workspace/ros2_ws/src/turtlebot3_llm_nav2/scripts/call_image.py

import json
from api.api_image_1shot import get_waypoints

def call_llm(image, start, goal, output_path):
    waypoints = get_waypoints(image, start, goal)
    with open(output_path, 'w') as f:
        json.dump({"waypoints": waypoints}, f, indent=2)


