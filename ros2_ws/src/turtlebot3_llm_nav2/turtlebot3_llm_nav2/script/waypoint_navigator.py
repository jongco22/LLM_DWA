#!/usr/bin/env python3

# /workspace/ros2_ws/src/turtlebot3_llm_nav2/turtlebot3_llm_nav2/script/waypoint_navigator.py

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateThroughPoses
from rclpy.action import ActionClient
import json
import math
from tf_transformations import quaternion_from_euler

class WaypointNavigator(Node):
    def __init__(self):
        super().__init__('waypoint_navigator')

        # NavigateThroughPoses 액션 클라이언트 생성
        self._action_client = ActionClient(self, NavigateThroughPoses, 'navigate_through_poses')

        # Waypoint 도달 체크용 상태 변수
        self.prev_poses_remaining = None

        # Waypoints 파일 읽기
        try:
            with open('/workspace/ros2_ws/src/turtlebot3_llm_nav2/data/waypoints.json') as f:
                self.waypoints = json.load(f)['waypoints']
                self.get_logger().info(f'Loaded {len(self.waypoints)} waypoints')
        except Exception as e:
            self.get_logger().error(f'Failed to load waypoint: {e}')
            self.waypoints = []

        # 서버 연결 후 전송
        self.send_goal()

    def send_goal(self):
        # 서버 준비 대기
        self.get_logger().info('Waiting for NavigateThroughPoses action server...')
        self._action_client.wait_for_server()

        # PoseStamped 리스트 생성
        poses = []
        for i, (x, y) in enumerate(self.waypoints):
            pose = PoseStamped()
            pose.header.frame_id = 'map'
            pose.header.stamp = self.get_clock().now().to_msg()

            pose.pose.position.x = float(x)
            pose.pose.position.y = float(y)

            # Yaw 계산 (다음 포인트를 기준으로)
            if i < len(self.waypoints) - 1:
                nx, ny = self.waypoints[i + 1]
                dx, dy = nx - x, ny - y
                yaw = math.atan2(dy, dx)
            else:
                yaw = 0.0
            qx, qy, qz, qw = quaternion_from_euler(0, 0, yaw)
            pose.pose.orientation.x = qx
            pose.pose.orientation.y = qy
            pose.pose.orientation.z = qz
            pose.pose.orientation.w = qw

            poses.append(pose)

        # Goal 생성
        goal_msg = NavigateThroughPoses.Goal()
        goal_msg.poses = poses
        goal_msg.behavior_tree = ''  # 기본 BT 사용

        self.get_logger().info('Sending waypoints to NavigateThroughPoses...')
        send_goal_future = self._action_client.send_goal_async(goal_msg, feedback_callback=self.feedback_callback)
        send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error('Goal rejected by server')
            return
        self.get_logger().info('Goal accepted')
        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self, future):
        result = future.result().result
        self.get_logger().info('Navigation finished successfully')
        rclpy.shutdown()

    def feedback_callback(self, feedback_msg):
        feedback = feedback_msg.feedback
        # number_of_poses_remaining 값이 감소할 때만 로그 출력
        if self.prev_poses_remaining is None or feedback.number_of_poses_remaining < self.prev_poses_remaining:
            self.get_logger().info(
                f"Waypoint reached! Remaining: {feedback.number_of_poses_remaining} | "
                f"Current pose: {feedback.current_pose} | "
                f"Navigation time: {feedback.navigation_time} | "
                f"Number of recoveries: {feedback.number_of_recoveries} | "
                f"Distance remaining: {feedback.distance_remaining}"
            )
        self.prev_poses_remaining = feedback.number_of_poses_remaining

def main(args=None):
    rclpy.init(args=args)
    node = WaypointNavigator()
    rclpy.spin(node)

if __name__ == '__main__':
    main()
