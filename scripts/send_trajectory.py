#!/usr/bin/env python3
"""Send one timed, multi-point trajectory to the simulated robot, then exit."""
import math
import sys

import rclpy
from rclpy.duration import Duration
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

JOINTS = ['slider_joint', 'arm_joint']

# shortcut: copied from example_robot.urdf.xacro, read /robot_description if they start changing
LIMITS = [(0.0, 2.0), (0.0, math.pi / 2)]  # slider in metres, arm in radians

# (seconds after the trajectory starts, [slider, arm])
WAYPOINTS = [
    (2.0, [0.5, 0.4]),
    (4.0, [1.5, 1.2]),
    (6.0, [1.0, 0.2]),
    (8.0, [0.0, 0.0]),
]


def build_trajectory(waypoints):
    """Turn waypoints into a message, rejecting any the controller can't follow."""
    if not waypoints:
        raise ValueError('need at least one waypoint')

    trajectory = JointTrajectory(joint_names=JOINTS)
    previous_time = 0.0
    for seconds, positions in waypoints:
        if seconds <= previous_time:
            raise ValueError(f'waypoint times must increase, got {seconds} after {previous_time}')
        if len(positions) != len(JOINTS):
            raise ValueError(f'expected {len(JOINTS)} positions, got {positions}')
        for joint, position, (lower, upper) in zip(JOINTS, positions, LIMITS):
            if not lower <= position <= upper:
                raise ValueError(f'{joint} target {position} is outside [{lower}, {upper}]')

        trajectory.points.append(JointTrajectoryPoint(
            positions=[float(position) for position in positions],
            time_from_start=Duration(seconds=seconds).to_msg()))
        previous_time = seconds
    return trajectory


def main():
    trajectory = build_trajectory(WAYPOINTS)

    rclpy.init()
    node = Node('send_trajectory')
    publisher = node.create_publisher(JointTrajectory, 'set_joint_trajectory', 10)
    try:
        # A message published before the Gazebo bridge connects is silently lost
        for _ in range(100):
            if publisher.get_subscription_count() > 0:
                break
            rclpy.spin_once(node, timeout_sec=0.1)
        else:
            node.get_logger().error('Nothing subscribed to set_joint_trajectory. Is the sim running?')
            return 1

        publisher.publish(trajectory)
        # Exiting straight after publish can drop the message before it is delivered
        publisher.wait_for_all_acked(Duration(seconds=2.0))
        node.get_logger().info(f'Sent {len(trajectory.points)} waypoints')
        return 0
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    sys.exit(main())
