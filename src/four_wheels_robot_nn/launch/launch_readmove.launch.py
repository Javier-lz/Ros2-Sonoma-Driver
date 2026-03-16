from launch import LaunchDescription
from launch_ros.actions import Node 

def generate_launch_description(): 
    return LaunchDescription([Node(
        package="four_wheels_robot_nn", 
        executable='datagathering',
        name='data_gathering_node',
        output='screen',
        parameters=[])

    ])