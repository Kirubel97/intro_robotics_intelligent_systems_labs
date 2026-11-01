import math
import time

import rclpy

from rclpy.node import Node
from rclpy.action import ActionServer
from rclpy.executors import MultiThreadedExecutor

from nav_msgs.msg import Odometry
from geometry_msgs.msg import Twist

from my_robot_interfaces.action import Rotate

def yaw_from_quaternion(q):
    """Rotation about the vertical axis, in rad, of an orientation quaternion."""
    return math.atan2(2.0 * (q.w * q.z + q.x * q.y), 1.0 - 2.0 * (q.y * q.y + q.z * q.z))

def angle_difference(target, current):
    """target - current, wrapped to [-pi, pi] so the robot turns the short way."""
    return math.atan2(math.sin(target - current), math.cos(target - current))


class RotateServer(Node):

    def __init__(self):

        super().__init__('rotate_server')

        self.declare_parameter(
            'turn_speed',
            0.5
        )

        self.current_yaw = 0.0
        self.last_yaw = None

        self.cmd_pub = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        self.odom_sub = self.create_subscription(
            Odometry,
            '/odom',
            self.odom_callback,
            10
        )

        self.action_server = ActionServer(
            self,
            Rotate,
            '/rotate',
            self.execute_callback
        )

    def odom_callback(self, msg):

        self.current_yaw = yaw_from_quaternion(
         msg.pose.pose.orientation
        )

    def execute_callback(self, goal_handle):

        goal = goal_handle.request.angle

        result = Rotate.Result()

        if goal == 0.0:

            goal_handle.abort()

            result.turned = 0.0

            return result

        turn_speed = float(
            self.get_parameter(
                'turn_speed'
            ).value
         )

        direction = 1.0

        if goal < 0:
            direction = -1.0

        cmd = Twist()
        cmd.angular.z = direction * turn_speed

        turned = 0.0

        self.last_yaw = self.current_yaw

        feedback = Rotate.Feedback()

        while abs(turned) < abs(goal):

            if goal_handle.is_cancel_requested:

                stop = Twist()
                self.cmd_pub.publish(stop)

                goal_handle.canceled()

                result.turned = turned

                return result

            self.cmd_pub.publish(cmd)

            delta = angle_difference(
                self.current_yaw,
                self.last_yaw
            )

            turned += delta

            self.last_yaw = self.current_yaw

            feedback.turned = turned

            goal_handle.publish_feedback(
                feedback
            )

            time.sleep(0.05)

        stop = Twist()

        self.cmd_pub.publish(stop)

        result.turned = turned

        goal_handle.succeed()

        return result

def main(args=None):

    rclpy.init(args=args)

    node = RotateServer()

    executor = MultiThreadedExecutor()

    executor.add_node(node)

    executor.spin()

    rclpy.shutdown()
if __name__ == '__main__':
    main()