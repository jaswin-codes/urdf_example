import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

from launch.conditions import IfCondition, UnlessCondition
from launch_ros.actions import Node


# Ported from Gazebo Classic (gazebo_ros) to the new Gazebo (ros_gz_sim), following video #10.
def generate_launch_description():

    # Specify the name of the package and path to xacro file within the package
    pkg_name = 'urdf_example'
    pkg_share = get_package_share_directory(pkg_name)
    # The world is now passed in explicitly (it used to be passed down by gazebo_ros)
    world = LaunchConfiguration('world')
    world_arg = DeclareLaunchArgument(
        'world',
        default_value=os.path.join(pkg_share, 'worlds', 'empty.sdf'),
        description='World file to load')


    # Reuse rsp.launch.py instead of repeating the robot_state_publisher setup here
    rsp = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_share, 'launch', 'rsp.launch.py')),
        launch_arguments={'use_sim_time': 'true'}.items()
    )


    # headless:=true runs only the Gazebo server (no window, off-screen rendering for the cameras)
    headless = LaunchConfiguration('headless')
    headless_arg = DeclareLaunchArgument(
        'headless', default_value='false',
        description='Run Gazebo without the GUI')


    # gazebo_ros/gazebo.launch.py  ->  ros_gz_sim/gz_sim.launch.py
    # -r runs the simulation straight away, -v4 prints extra debug info
    gz_sim_launch = PythonLaunchDescriptionSource([os.path.join(
        get_package_share_directory('ros_gz_sim'), 'launch'), '/gz_sim.launch.py'])
    gazebo = IncludeLaunchDescription(
        gz_sim_launch,
        launch_arguments={'gz_args': ['-r -v4 ', world],
                          'on_exit_shutdown': 'true'}.items(),
        condition=UnlessCondition(headless))
    gazebo_headless = IncludeLaunchDescription(
        gz_sim_launch,
        launch_arguments={'gz_args': ['-r -s --headless-rendering -v4 ', world],
                          'on_exit_shutdown': 'true'}.items(),
        condition=IfCondition(headless))


    # gazebo_ros spawn_entity.py  ->  ros_gz_sim create  (-entity became -name)
    spawn_entity = Node(package='ros_gz_sim', executable='create',
                    arguments=['-topic', 'robot_description',
                                '-name', 'my_bot'],
                    output='screen')


    # Copy Gazebo topics <-> ROS topics (clock, joint states, trajectory commands, camera)
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[{'config_file': os.path.join(pkg_share, 'config', 'gz_bridge.yaml'),
                     'use_sim_time': True}],
        output='screen'
    )

    # Images get their own bridge so they can use image_transport
    image_bridge = Node(
        package='ros_gz_image',
        executable='image_bridge',
        arguments=['camera/image', 'camera/depth_image'],
        parameters=[{'use_sim_time': True}],
        output='screen'
    )




    # Run the node
    return LaunchDescription([
        world_arg,
        headless_arg,
        gazebo,
        gazebo_headless,
        rsp,
        spawn_entity,
        bridge,
        image_bridge
    ])
