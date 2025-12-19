#!/usr/bin/env python3
from get_user_input import get_start_goal
import sys
import os

script_dir = os.path.dirname(__file__) # This is /workspace/ros2_ws/src/turtlebot3_llm_nav2/scripts
# This adds /workspace/ros2_ws/src/turtlebot3_llm_nav2 to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(script_dir, '..')))

from call_llm import call_llm 

def main():
    start, goal = get_start_goal()
    call_llm(start, goal, '/workspace/ros2_ws/src/turtlebot3_llm_nav2/data/obstacle.json', '/workspace/ros2_ws/src/turtlebot3_llm_nav2/data/waypoints.json')


if __name__ == "__main__":
    main()
