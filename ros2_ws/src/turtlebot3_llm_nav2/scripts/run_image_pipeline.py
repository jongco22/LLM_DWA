#!/usr/bin/env python3
# /workspace/ros2_ws/src/turtlebot3_llm_nav2/scripts/run_image_pipeline.py

from get_user_input import get_start_goal
import sys
import os

script_dir = os.path.dirname(__file__) # This is /workspace/ros2_ws/src/turtlebot3_llm_nav2/scripts
# This adds /workspace/ros2_ws/src/turtlebot3_llm_nav2 to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(script_dir, '..')))

from call_image import call_llm
import base64



# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


# Path to your image
image_path = "/workspace/ros2_ws/src/turtlebot3_llm_nav2/image/jh_world_2.png"

# Getting the Base64 string
base64_image = encode_image(image_path)

def main():
    start, goal = get_start_goal()
    call_llm(base64_image, start, goal, '/workspace/ros2_ws/src/turtlebot3_llm_nav2/data/waypoints.json')


if __name__ == "__main__":
    main()
