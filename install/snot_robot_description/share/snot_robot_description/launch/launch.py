import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, LogInfo, TimerAction
from launch.conditions import IfCondition
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    # Get the package directory
    bringup_dir = get_package_share_directory('snot_robot_description')
    urdf_file = os.path.join(bringup_dir, 'urdf', 'snot_bot_urdf.urdf')

    # Verify if the URDF file exists
    if not os.path.exists(urdf_file):
        raise FileNotFoundError(f"URDF file not found: {urdf_file}")

    # Launch configuration variables
    use_robot_state_pub = LaunchConfiguration('use_robot_state_pub')
    use_joint_state_pub = LaunchConfiguration('use_joint_state_pub')

    declare_use_robot_state_pub_cmd = DeclareLaunchArgument(
        'use_robot_state_pub',
        default_value='True',
        description='Whether to start the robot state publisher')

    declare_use_joint_state_pub_cmd = DeclareLaunchArgument(
        'use_joint_state_pub',
        default_value='True',
        description='Whether to start the joint state publisher')

    declare_urdf_cmd = DeclareLaunchArgument(
        'urdf_file',
        default_value=urdf_file,
        description='Full path to the URDF file')

    with open(urdf_file, 'r') as infp:
        robot_desc = infp.read()

    robot_description_param = {'robot_description': robot_desc}

    # Start the robot_state_publisher node with a small delay to ensure it's ready before joint_state_publisher
    start_robot_state_publisher_cmd = TimerAction(
        period=2.0,  # Delay in seconds
        actions=[Node(
            condition=IfCondition(use_robot_state_pub),
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[robot_description_param]
        )]
    )

    # Start the joint_state_publisher node with the URDF path as an argument
    start_joint_state_publisher_cmd = Node(
        condition=IfCondition(use_joint_state_pub),
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        output='screen',
        arguments=[urdf_file]  # Ensure the URDF file path is passed here
    )

    # Log URDF file path and content
    log_urdf_path = LogInfo(msg=f'URDF file path: {urdf_file}')
    log_urdf_content = LogInfo(msg=f'URDF content: {robot_desc[:500]}...')

    # Create the launch description and populate
    ld = LaunchDescription()

    # Declare the launch options
    ld.add_action(declare_use_robot_state_pub_cmd)
    ld.add_action(declare_use_joint_state_pub_cmd)
    ld.add_action(declare_urdf_cmd)

    # Add logging actions
    ld.add_action(log_urdf_path)
    ld.add_action(log_urdf_content)

    # Add any conditioned actions
    ld.add_action(start_robot_state_publisher_cmd)
    ld.add_action(start_joint_state_publisher_cmd)

    return ld
