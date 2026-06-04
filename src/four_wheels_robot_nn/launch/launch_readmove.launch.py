from launch import LaunchDescription
from launch_ros.actions import Node 
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

def generate_launch_description(): 
    live_arg=DeclareLaunchArgument('live_save',default_value='0',description="A bool for the data to be saved directly or not by default NO")
    value=LaunchConfiguration('live_save')

    return LaunchDescription([
        live_arg,
        Node(
        package="four_wheels_robot_nn", 
        executable='datagathering',
        name='data_gathering_node',
        output='screen',
        parameters=[
        { 'live':value}
        ])

    ])