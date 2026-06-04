
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='four_wheels_robot_nn',
            executable='controller_ai',
            name='ai_node',
            output='screen',
            parameters=[]),


            
    ])
