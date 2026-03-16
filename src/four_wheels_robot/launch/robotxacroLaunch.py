from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import Command, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from launch.actions import ExecuteProcess 
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.actions import IncludeLaunchDescription

def generate_launch_description():
    robot_xacro=PathJoinSubstitution([
            FindPackageShare('four_wheels_robot'),
            'urdf',
            'robot.xacro'
        ])
    robot_description = Command([
        'xacro ',
        robot_xacro
    ])

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description
        }]
)
    rviz_config= Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', PathJoinSubstitution([
            FindPackageShare('four_wheels_robot'),'config','baseRvizConfig.rviz'])]

    )
    velocity_publisher=Node(package='four_wheels_robot', executable='velocity_publisher', output='screen')

    ros_bridge_gz_velocity=Node(package='ros_gz_bridge',
                                executable= 'parameter_bridge',
                                name='ros_bridge_gz_velocity',
                                arguments=['/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist'],
                                   
                                output='screen')

    gz_bridge_front_camera=Node(package='ros_gz_bridge',
                                executable= 'parameter_bridge',
                                name='gz_bridge_front_camera',
                                arguments=['/front_camera@sensor_msgs/msg/Image@gz.msgs.Image'],
                                
                                output='screen')

    
    gz_bridge_car_odometry = Node(
    package='ros_gz_bridge',
    executable='parameter_bridge',
    name='gz_bridge_odometry',
    # Using the '[' character forces Gazebo -> ROS 2 direction
    arguments=[
        '/model/prius_hybrid/odometry@nav_msgs/msg/Odometry[gz.msgs.Odometry'
    ],
    remappings=[('/model/prius_hybrid/odometry','/odometry')],
    output='screen'
)
    gz_launch=IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('ros_gz_sim'),
                'launch',
                'gz_sim.launch.py'
            ])
        ]),launch_arguments={'gz_args': PathJoinSubstitution([
            FindPackageShare('four_wheels_robot'),
            #'-s',
            'worlds',
            'sonoma.sdf'
        ])}.items())
    



    return LaunchDescription([
        gz_launch ,
    

        gz_bridge_car_odometry,
      
      
        ros_bridge_gz_velocity,
        gz_bridge_front_camera,
   
        

        
    ])
