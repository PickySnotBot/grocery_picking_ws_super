from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    # Get the package directory
    pkg_dir = get_package_share_directory('localization')
    config_file = os.path.join(pkg_dir, 'config', 'snot_ekf_config.yaml')

    return LaunchDescription([
        Node(
            package='robot_localization',
            executable='ekf_node',
            name='ekf_filter_node_odom',
            output='screen',
            parameters=[config_file]
        )
    ])
