#!/usr/bin/env python3
"""Report the distance to the nearest thing in front of the depth camera."""
import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import Float32

# Fraction of the image width/height (centred) that counts as "in front"
CENTRE_FRACTION = 0.2


def nearest_distance(depth, fraction=CENTRE_FRACTION):
    """Smallest valid depth (metres) in the centre window of a 2D depth array, or None."""
    rows, cols = depth.shape
    dr, dc = max(1, int(rows * fraction / 2)), max(1, int(cols * fraction / 2))
    window = depth[rows // 2 - dr:rows // 2 + dr, cols // 2 - dc:cols // 2 + dc]
    valid = window[np.isfinite(window) & (window > 0.0)]  # no-return pixels are inf or nan
    return float(valid.min()) if valid.size else None


class ObstacleDistance(Node):
    def __init__(self):
        super().__init__('obstacle_distance')
        self.publisher = self.create_publisher(Float32, 'obstacle_distance', 10)
        self.create_subscription(Image, 'camera/depth_image', self.on_depth, 10)

    def on_depth(self, msg):
        if msg.encoding != '32FC1':
            self.get_logger().error(f'Expected 32FC1 depth, got {msg.encoding}', once=True)
            return
        depth = np.frombuffer(msg.data, dtype=np.float32).reshape(msg.height, msg.width)
        distance = nearest_distance(depth)
        if distance is None:
            self.get_logger().info('Nothing in range', throttle_duration_sec=1.0)
            return
        self.publisher.publish(Float32(data=distance))
        self.get_logger().info(f'Obstacle {distance:.2f} m ahead', throttle_duration_sec=1.0)


def main():
    rclpy.init()
    node = ObstacleDistance()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
