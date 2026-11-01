#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from std_srvs.srv import SetBool
from my_robot_interfaces.srv import SetTurnSpeed
from my_robot_interfaces.msg import RobotStatus
from geometry_msgs.msg import Twist
from lab_interfaces.msg import ObstacleInfo


class TurnAway(Node):

    def __init__(self):
        super().__init__('turn_away')
        self.declare_parameter('forward_speed', 0.2)
        self.declare_parameter('turn_speed', 0.5)
        self.declare_parameter('max_turn_speed', 1.5)
        self.enabled = True

        self.cmd_vel_pub = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        self.obstacle_sub = self.create_subscription(
            ObstacleInfo,
            '/obstacle',
            self.obstacle_callback,
            10
        )
        self.status_pub = self.create_publisher(
            RobotStatus,
            '/robot_status',
             10
        )

        self.enable_service = self.create_service(
            SetBool,
            '/turn_away_enable',
            self.enable_callback
        )

        self.turn_speed_service = self.create_service(
            SetTurnSpeed,
            '/set_turn_speed',
            self.set_turn_speed_callback
        )
        self.get_logger().info('turn_away node started')

    def obstacle_callback(self, msg):
        forward_speed = float(self.get_parameter(
        'forward_speed').value)

        turn_speed = float(self.get_parameter(
        'turn_speed').value)

        cmd = Twist()
        status = RobotStatus()
        if not self.enabled:

            status.state = "stopped"
            status.obstacle_distance = msg.distance

            self.status_pub.publish(status)

            return

        status.obstacle_distance = msg.distance

        # Drive forward when obstacle is not too close
        if not msg.too_close:
            cmd.linear.x = forward_speed
            cmd.angular.z = 0.0

            status.state = "forward"

        # Turn away from obstacle
        else:
            cmd.linear.x = 0.0

            status.state = "turning"

            if msg.angle > 0:
                # obstacle is left -> turn right
                cmd.angular.z = -turn_speed
            else:
                # obstacle is right -> turn left
                cmd.angular.z = turn_speed

        self.cmd_vel_pub.publish(cmd)
        self.status_pub.publish(status)

    def enable_callback(self, request, response):

        self.enabled = request.data

        if not self.enabled:

            cmd = Twist()
            self.cmd_vel_pub.publish(cmd)

        response.success = True

        if self.enabled:
            response.message = "turn_away enabled"
        else:
            response.message = "turn_away disabled"

        return response

    def set_turn_speed_callback(self, request, response):

        max_turn_speed = float(
         self.get_parameter('max_turn_speed').value
        )

        speed = request.turn_speed

        if speed <= 0.0:

            response.success = False
            response.message = "turn_speed must be greater than zero"

            return response

        if speed > max_turn_speed:

            response.success = False
            response.message = (
                f"turn_speed exceeds max_turn_speed ({max_turn_speed})"
            )

            return response

        self.set_parameters([
            rclpy.parameter.Parameter(
                'turn_speed',
                rclpy.Parameter.Type.DOUBLE,
                float(speed)
            )
        ])

        response.success = True
        response.message = f"turn_speed set to {speed}"

        return response

def main(args=None):
    rclpy.init(args=args)

    node = TurnAway()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()