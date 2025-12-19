# api
# /workspace/ros2_ws/src/turtlebot3_llm_nav2/api/api.py
import openai
import json
import time
import os
from dotenv import load_dotenv

dotenv_path = '/workspace/ros2_ws/.env' 
load_dotenv(dotenv_path)
api_key = os.getenv('OPENAI_API_KEY')
openai.api_key = api_key

# 시스템 프롬프트 설정
sysprompt = """
You are a robot path planner using waypoints for a mobile robot in a Gazebo + ROS2 environment.

You will be given a start(x_start, y_start), goal(x_goal, y_goal), and a list of obstacles (x, y, width, depth, height).

You are allowed to think step by step — reasoning helps you avoid obstacles and select safe waypoints.

However, your final output MUST ONLY be a valid JSON object like:
{
  "waypoints": [[x1, y1], [x2, y2], ..., [xn, yn]]
}

Do NOT include any explanation, markdown, or comments in the output.
"""


def get_waypoints(start, goal, obstacles):
    start_time = time.time()
    
    user_prompt = f"""
    Please generate a sequence of waypoints that creates the fastest possible path to the goal, avoiding all obstacles.
        Input:
            Start: {start}
            Goal: {goal}
            Obstacles: {obstacles}

        Output Format:
        {{
        "waypoints": [[start_x, start_y], [x2, y2], ..., [goal_x, goal_y]]
        }}

        """

    response = openai.ChatCompletion.create(
        model='gpt-4-turbo',
        temperature=0.5,
        messages=[
            {"role": "system", "content": sysprompt},
            {"role": "user", "content": user_prompt}
        ]
    )

    def extract_waypoints(response_content):
        try:
            parsed = json.loads(response_content.strip())
            return parsed["waypoints"]
        except Exception as e:
            print("JSON parsing or extraction error:", e)
            raise e

    response_content = response["choices"][0]["message"]["content"]
    print(f"response: {response_content}")
    waypoints = extract_waypoints(response_content)
    end_time = time.time()
    print("Extracted Waypoints:", waypoints)
    print(f"API 호출 시간: {end_time - start_time:.2f}초")
    return waypoints

if __name__ == "__main__":
    start = (-2.0, -2.0)
    goal = (6.0, 5.0)
    obstacles = [
        (-4.0, 3.0, 2.0, 1.0, 2.5),
        (2.0, 0.0, 3.0, 1.5, 2.5)
    ]
    get_waypoints(start, goal, obstacles)
