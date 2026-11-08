# URDF Example

> My learning fork of [joshnewans/urdf_example](https://github.com/joshnewans/urdf_example). The `jazzy-new-gazebo` branch ports the simulation from Gazebo Classic to Gazebo Harmonic on ROS 2 Jazzy. The robot and the original tutorial are by Josh Newans.


This repo contains an example of a URDF file and a launch script to run it. (ROS 2)
This is part of a tutorial on creating URDF files, available at the links below:

YouTube:
[![See video for example](https://img.youtube.com/vi/CwdbsvcpOHM/0.jpg)](https://youtu.be/CwdbsvcpOHM)

Blog Post:
[https://articulatedrobotics.xyz/ready-for-ros-7-urdf/](https://articulatedrobotics.xyz/ready-for-ros-7-urdf/)



## Run the Gazebo simulation

Needs ROS 2 Jazzy and the Gazebo bridge packages (`sudo apt install ros-jazzy-ros-gz`).

```bash
cd ~/ros2_ws/src
git clone https://github.com/jaswin-codes/urdf_example.git
cd ~/ros2_ws
colcon build --packages-select urdf_example
source install/setup.bash
ros2 launch urdf_example rsp_sim.launch.py
```

In a second terminal (after `source install/setup.bash`), move the joints. The slider range is 0 to 2 m and the arm range is 0 to pi/2 rad.

```bash
ros2 topic pub -1 /set_joint_trajectory trajectory_msgs/msg/JointTrajectory '{joint_names: [slider_joint, arm_joint], points: [{positions: [0.8, 0.6]}]}'
```

To see the robot and camera in RViz:

```bash
rviz2 -d $(ros2 pkg prefix urdf_example)/share/urdf_example/view_with_camera.rviz
```

| ROS topic | Type | Direction |
|---|---|---|
| `/clock` | `rosgraph_msgs/msg/Clock` | Gazebo to ROS |
| `/joint_states` | `sensor_msgs/msg/JointState` | Gazebo to ROS |
| `/set_joint_trajectory` | `trajectory_msgs/msg/JointTrajectory` | ROS to Gazebo |
| `/camera/image` | `sensor_msgs/msg/Image` | Gazebo to ROS |
| `/camera/depth_image` | `sensor_msgs/msg/Image` | Gazebo to ROS |
| `/camera/points` | `sensor_msgs/msg/PointCloud2` | Gazebo to ROS |
| `/camera/camera_info` | `sensor_msgs/msg/CameraInfo` | Gazebo to ROS |

## View the robot in RViz only (no simulation)


1. Build the package with colcon.
2. Launch the `robot_state_publisher` launch file with `ros2 launch urdf_example rsp.launch.py`.
3. Launch `joint_state_publisher_gui` with `ros2 run joint_state_publisher_gui joint_state_publisher_gui`. You may need to install it if you don't have it already.
4. Launch RViz with `rviz2`

To replicate the RViz display shown in the video you will want to
- Set your fixed frame to `world`
- Add a `RobotModel` display, with the topic set to `/robot_description`, and alpha set to 0.8
- Add a `TF` display with names enabled.