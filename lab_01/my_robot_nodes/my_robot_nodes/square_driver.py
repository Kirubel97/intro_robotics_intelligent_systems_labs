import math
import time

import threading
from rclpy.executors import MultiThreadedExecutor

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

from my_robot_interfaces.action import Rotate
from lab_interfaces.action import DriveDistance

class SquareDriver(Node):

    def __init__(self):

        super().__init__('square_driver')

        self.declare_parameter(
            'side_length',
            0.5
        )

        self.drive_client = ActionClient(
            self,
            DriveDistance,
            '/drive_distance'
        )

        self.rotate_client = ActionClient(
            self,
            Rotate,
            '/rotate'
        )

       
    def drive_side(self, length):

        goal = DriveDistance.Goal()
        goal.distance = length

        self.drive_client.wait_for_server()

        future = self.drive_client.send_goal_async(
            goal
        )

        rclpy.spin_until_future_complete(
            self,
            future
        )

        goal_handle = future.result()

        if not goal_handle.accepted:
            return False

        result_future = goal_handle.get_result_async()

        rclpy.spin_until_future_complete(
            self,
            result_future
        )

        result = result_future.result()

        return result.status == 4

    def rotate_corner(self):

        goal = Rotate.Goal()

        goal.angle = math.pi / 2.0

        self.rotate_client.wait_for_server()

        future = self.rotate_client.send_goal_async(
            goal
        )

        rclpy.spin_until_future_complete(
            self,
            future
        )

        goal_handle = future.result()

        if not goal_handle.accepted:
            return False

        result_future = goal_handle.get_result_async()

        rclpy.spin_until_future_complete(
            self,
            result_future
        )

        result = result_future.result()

        return result.status == 4

    def run_square(self):

        time.sleep(8.0)

        side_length = float(
        self.get_parameter(
            'side_length'
         ).value
        )

        side_length = float(
            self.get_parameter(
                'side_length'
            ).value
        )

        for side in range(1, 5):

            self.get_logger().info(
                f"Driving side {side}"
            )

            if not self.drive_side(side_length):

                self.get_logger().error(
                    f"Drive failed on side {side}"
                )

                return

            self.get_logger().info(
                f"Turning corner {side}"
            )

            if not self.rotate_corner():

                self.get_logger().error(
                    f"Rotate failed on side {side}"
                )

                return

        self.get_logger().info(
            "Square complete"
        )

def main(args=None):

    rclpy.init(args=args)

    node = SquareDriver()

    executor = MultiThreadedExecutor()

    executor.add_node(node)

    threading.Thread(
        target=node.run_square,
        daemon=True
    ).start()

    executor.spin()

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()