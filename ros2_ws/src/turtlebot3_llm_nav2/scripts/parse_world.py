# /workspace/ros2_ws/src/turtlebot3_llm_nav2/scripts/parse_world.py

import xml.etree.ElementTree as ET
import json
import sys
import os

def parse_world(input_path, output_path):
    tree = ET.parse(input_path)
    root = tree.getroot()
    obstacles = []
    # input_path에서 world 앞의 이름 추출
    basename = os.path.basename(input_path)
    model_name = basename.split('.world')[0]
    for link in root.findall(f".//model[@name='{model_name}']/link"):
        pose_elem = link.find("pose")
        size_elem = link.find(".//box/size")
        if pose_elem is None or size_elem is None:
            continue
        px, py, pz, roll, pitch, yaw = map(float, pose_elem.text.strip().split())
        sx, sy, sz = map(float, size_elem.text.strip().split())
        if abs(abs(yaw) - 1.5708) < 0.01:
            # 90도 회전이면 width <-> depth
            width, depth = sy, sx
            # 중심 -> 왼쪽 아래 계산
            ox = px - width / 2
            oy = py - depth / 2
        else:
            width, depth = sx, sy
            ox = px - width / 2
            oy = py - depth / 2

        obstacles.append({
            "x": round(ox, 3),
            "y": round(oy, 3),
            "width": round(width, 3),
            "depth": round(depth, 3),
            "height": round(sz, 3)
        })
    
    with open(output_path, 'w') as f:
        json.dump({"obstacles": obstacles}, f, indent=2)


if __name__ == "__main__":
    parse_world(sys.argv[1], sys.argv[2])
