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


        Example:
        Input:
            start = [-7, -6]
            goal = [-7, 5]
            obstacles: [
            {{
            "x": -7.997,
            "y": -7.625,
            "width": 16.0,
            "depth": 0.15,
            "height": 2.5
            }},
            {{
            "x": 7.853,
            "y": -7.625,
            "width": 0.15,
            "depth": 15.25,
            "height": 2.5
            }},
            {{
            "x": -6.982,
            "y": 7.475,
            "width": 13.97,
            "depth": 0.15,
            "height": 2.5
            }},
            {{
            "x": -7.997,
            "y": -6.651,
            "width": 0.15,
            "depth": 13.303,
            "height": 2.5
            }},
            {{
            "x": -6.173,
            "y": 5.403,
            "width": 4.35,
            "depth": 0.5,
            "height": 2.5
            }},
            {{
            "x": -8.003,
            "y": 0.921,
            "width": 13.35,
            "depth": 0.5,
            "height": 2.5
            }},
            {{
            "x": -1.218,
            "y": -3.199,
            "width": 0.5,
            "depth": 4.6,
            "height": 2.5
            }},
            {{
            "x": -4.549,
            "y": -5.714,
            "width": 0.5,
            "depth": 5.1,
            "height": 2.5
            }},
            {{
            "x": -4.549,
            "y": -5.714,
            "width": 7.6,
            "depth": 0.5,
            "height": 2.5
            }},
            {{
            "x": 2.551,
            "y": -5.714,
            "width": 0.5,
            "depth": 4.35,
            "height": 2.5
            }},
            {{
            "x": 6.472,
            "y": -6.703,
            "width": 0.5,
            "depth": 6.85,
            "height": 2.5
            }}
            ]
            


        -First iteration on [-7, -6]
        Thought: The obstacle at [-4.549, -5.714, 0.5, 5.1, 2.5] blocks the direct path to the goal. To navigate around it, we should move to upper-left corner of the obstacles.
        Selected Point: [-5, 0.5]
        Evaluation: The selected point [-5, 0.5] effectively bypasses the obstacle, positioning us at its corner and maintaining progress toward the goal without encountering additional obstacles.
        -Second iteration on [-5, 0.5]
        Thought: The obstacle at [-4.549, -5.714, 0.5, 5.1, 2.5] blocks the direct path to the goal. To navigate around it, we should move to the lower-left corner of the obstacle.
        Selected Point: [-2, -4]
        Evaluation: The selected point [-2, -4] effectively bypasses the obstacle, positioning us at its corner and maintaining progress toward the goal without encountering additional obstacles.
        -Third iteration on [-2, -4]
        Thought: When the robot is at [-2, -4], it is trapped inside a U-shaped obstacle formed by three obstacles: [-4.549, -5.714, 0.5, 5.1, 2.5], [-4.549, -5.714, 7.6, 0.5, 2.5] and [2.551, -5.714, 0.5, 4.35, 2.5]. To avoid getting stuck in a local minima, an intermediate waypoint is set near the obstacles' edge at [2, -0.5].
        Selected Point: [2, -0.5]
        Evaluation: The selected point [2, -0.5] successfully navigates around the U-shaped obstacle, allowing the robot to continue toward the goal without getting trapped.
        -Fourth iteration on [2, -0.5]
        Thought: When the robot is at [2, -0.5], it is blocks the direct path to the goal about obstacles that [-8.003, 0.921, 13.35, 0.5, 2.5], [6.472, -6.703, 0.5, 6.85, 2.5]. To avoid obstacles, and achieve the goal intermediate waypoint is between obstacles at [6.0, 1.0].
        Selected Point: [6.0, 1.0]
        Evaluation: The path to the goal is clear from here, allowing a direct move to the goal.

        "waypoints": [[-7, -6], [-5, 0.5], [-2, -4], [2, -0.5], [6.0, 1.0], [-7, 5]]

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
    print(f"API calling time: {end_time - start_time:.2f}초")
    return waypoints

if __name__ == "__main__":
    start = (-2.0, -2.0)
    goal = (6.0, 5.0)
    obstacles = [
        (-4.0, 3.0, 2.0, 1.0, 2.5),
        (2.0, 0.0, 3.0, 1.5, 2.5)
    ]
    get_waypoints(start, goal, obstacles)
