from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import Command, PathJoinSubstitution, LaunchConfiguration
from launch_ros.substitutions import FindPackageShare
from launch.actions import ExecuteProcess, AppendEnvironmentVariable, DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction
from launch.launch_description_sources import PythonLaunchDescriptionSource

def launch_setup(context, *args, **kwargs):
    # This dictionary maps our string numbers to actual track names
    names_tracks = {'0': 'sonoma', '1': 'grass_track', '2': 'sand_track', '3': 'snow_track', '4': 'dirt_track'}
    
    # 1. Resolve the LaunchConfiguration into a raw Python string at runtime
    selected_key = LaunchConfiguration('world_name').perform(context)
    
    # Fallback to 'sonoma' if an unexpected integer is passed
    track_name = names_tracks.get(selected_key, 'sonoma')
    
    pkg_share = FindPackageShare('four_wheels_robot')
    models_path = PathJoinSubstitution([pkg_share, 'models'])
    
    # 2. Build the world file path safely using the resolved track name string
    world_file = PathJoinSubstitution([pkg_share, 'worlds', f"{track_name}.sdf"])
    
    # 3. Setup Robot Xacro and Descriptions
    robot_xacro = PathJoinSubstitution([pkg_share, 'urdf', 'robot.xacro'])
    robot_description = Command(['xacro ', robot_xacro])

    ros_bridge_gz_velocity = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='ros_bridge_gz_velocity',
        arguments=['/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist'],
        output='screen'
    )

    gz_bridge_front_camera = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='gz_bridge_front_camera',
        arguments=['/front_camera@sensor_msgs/msg/Image@gz.msgs.Image'],
        output='screen'
    )
    
    gz_bridge_car_odometry = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='gz_bridge_odometry',
        arguments=['/model/prius_hybrid/odometry@nav_msgs/msg/Odometry[gz.msgs.Odometry'],
        remappings=[('/model/prius_hybrid/odometry', '/odometry')],
        output='screen'
    )
    
    # 5. Setup Gazebo Sim Launch Include
    gz_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([FindPackageShare('ros_gz_sim'), 'launch', 'gz_sim.launch.py'])
        ]),
        launch_arguments={'gz_args': ['-r ', world_file]}.items()
    )
    
    # Return all the nodes and actions to execute
    return [
        AppendEnvironmentVariable(name='GZ_SIM_RESOURCE_PATH', value=models_path),
        gz_launch,
     


        gz_bridge_car_odometry,
        ros_bridge_gz_velocity,
        gz_bridge_front_camera
    ]


def generate_launch_description():
    # Declare the argument outside so the CLI can see it immediately
    world_name_arg = DeclareLaunchArgument(
        'world_name',
        default_value='0',
        description='The numerical ID of the loaded world (0=sonoma, 1=grass, etc.)'
    )

    return LaunchDescription([
        world_name_arg,
        # OpaqueFunction calls our layout function and passes the runtime context
        OpaqueFunction(function=launch_setup)
    ])