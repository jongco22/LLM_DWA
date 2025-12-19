# /workspace/ros2_ws/src/turtlebot3_llm_nav2/api/api_image_1shot.py

import json
import time
import openai
import re
import base64
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

def get_waypoints(map_image, start, goal):
    start_time = time.time()
    
    def encode_image(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")


    # Path to your image
    image_path = "/workspace/ros2_ws/src/turtlebot3_llm_nav2/image/house_example.png"

    # Getting the Base64 string
    example_image = encode_image(image_path)
    user_prompt = f"""
    You will be given two images in this order:

    1. Example image: Shows waypoints as red dots for visualization.
    2. Actual map image: The map you must analyze to generate waypoints.

    Example:
    start = [1.0, -1.0]
    goal = [-6.5, -2.0]
    image = {image_path}

    Output:
    {{
        "waypoints": [[1.0, -1.0], [-4.0, 2.0], [-5.0, 4.0], [-6.5, -2.0]]
    }}
    
    Task:
    Given the actual map image, compute a feasible path from:

    Start: {start}  
    Goal: {goal}
    image: {map_image}

    Rules:
    - Place intermediate waypoints only in obstacle-free areas.
    - Output ONLY the list of waypoints in exactly the following JSON format:
    {{
        "waypoints": [[x_start, y_start], [x2, y2], ..., [x_goal, y_goal]]
    }}

    """

    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            { "role": "system", "content": sysprompt.strip() },
            {
                "role": "user",
                "content": [
                    { "type": "text", "text": user_prompt.strip() },
                    { "type": "image_url", "image_url": { "url": f"data:image/png;base64,{example_image}", "detail": "low" } },
                    { "type": "image_url", "image_url": { "url": f"data:image/png;base64,{map_image}", "detail": "low" } }
                ]
            }
        ],
        max_tokens=500
    )

    response_content = response.choices[0].message.content
    print(f"Raw LLM Response: {response_content}")
    
    
    def extract_waypoints(text):
        try:
            # Remove ```json ``` code blocks if present
            cleaned = re.sub(r"```(?:json)?\s*([\s\S]*?)\s*```", r"\1", text).strip()
            parsed = json.loads(cleaned)
            return parsed["waypoints"]
        except Exception as e:
            print("JSON parsing or extraction error:", e)
            raise e

    waypoints = extract_waypoints(response_content)
    end_time = time.time()
    print("Extracted Waypoints:", waypoints)
    print(f"API Call Duration: {end_time - start_time:.2f} seconds")
    return waypoints


if __name__ == "__main__":
    example_image_base64 = "예시_이미지_base64_문자열"
    map_image_base64 = "실제_지도_base64_문자열"
    start = (-7.0, -6.0)
    goal = (5.0, 5.0)

    get_waypoints(example_image_base64, map_image_base64, start, goal)
