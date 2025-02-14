import launch
from launch.actions import TimerAction, ExecuteProcess, RegisterEventHandler
from launch.event_handlers import OnProcessExit
import launch.event_handlers
import launch.launch_description_sources
import launch_ros
import os
from ament_index_python.packages import get_package_share_directory
import launch_ros.parameter_descriptions

def generate_launch_description():
    # 获取功能包share路径
    urdf_pack_path = get_package_share_directory('my_robo_description')
    defa_xacro_path = os.path.join(urdf_pack_path, 'URDF', 'ano_robo.urdf.xacro')
    defa_gazebo_world_config_path = os.path.join(urdf_pack_path, 'world', 'custom_room.world')

    # 声明一个urdf参数，方便修改
    action_declare_arg_mode_path = launch.actions.DeclareLaunchArgument(
        name='model',
        default_value=str(defa_xacro_path),
        description='加载的模型文件路径'
    )

    # 通过文件路径，获取内容，并转变成参数值对象，以供传入 robot_state_publisher
    model_path = launch.substitutions.LaunchConfiguration('model')
    sub_command_result = launch.substitutions.Command(['xacro ', model_path])
    rob_describle_value = launch_ros.parameter_descriptions.ParameterValue(sub_command_result, value_type=str)

    # 状态发布节点
    action_rob_state_pub = launch_ros.actions.Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': rob_describle_value}]
    )

    # 启动 Gazebo
    action_launch_gazebo = launch.actions.IncludeLaunchDescription(
        launch.launch_description_sources.PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('gazebo_ros'), 'launch', 'gazebo.launch.py')
        ),
        launch_arguments=[('world', defa_gazebo_world_config_path), ('verbose', 'true')]
    )

    # 加载机器人
    spawn_robot_node = launch_ros.actions.Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-topic', '/robot_description', '-entity', 'ano_robo']
    )

    # 使用 TimerAction 延迟加载机器人
    action_launch_robo = TimerAction(
        period=1.0,  # 延迟1秒
        actions=[spawn_robot_node]
    )

    # 加载控制器
    load_joint_state_controller = launch.actions.ExecuteProcess(
        cmd=['ros2', 'control', 'load_controller', '--set-state', 'active', 'my_robot_state_broadcaster'],
        output='screen'
    )
    load_joint_effort_controller = launch.actions.ExecuteProcess(
        cmd=['ros2', 'control', 'load_controller', '--set-state', 'active', 'my_robot_effort_broadcaster'],
        output='screen'
    )
    load_joint_diff_drive_controller = launch.actions.ExecuteProcess(
        cmd=['ros2', 'control', 'load_controller', '--set-state', 'active', 'my_robot_diff_drive_controller'],
        output='screen'
    )

    action_load_joint = launch.actions.RegisterEventHandler(
        event_handler=launch.event_handlers.OnProcessExit(
            target_action=spawn_robot_node,  # 直接使用 spawn_robot_node 作为 target_action
            on_exit=[load_joint_state_controller],
        )
    )
    action_load_effort = launch.actions.RegisterEventHandler(
        event_handler=launch.event_handlers.OnProcessExit(
            target_action=load_joint_state_controller,  # 直接使用 spawn_robot_node 作为 target_action
            on_exit=[load_joint_diff_drive_controller],  # 6.5.5里面才为load_joint_diff_drive_controller
        )
    )

    # 返回 LaunchDescription
    return launch.LaunchDescription([
        action_declare_arg_mode_path,
        action_rob_state_pub,
        action_launch_gazebo,
        action_launch_robo,
        action_load_joint,
        action_load_effort
    ])