import launch
from launch.actions import TimerAction
import launch.launch_description_sources
import launch_ros
import os
from ament_index_python.packages import get_package_share_directory
import launch_ros.parameter_descriptions
def generate_launch_description():
    # 获取功能包share路径
    urdf_pack_path = get_package_share_directory('my_robo_description')
    defa_xacro_path = os.path.join(urdf_pack_path, 'URDF', 'ano_robo.urdf.xacro')
    #defa_xacro_path=urdf_pack_path+'URDF/ano_robo.urdf.xacro'
    #defa_rviz2_config_path = os.path.join(urdf_pack_path, 'config', 'display_robot_model.rviz')
    defa_gazebo_world_config_path = os.path.join(urdf_pack_path, 'world', 'custom_room.world')

    # 声明一个urdf参数，方便修改
    action_declare_arg_mode_path = launch.actions.DeclareLaunchArgument(
        name='model',
        default_value=str(defa_xacro_path),
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

   # action_launch_gazebo=launch.actions.IncludeLaunchDescription(
  #      launch.launch_description_sources.PythonLaunchDescriptionSource([
  #          get_package_share_directory('gazebo_ros'),'/launch','/gazebo.launch.py'
  #      ]),launch_arguments=[('world',defa_gazebo_world_config_path),('verbose','true')]
  #  ) 
    action_launch_gazebo = launch.actions.IncludeLaunchDescription(
    launch.launch_description_sources.PythonLaunchDescriptionSource(
        os.path.join(get_package_share_directory('gazebo_ros'), 'launch', 'gazebo.launch.py')
    ),
    launch_arguments=[('world', defa_gazebo_world_config_path), ('verbose', 'true')]
    )   


 #加载机器人
    action_launch_robo = TimerAction(
    period=10.0,  # 延迟 5 秒
    actions=[
        launch_ros.actions.Node(
            package='gazebo_ros',
            executable='spawn_entity.py',
            arguments=['-topic', '/robot_description', '-entity', 'ano_robo']
        )
    ]
    )


   
 #   action_launch_robo=launch_ros.actions.Node(
 #       package='gazebo_ros',
  #      executable='spawn_entity.py',
  #      arguments=['-topic', '/robot_description', '-entity', 'ano_robo']
  #  )
#
   

    return launch.LaunchDescription([
        action_declare_arg_mode_path,
        action_rob_state_pub,
        action_launch_gazebo,
        action_launch_robo
        
    ])
    
    
    
    
    
    
    
    
    