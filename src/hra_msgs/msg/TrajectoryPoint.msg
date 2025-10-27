# TrajectoryPoint.msg
# 包含一个时间点的完整6-DOF期望状态

# 轨迹的相对时间戳 (从0开始)
duration time_from_start

# 期望位姿 (位置 + 姿态)
geometry_msgs/Pose pose

# 期望速度 (线速度 + 角速度)
geometry_msgs/Twist velocity

# 期望加速度 (线加速度 + 角加速度)
geometry_msgs/Accel acceleration