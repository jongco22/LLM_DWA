# api
# /workspace/ros2_ws/src/turtlebot3_llm_nav2/api/api_image.py
import json
import time
import openai 
import re
from dotenv import load_dotenv
import os

dotenv_path = '/workspace/ros2_ws/.env' 
load_dotenv(dotenv_path)
api_key = os.getenv('OPENAI_API_KEY')
openai.api_key = api_key



sysprompt = """
# ROLE
You are an expert path planning agent for a mobile robot navigating simulated indoor environments.

# CONTEXT
You are given:
- A top-down image of a 3D environment from a simulator like Gazebo.
- Start and goal positions in the environment.
- The image represents walls, doors, and open spaces from a bird’s eye view.

# MAP INTERPRETATION
- Thick structures forming enclosed shapes are walls — they are impassable.
- Open gaps in those structures indicate doorways or passages.
- Lighter or empty areas are navigable free space.
- The robot must move through these passages (not through walls) to reach the goal.
- In some environments, additional obstacles such as furniture or partitions may exist; these should be avoided.
- The robot is differential-drive, so smooth turns are preferred over sharp corners.

# OBJECTIVE
Compute a path from the start to the goal position using intermediate (x, y) waypoints.
The path must:
1. Stay within navigable free space.
2. Move through passages and avoid walls.
3. Avoid static obstacles and furniture.
4. Be efficient (shorter path preferred).
5. Be smooth, with minimal sharp turns.

# OUTPUT FORMAT
Return ONLY a valid JSON object:
{
  "waypoints": [[x1, y1], [x2, y2], ..., [xn, yn]]
}

Do not include any explanation, markdown, or natural language text.
"""

def get_waypoints(image, start, goal):
    start_time = time.time()

    user_prompt = f"""
    Given the following map image (centered at (0,0), 1 unit per grid square), compute a feasible path from:

    Start: {start}  
    Goal: {goal}

    Return the waypoints in this format:
    {{
    "waypoints": [[x_start, y_start], [x2, y2], ..., [x_goal, y_goal]]
    }}
    """

    response = openai.ChatCompletion.create(
        model="gpt-4o",  
        messages=[
            {
                "role": "system",
                "content": sysprompt.strip()
            },
            {
                "role": "user",
                "content": [
                    { "type": "text", "text": user_prompt.strip() },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image}"
                        }
                    }
                ]
            }
        ],
        max_tokens=500
    )

    response_content = response.choices[0].message.content
    print(f"response: {response_content}")

    def extract_waypoints(response_content):
        try:
            cleaned = re.sub(r"```(?:json)?\s*([\s\S]*?)\s*```", r"\1", response_content).strip()
            parsed = json.loads(cleaned)
            return parsed["waypoints"]
        except Exception as e:
            print("JSON parsing or extraction error:", e)
            raise e

    waypoints = extract_waypoints(response_content)
    end_time = time.time()
    print("Extracted Waypoints:", waypoints)
    print(f"API 호출 시간: {end_time - start_time:.2f}초")
    return waypoints


# if __name__ == "__main__":
#     map = base64_image
#     start = (-7.0, -6.0)
#     goal = (5.0, 5.0)
    
#     get_waypoints(map, start, goal)
