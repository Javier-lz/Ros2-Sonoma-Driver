from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import Command, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from launch.actions import ExecuteProcess 
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.actions import IncludeLaunchDescription


def generate_launch_description():
    keyboard_controller_node = Node(
        package='four_wheels_robot',
        executable='keyboard_control',
        name='keyboard_control',
        output='screen',

)
    return LaunchDescription([keyboard_controller_node])