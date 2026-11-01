from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.actions import DeclareLaunchArgument

from launch.substitutions import LaunchConfiguration

from launch.launch_description_sources import (
    PythonLaunchDescriptionSource
)

from launch_ros.actions import Node

from ament_index_python.packages import (
    get_package_share_directory
)

import os

def generate_launch_description():

    side_length = LaunchConfiguration(
        'side_length'
    )

    control_launch = os.path.join(
        get_package_share_directory(
            'diffdrive_bot'
        ),
        'launch',
        'control.launch.py'
    )

    return LaunchDescription([

        DeclareLaunchArgument(
            'side_length',
            default_value='0.5'
        ),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                control_launch
            )
        ),

        Node(
            package='my_robot_nodes',
            executable='rotate_server',
            output='screen'
        ),

        Node(
            package='my_robot_nodes',
            executable='square_driver',
            output='screen',
            parameters=[
                {
                    'side_length': side_length
                }
            ]
        )
    ])