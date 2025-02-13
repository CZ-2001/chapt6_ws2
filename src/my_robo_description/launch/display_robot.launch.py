import launch
import launch_ros
import os
from ament_index_python.packages import get_package_share_directory
import launch_ros.parameter_descriptions

def generate_launch_description():
    # 获取默认的urdf路径
    urdf_pack_path = get_package_share_directory('my_robo_description')
    defa_urdf_path = os.path.join(urdf_pack_path, 'URDF', 'my_robo.urdf')
    defa_rviz2_config_path = os.path.join(urdf_pack_path, 'config', 'display_robot_model.rviz')
    #defa_rviz2_config_path = os.path.join(urdf_pack_path, 'config', 'display_robot_model.rviz')

    # 声明一个urdf参数，方便修改
    action_declare_arg_mode_path = launch.actions.DeclareLaunchArgument(
        name='model',
        default_value=defa_urdf_path,
        description='加载的模型文件路径'
    )
    #'cat ' 看清楚 cat 后面有个空格 空格在引号里面
   # 通过文件路径，获取内容，并转变成参数值对象，以供传入 robot_state_publisher
    model_path = launch.substitutions.LaunchConfiguration('model')
    sub_command_result = launch.substitutions.Command(['xacro ', model_path])
    rob_describle_value = launch_ros.parameter_descriptions.ParameterValue(sub_command_result, value_type=str)
    # 状态发布节点
    action_rob_state_pub = launch_ros.actions.Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': rob_describle_value}]# 相当于命令行后加 args=xx这种
    )

    # 关节状态发布节点
    action_joint_state_pub = launch_ros.actions.Node(
        package='joint_state_publisher',
        executable='joint_state_publisher'
    )

    # RViz2 节点
    action_rviz2_node = launch_ros.actions.Node(
        package='rviz2',
        executable='rviz2',
      arguments=['-d',defa_rviz2_config_path] #相当于在命令行后加东西  实现效果就是直接打开该文件 rviz2中
    )

   

    return launch.LaunchDescription([
        action_declare_arg_mode_path,
        action_rob_state_pub,
        action_joint_state_pub,
        action_rviz2_node
    ])
    
    
    
    
    
    
    
    
    