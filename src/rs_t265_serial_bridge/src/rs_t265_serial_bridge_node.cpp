/**
 * rs_t265_serial_bridge_node.cpp
 *
 * 功能：
 *   1. 订阅 T265 的 Odometry (/camera/odom/sample) 和 IMU (/camera/imu) 数据
 *   2. 使用 TF2 将各数据从相机坐标系转换到机器人底盘坐标系 (base_link)
 *   3. 提取位置、线速度、线加速度、欧拉角 (弧度)、角速度、角加速度
 *   4. 按 STM32 协议帧格式打包 (帧头、36×int16、校验、帧尾) 并通过串口发送
 *
 * 修改说明：
 *   - 新增订阅 /desired_state_topic，接收期望轨迹点。
 *   - 修改 timerCallback，将接收到的期望值打包进串口帧。
 *   - 增加安全机制：若长时间未收到期望值，则自动切换为悬停指令。
 *
 * 依赖：
 *   roscpp, nav_msgs, sensor_msgs, serial,
 *   tf2, tf2_ros, tf2_geometry_msgs
 *
 * 作者：孙浩然
 * 日期：2025-04-18
 */

#include <ros/ros.h>           // ROS基本头文件，提供ROS相关函数
#include <serial/serial.h>     // 提供串口通信功能
#include <nav_msgs/Odometry.h> // ROS里程计数据消息类型（位姿与速度）
#include <nav_msgs/Path.h>     // ROS路径消息类型
#include <std_msgs/Float64.h>  // ROS标准浮点数消息类型
#include <sensor_msgs/Imu.h>   // ROS IMU数据消息类型（加速度与角速度）

#include <tf2_ros/transform_listener.h>          // TF2 监听器，用于接收和缓存变换
#include <tf2_ros/buffer.h>                      // TF2 Buffer，用于存储和查询变换
#include <tf2_geometry_msgs/tf2_geometry_msgs.h> // tf2 与 geometry_msgs 的桥接
#include <tf2_sensor_msgs/tf2_sensor_msgs.h>
#include <tf2_kdl/tf2_kdl.h>          // tf2_kdl: KDL::Twist support
#include <tf2/convert.h>              // 让 fromMsg / toMsg / doTransform 模板可见
#include <tf2/LinearMath/Matrix3x3.h> // tf2 矩阵运算
#include <kdl/frames.hpp>             // KDL::Twist, Frames

#include <geometry_msgs/PoseStamped.h>    // for PoseStamped
#include <geometry_msgs/TwistStamped.h>   // for TwistStamped
#include <geometry_msgs/Vector3Stamped.h> // for Vector3Stamped
#include <geometry_msgs/PoseStamped.h>    // for PoseStamped

#include <Eigen/Core>    // Eigen核心头文件，提供矩阵和向量操作
#include <Eigen/Dense>   // Eigen稠密矩阵头文件，提供线性代数运算
#include <vector>        // 动态数组类型，便于数据打包发送
#include <mutex>         // 提供互斥锁，确保多线程安全性
#include <algorithm>     // std::max, std::min
#include <cmath>         // M_PI
#include <deque>         // 用于缓存 IMU 消息
#include <array>         // 用于存储固定大小的数组

#include "hra_msgs/TrajectoryPoint.h"   //轨迹生成器消息类型

// ===========================
// ------ 全局变量及常量 ------
// ===========================
#define CRC_DEBUG_ENABLED 0 // 设置为1启用CRC调试信息，设置为0关闭

// 串口对象
serial::Serial ser;

// TF2 相关
tf2_ros::Buffer *tf_buffer_ptr;              // TF buffer
tf2_ros::TransformListener *tf_listener_ptr; // TF listener (raw pointer)

// 话题参数
std::string odom_topic;
std::string imu_topic;

// 机器人坐标系 & 偏置
std::string base_link;
std::string odom;
std::string pose;
double offset_x_, offset_y_, offset_z_;

// 全局缓存声明
std::deque<sensor_msgs::Imu> imu_buffer;    // IMU 消息缓存
std::deque<nav_msgs::Odometry> odom_buffer; // Odom 消息缓存
std::mutex data_mutex;

// 最大缓存时长：0.1s，可根据系统延迟调整
const ros::Duration MAX_BUFFER_DURATION(0.1);

// 缓存最新消息
nav_msgs::Odometry latest_odom; // 最新 Odometry
sensor_msgs::Imu latest_imu;    // 最新 IMU

// 期望状态缓存
hra_msgs::TrajectoryPoint latest_desired_state;
std::mutex desired_state_mutex;
bool desired_state_received = false;
ros::Time last_desired_state_time;

// 可视化相关的全局变量
ros::Publisher actual_path_pub;
nav_msgs::Path actual_path_msg; // 用于累积实际路径

// rqt_plot 发布器
// 位置
ros::Publisher plot_pos_x_des_pub, plot_pos_x_act_pub;
ros::Publisher plot_pos_y_des_pub, plot_pos_y_act_pub;
ros::Publisher plot_pos_z_des_pub, plot_pos_z_act_pub;
ros::Publisher plot_vel_x_des_pub, plot_vel_x_act_pub;
ros::Publisher plot_vel_y_des_pub, plot_vel_y_act_pub;
ros::Publisher plot_vel_z_des_pub, plot_vel_z_act_pub;
ros::Publisher plot_acc_x_des_pub, plot_acc_x_act_pub;
ros::Publisher plot_acc_y_des_pub, plot_acc_y_act_pub;
ros::Publisher plot_acc_z_des_pub, plot_acc_z_act_pub;
// 姿态
ros::Publisher plot_ang_x_des_pub, plot_ang_x_act_pub;
ros::Publisher plot_ang_y_des_pub, plot_ang_y_act_pub;
ros::Publisher plot_ang_z_des_pub, plot_ang_z_act_pub;
ros::Publisher plot_ang_vel_x_des_pub, plot_ang_vel_x_act_pub;
ros::Publisher plot_ang_vel_y_des_pub, plot_ang_vel_y_act_pub;
ros::Publisher plot_ang_vel_z_des_pub, plot_ang_vel_z_act_pub;
ros::Publisher plot_ang_acc_x_des_pub, plot_ang_acc_x_act_pub;
ros::Publisher plot_ang_acc_y_des_pub, plot_ang_acc_y_act_pub;
ros::Publisher plot_ang_acc_z_des_pub, plot_ang_acc_z_act_pub;

    // 角加速度计算变量
    static const int ACC_WINDOW_SIZE = 5; // 角加速度滑动平均窗口
std::deque<std::array<float, 3>> ang_acc_buffer;
std::array<float, 3> prev_ang_vel = {0.0f, 0.0f, 0.0f}; // 保存上次角速度与时间，用于差分计算
ros::Time prev_imu_time;

// 串口数据帧参数
static uint32_t g_seq = 1; // 帧序号（从 1 开始）

// =============================================================
// @brief 串口数据帧协议：帧头、帧序号、时间戳、数据帧、校验和、帧尾
// 0  1   2..5     6..13          14..85           86..87  88 89
// ┌──┬──┬────────┬──────────────┬────────────────┬──────┬──┬──┐
// │AA│BB│sequence│ unix_time_ns │  72 B payload  │CRC16 │CC│DD│
// └──┴──┴────────┴──────────────┴────────────────┴──────┴──┴──┘
//           ↑Big-endian↑
// =============================================================

// 上位机CRC计算函数，与下位机完全一致
uint16_t calculate_crc16_be(const uint8_t *data, uint16_t length)
{
  uint16_t crc = 0;
  const uint8_t *p = data;
  uint16_t n = length;

  while (n >= 2)
  {
    crc += (static_cast<uint16_t>(*p++) << 8) | static_cast<uint16_t>(*p++);
    n -= 2;
  }

  return crc;
}

// ===============================================
// @brief 接收T265发布的Odometry消息回调函数
// @param msg const 指针，指向接收到的位姿与速度数据
// ===============================================

void odomCallback(const nav_msgs::Odometry::ConstPtr &msg)
{
  std::lock_guard<std::mutex> lk(data_mutex);
  latest_odom = *msg; // 复制最新的数据到全局变量

  // 缓存最新 Odom
  odom_buffer.push_back(*msg);
  // 丢弃过期 Odom
  while (!odom_buffer.empty() &&
         (msg->header.stamp - odom_buffer.front().header.stamp) > MAX_BUFFER_DURATION)
  {
    odom_buffer.pop_front();
  }
}

// =====================================================
// @brief 接收T265发布的IMU消息回调函数
// @param msg const 指针，指向接收到的线加速度与角速度数据
// =====================================================

void imuCallback(const sensor_msgs::Imu::ConstPtr &msg)
{
  std::lock_guard<std::mutex> lk(data_mutex);
  latest_imu = *msg; // 复制最新的数据到全局变量（整个 Imu 消息，包括 angular_velocity、linear_acceleration）

  // 若首次接收，则初始化 prev_imu_time
  if (prev_imu_time.isZero())
  {
    prev_imu_time = msg->header.stamp;
  }

  // 缓存最新 IMU
  imu_buffer.push_back(*msg);
  // 丢弃过期 IMU
  while (!imu_buffer.empty() &&
         (msg->header.stamp - imu_buffer.front().header.stamp) > MAX_BUFFER_DURATION)
  {
    imu_buffer.pop_front();
  }
}

// ============================================================
// @brief 接收期望轨迹点消息回调函数
// @param msg const 指针，指向接收到的期望轨迹点数据
// ============================================================
void desiredStateCallback(const hra_msgs::TrajectoryPoint::ConstPtr &msg)
{
  std::lock_guard<std::mutex> lock(desired_state_mutex);
  latest_desired_state = *msg;
  desired_state_received = true;
  last_desired_state_time = ros::Time::now();
}

// ==================================================================
// @brief 定时器回调函数，按照固定频率触发（可按需设定，这里为100Hz），
//        1. 从缓存复制 Odometry 与 IMU
//        2. 使用 TF2 将 Odometry、IMU 数据从相机系转换到 base_link
//        3. 提取并计算：位置、线速度、线加速度、欧拉角、角速度、角加速度
//        4. 打包并通过串口发送
// @param event 定时器事件信息（未使用）
// ==================================================================

void timerCallback(const ros::TimerEvent &)
{
  // —— 1. 复制缓存数据 、对齐时间戳、检查空frame ——
  // 先一次性读取系统当前时刻，后面两段选最近消息都用同一个基准
  const ros::Time t_ref = ros::Time::now();

  nav_msgs::Odometry odom_msg;
  sensor_msgs::Imu imu_msg;
  {
    std::lock_guard<std::mutex> lk(data_mutex);
    // —— 1) 从 odom_buffer 里找出与当前时刻差值绝对值最小的一条 ——
    if (!odom_buffer.empty())
    {
      auto best_it = odom_buffer.begin();
      // 计算初始 best_diff（手动取绝对值）
      ros::Duration best_diff = (best_it->header.stamp >= t_ref)
                                    ? (best_it->header.stamp - t_ref)
                                    : (t_ref - best_it->header.stamp);
      for (auto it = odom_buffer.begin(); it != odom_buffer.end(); ++it)
      {
        ros::Duration diff = (it->header.stamp >= t_ref)
                                 ? (it->header.stamp - t_ref)
                                 : (t_ref - it->header.stamp);
        if (diff < best_diff)
        {
          best_diff = diff;
          best_it = it;
        }
      }
      odom_msg = *best_it;
    }
    else
    {
      odom_msg = latest_odom; // buffer 为空时回退
    }

    // —— 2) 同理，从 imu_buffer 里选最贴近当前时刻的一条 ——
    if (!imu_buffer.empty())
    {
      auto best_it = imu_buffer.begin();
      ros::Duration best_diff = (best_it->header.stamp >= t_ref)
                                    ? (best_it->header.stamp - t_ref)
                                    : (t_ref - best_it->header.stamp);
      for (auto it = imu_buffer.begin(); it != imu_buffer.end(); ++it)
      {
        ros::Duration diff = (it->header.stamp >= t_ref)
                                 ? (it->header.stamp - t_ref)
                                 : (t_ref - it->header.stamp);
        if (diff < best_diff)
        {
          best_diff = diff;
          best_it = it;
        }
      }
      imu_msg = *best_it;
    }
    else
    {
      imu_msg = latest_imu;
    }
  }

  // 只有收到有效的frame_id后才做变换
  if (odom_msg.header.frame_id.empty() || imu_msg.header.frame_id.empty())
  {
    ROS_WARN_THROTTLE(5, "Waiting for valid Odometry/IMU data (frame_id empty)...");
    return;
  }

  // 2. Pose（位置+姿态）：获取base_link在世界坐标系下位姿
  // 获取位姿
  geometry_msgs::TransformStamped tf_odom_base;
  try
  {
    tf_odom_base = tf_buffer_ptr->lookupTransform(
        odom,      // 目标 (world)
        base_link, // 源   (robot)
        odom_msg.header.stamp,
        ros::Duration(0.01));
  }
  catch (const tf2::TransformException &ex)
  {
    ROS_WARN_STREAM_THROTTLE(1.0, "TF lookup odom→base failed: " << ex.what());
    return;
  }

  // 2.1 用 Eigen 取出世界系下位置 & 四元数
  Eigen::Vector3d pos_world(
      tf_odom_base.transform.translation.x,
      tf_odom_base.transform.translation.y,
      tf_odom_base.transform.translation.z);

  tf2::Quaternion q_base;
  tf2::fromMsg(tf_odom_base.transform.rotation, q_base);
  double qw = q_base.w(), qx = q_base.x(),
         qy = q_base.y(), qz = q_base.z();
  Eigen::Quaterniond quat_world(qw, qx, qy, qz);

  // 2.2 静态安装偏置补偿
  // offset_..._ 在类里通过参数 (不同构型) 已经读入
  Eigen::Vector3d offset_body;
  offset_body = Eigen::Vector3d(offset_x_, offset_y_, offset_z_);

  // 世界系下，偏置在机体系下 rotated 到世界系
  Eigen::Vector3d offset_world = quat_world * offset_body;
  Eigen::Vector3d pos_base_world = pos_world + offset_world;

  // 把补偿后的位置写回 tf_odom_base
  tf_odom_base.transform.translation.x = static_cast<float>(pos_base_world.x());
  tf_odom_base.transform.translation.y = static_cast<float>(pos_base_world.y());
  tf_odom_base.transform.translation.z = static_cast<float>(pos_base_world.z());
  // 旋转保持不变
  tf_odom_base.transform.rotation = tf2::toMsg(q_base);

  // 3. Twist (线速度)：KDL 实现 odom→pose 的速度变换 + 刚体速度补偿
  // 3.1 查询 odom→pose_frame
  geometry_msgs::TransformStamped tf_odom_pose;
  try
  {
    tf_odom_pose = tf_buffer_ptr->lookupTransform(
        odom,
        pose,
        odom_msg.header.stamp,
        ros::Duration(0.01));
  }
  catch (const tf2::TransformException &ex)
  {
    ROS_WARN_STREAM_THROTTLE(1.0, "TF lookup odom→pose_frame failed: " << ex.what());
    return;
  }

  // 3.2 构造 TwistStamped 并借助 tf2_kdl 做坐标系转换
  geometry_msgs::TwistStamped twist_in;
  twist_in.header.stamp = odom_msg.header.stamp;
  twist_in.header.frame_id = pose; // 源 = pose_frame
  twist_in.twist = odom_msg.twist.twist;

  tf2::Stamped<KDL::Twist> kdl_in;
  tf2::fromMsg(twist_in, kdl_in);

  tf2::Stamped<KDL::Twist> kdl_out;
  try
  {
    tf2::doTransform(kdl_in, kdl_out, tf_odom_pose);
  }
  catch (const tf2::TransformException &ex)
  {
    ROS_WARN_STREAM_THROTTLE(1.0, "TF doTransform(Twist) failed: " << ex.what());
    return;
  }
  geometry_msgs::TwistStamped twist_odom = tf2::toMsg(kdl_out);

  // 3.3 刚体速度补偿 v_base = v_pose + ω × r
  Eigen::Vector3d v_world(
      twist_odom.twist.linear.x,
      twist_odom.twist.linear.y,
      twist_odom.twist.linear.z);
  Eigen::Vector3d omega_world(
      twist_odom.twist.angular.x,
      twist_odom.twist.angular.y,
      twist_odom.twist.angular.z);

  // r = (补偿后 base_world) - (pose 在 world)：
  Eigen::Vector3d p_pose_world(
      tf_odom_pose.transform.translation.x,
      tf_odom_pose.transform.translation.y,
      tf_odom_pose.transform.translation.z);
  Eigen::Vector3d r = pos_base_world - p_pose_world;
  v_world += omega_world.cross(r);

  // 4. IMU 加速度/角速度：world→body + 重力补偿
  geometry_msgs::Vector3Stamped acc_in, acc_base, gyro_in, gyro_base;
  acc_in.header = gyro_in.header = imu_msg.header;
  acc_in.header.frame_id = imu_msg.header.frame_id;
  gyro_in.header.frame_id = imu_msg.header.frame_id;
  acc_in.vector = imu_msg.linear_acceleration;
  gyro_in.vector = imu_msg.angular_velocity;

  try
  {
    tf_buffer_ptr->transform(acc_in, acc_base, base_link, ros::Duration(0.01));
    tf_buffer_ptr->transform(gyro_in, gyro_base, base_link, ros::Duration(0.01));
  }
  catch (const tf2::TransformException &ex)
  {
    ROS_WARN_STREAM_THROTTLE(1, "IMU TF 失败: " << ex.what());
    return;
  }
  // 4.1 重力补偿： g_world = (0,0,9.81)
  tf2::Vector3 g_w(0, 0, 9.81), g_b = tf2::quatRotate(q_base.inverse(), g_w);
  acc_base.vector.x -= g_b.x();
  acc_base.vector.y -= g_b.y();
  acc_base.vector.z -= g_b.z();

  // —— 5. 提取数据：位置/速度/加速度 ——
  std::array<float, 3> pos, vel, acc, ang, ang_vel, ang_acc;
  // —— 5.1 位置 (m) ——
  pos = {
      static_cast<float>(tf_odom_base.transform.translation.x),
      static_cast<float>(tf_odom_base.transform.translation.y),
      static_cast<float>(tf_odom_base.transform.translation.z)};
  // —— 5.2 线速度 (m/s) ——
  vel = {
      static_cast<float>(v_world.x()),
      static_cast<float>(v_world.y()),
      static_cast<float>(v_world.z())};
  // —— 5.3 线加速度 (m/s²) ——
  acc = {
      static_cast<float>(acc_base.vector.x),
      static_cast<float>(acc_base.vector.y),
      static_cast<float>(acc_base.vector.z)};

  // —— 5.4 欧拉角转换 (四元数 → roll,pitch,yaw)并存储 ——
  {
    // 使用tf2的Matrix3x3提取欧拉角 (RPY，单位为弧度)
    double roll_rad, pitch_rad, yaw_rad;
    tf2::Matrix3x3(q_base).getRPY(roll_rad, pitch_rad, yaw_rad);

    // 角度 (rad)
    ang = {
        static_cast<float>(roll_rad),
        static_cast<float>(pitch_rad),
        static_cast<float>(yaw_rad)};
  }

  // —— 5.5 角速度 (rad/s) ——
  ang_vel = {
      static_cast<float>(gyro_base.vector.x),
      static_cast<float>(gyro_base.vector.y),
      static_cast<float>(gyro_base.vector.z)};

  // 5.6 角加速度 (rad/s²) → 差分 + 滑动平均
  // 计算滑动平均角加速度 (rad/s²)
  ros::Time curr_time = imu_msg.header.stamp;
  double dt = (curr_time - prev_imu_time).toSec(); // IMU 更新周期
  prev_imu_time = curr_time;

  // 差分计算角加速度
  std::array<float, 3> ang_acc_diff = {0, 0, 0};
  for (int i = 0; i < 3; ++i)
  {
    ang_acc_diff[i] = (dt > 0.0)
                          ? (ang_vel[i] - prev_ang_vel[i]) / static_cast<float>(dt)
                          : 0.0f;
  }

  // 更新 prev_ang_vel
  prev_ang_vel = ang_vel;

  // 推入缓冲用于滑动平均
  ang_acc_buffer.push_back(ang_acc_diff);
  if ((int)ang_acc_buffer.size() > ACC_WINDOW_SIZE)
  {
    ang_acc_buffer.pop_front();
  }

  // 计算均值
  ang_acc = {0.0f, 0.0f, 0.0f};
  for (auto &d : ang_acc_buffer)
  {
    for (int i = 0; i < 3; ++i)
      ang_acc[i] += d[i];
  }
  for (int i = 0; i < 3; ++i)
  {
    ang_acc[i] = ang_acc_buffer.empty()
                     ? 0.0f
                     : ang_acc[i] / static_cast<float>(ang_acc_buffer.size());
  }

  // --- 6. 获取期望数据 ---
  hra_msgs::TrajectoryPoint desired_state;
  {
    std::lock_guard<std::mutex> lock(desired_state_mutex);
    // 安全检查：如果超过0.2秒没收到新指令，则切换为悬停指令
    if (desired_state_received && (ros::Time::now() - last_desired_state_time).toSec() < 0.2)
    {
      desired_state = latest_desired_state;
    }
    else
    {
      // 生成悬停指令：期望位置=当前实际位置，其余为0
      desired_state.pose.position.x = pos[0];
      desired_state.pose.position.y = pos[1];
      desired_state.pose.position.z = pos[2];
      desired_state.pose.orientation = tf_odom_base.transform.rotation;
      // 速度和加速度默认为0
    }
  }

  // —— 7. 构建协议数据段 ——
  // 按协议：float ×36个 → int16_t ×36个 (乘以1000)
  std::vector<int16_t> all_data;
  all_data.reserve(36);
  auto append = [&](float v)
  {
    // 乘以1000并截断到 [-32768,32767]范围，避免溢出
    int32_t iv = static_cast<int32_t>(v * 1000.0f);
    iv = std::max(-32768, std::min(32767, iv));
    all_data.push_back(static_cast<int16_t>(iv));
  };
  // 遍历插入：
  // 期望值： 位置 (m), 速度 (m/s), 线加速度 (m^2), 共9个数据
  append(desired_state.pose.position.x);
  append(desired_state.pose.position.y);
  append(desired_state.pose.position.z);
  append(desired_state.velocity.linear.x);
  append(desired_state.velocity.linear.y);
  append(desired_state.velocity.linear.z);
  append(desired_state.acceleration.linear.x);
  append(desired_state.acceleration.linear.y);
  append(desired_state.acceleration.linear.z);

  // 期望值： 欧拉角 (rad), 角速度 (rad/s), 角加速度 (rad/s²), 共9个数据
  tf2::Quaternion q_des;
  tf2::fromMsg(desired_state.pose.orientation, q_des);
  double r_des, p_des, y_des;
  tf2::Matrix3x3(q_des).getRPY(r_des, p_des, y_des);
  append(r_des);
  append(p_des);
  append(y_des);
  append(desired_state.velocity.angular.x);
  append(desired_state.velocity.angular.y);
  append(desired_state.velocity.angular.z);
  append(desired_state.acceleration.angular.x);
  append(desired_state.acceleration.angular.y);
  append(desired_state.acceleration.angular.z);

  // 实际值: 位置 (m), 速度 (m/s), 线加速度 (m^2), 共9个数据
  for (float v : pos)
    append(v);
  for (float v : vel)
    append(v);
  for (float v : acc)
    append(v);

  // 实际值: 欧拉角 (rad), 角速度 (rad/s), 滑动平均角加速度 (rad/s²), 共9个数据
  for (float v : ang)
    append(v);
  for (float v : ang_vel)
    append(v);
  for (float v : ang_acc)
    append(v);

  // 8. 发布可视化数据
  // 8.1 更新并发布实际路径
  geometry_msgs::PoseStamped current_pose_stamped;
  current_pose_stamped.header.stamp = ros::Time::now();
  current_pose_stamped.header.frame_id = odom;
  current_pose_stamped.pose.position.x = pos[0];
  current_pose_stamped.pose.position.y = pos[1];
  current_pose_stamped.pose.position.z = pos[2];
  current_pose_stamped.pose.orientation = tf_odom_base.transform.rotation;

  actual_path_msg.header = current_pose_stamped.header;
  actual_path_msg.poses.push_back(current_pose_stamped);
  // // 可选：为了防止路径过长，可以限制其大小
  // if (actual_path_msg.poses.size() > 20000)
  // { // 保留最新的20000个点
  //   actual_path_msg.poses.erase(actual_path_msg.poses.begin());
  // }
  // actual_path_pub.publish(actual_path_msg);

  // 8.2 发布用于 rqt_plot 的数据
  std_msgs::Float64 msg_f64;
  // 位置
  msg_f64.data = desired_state.pose.position.x;
  plot_pos_x_des_pub.publish(msg_f64);
  msg_f64.data = pos[0];
  plot_pos_x_act_pub.publish(msg_f64);

  msg_f64.data = desired_state.pose.position.y;
  plot_pos_y_des_pub.publish(msg_f64);
  msg_f64.data = pos[1];
  plot_pos_y_act_pub.publish(msg_f64);

  msg_f64.data = desired_state.pose.position.z;
  plot_pos_z_des_pub.publish(msg_f64);
  msg_f64.data = pos[2];
  plot_pos_z_act_pub.publish(msg_f64);

  msg_f64.data = desired_state.velocity.linear.x;
  plot_vel_x_des_pub.publish(msg_f64);
  msg_f64.data = vel[0];
  plot_vel_x_act_pub.publish(msg_f64);

  msg_f64.data = desired_state.velocity.linear.y;
  plot_vel_y_des_pub.publish(msg_f64);
  msg_f64.data = vel[1];
  plot_vel_y_act_pub.publish(msg_f64);

  msg_f64.data = desired_state.velocity.linear.z;
  plot_vel_z_des_pub.publish(msg_f64);
  msg_f64.data = vel[2];
  plot_vel_z_act_pub.publish(msg_f64);

  msg_f64.data = desired_state.acceleration.linear.x;
  plot_acc_x_des_pub.publish(msg_f64);
  msg_f64.data = acc[0];
  plot_acc_x_act_pub.publish(msg_f64);

  msg_f64.data = desired_state.acceleration.linear.y;
  plot_acc_y_des_pub.publish(msg_f64);
  msg_f64.data = acc[1];
  plot_acc_y_act_pub.publish(msg_f64);

  msg_f64.data = desired_state.acceleration.linear.z;
  plot_acc_z_des_pub.publish(msg_f64);
  msg_f64.data = acc[2];
  plot_acc_z_act_pub.publish(msg_f64);

  // 角度
  msg_f64.data = r_des;
  plot_ang_x_des_pub.publish(msg_f64);
  msg_f64.data = ang[0];
  plot_ang_x_act_pub.publish(msg_f64);

  msg_f64.data = p_des;
  plot_ang_y_des_pub.publish(msg_f64);
  msg_f64.data = ang[1];
  plot_ang_y_act_pub.publish(msg_f64);

  msg_f64.data = y_des;
  plot_ang_z_des_pub.publish(msg_f64);
  msg_f64.data = ang[2];
  plot_ang_z_act_pub.publish(msg_f64);

  msg_f64.data = desired_state.velocity.angular.x;
  plot_ang_vel_x_des_pub.publish(msg_f64);
  msg_f64.data = ang_vel[0];
  plot_ang_vel_x_act_pub.publish(msg_f64);

  msg_f64.data = desired_state.velocity.angular.y;
  plot_ang_vel_y_des_pub.publish(msg_f64);
  msg_f64.data = ang_vel[1];
  plot_ang_vel_y_act_pub.publish(msg_f64);

  msg_f64.data = desired_state.velocity.angular.z;
  plot_ang_vel_z_des_pub.publish(msg_f64);
  msg_f64.data = ang_vel[2];
  plot_ang_vel_z_act_pub.publish(msg_f64);

  msg_f64.data = desired_state.acceleration.angular.x;
  plot_ang_acc_x_des_pub.publish(msg_f64);
  msg_f64.data = ang_acc[0];
  plot_ang_acc_x_act_pub.publish(msg_f64);

  msg_f64.data = desired_state.acceleration.angular.y;
  plot_ang_acc_y_des_pub.publish(msg_f64);
  msg_f64.data = ang_acc[1];
  plot_ang_acc_y_act_pub.publish(msg_f64);

  msg_f64.data = desired_state.acceleration.angular.z;
  plot_ang_acc_z_des_pub.publish(msg_f64);
  msg_f64.data = ang_acc[2];
  plot_ang_acc_z_act_pub.publish(msg_f64);

  // 8. 构建完整帧：帧头(0xAA,0xBB)、帧序号、时间戳、数据、校验、帧尾(0xCC,0xDD)
  std::vector<uint8_t> frame;
  frame.reserve(90); // 2+4+8+72+2+2

  // 8.1 帧头 (2字节)
  frame.push_back(0xAA);
  frame.push_back(0xBB);

  // 7.2 数据帧序号（4B, BE）
  uint32_t seq = g_seq++;
  for (int i = 3; i >= 0; --i)
    frame.push_back(static_cast<uint8_t>((seq >> (8 * i)) & 0xFF));

  // 7.3 时间戳（8B, BE）
  uint64_t t_ns = static_cast<uint64_t>(ros::Time::now().toNSec());
  for (int i = 7; i >= 0; --i)
    frame.push_back(static_cast<uint8_t>((t_ns >> (8 * i)) & 0xFF));

  // 7.4 payload (72 B, int16×36, BE)
  for (int16_t val : all_data)
  {
    frame.push_back((val >> 8) & 0xFF);
    frame.push_back(val & 0xFF);
  }

  // ---------- 计算 CRC16 大端校验和 ----------
  uint16_t crc = 0;
#if CRC_DEBUG_ENABLED
  ROS_INFO_STREAM("=== Upper CRC Debug ===");
  ROS_INFO_STREAM("Frame size before CRC: " << frame.size());
  ROS_INFO_STREAM("CRC calculation range: bytes 14-85 (72 bytes total)");

  // 打印用于CRC计算的后16字节数据（字节70-85，包含实际位姿信息）
  std::stringstream hex_stream;
  hex_stream << "CRC data (last 16 bytes): ";
  for (int i = 70; i < 86 && i < frame.size(); i++)
  {
    hex_stream << std::hex << std::setfill('0') << std::setw(2) << (int)frame[i] << " ";
  }
  ROS_INFO_STREAM(hex_stream.str());

  // 分步计算CRC，显示后8步的计算过程（对应后16字节）

  ROS_INFO_STREAM("CRC calculation step by step (last 8 steps, bytes 70-85):");

  // 先计算前面的部分（不显示）
  for (size_t i = 14; i < 70; i += 2)
  {
    crc += (static_cast<uint16_t>(frame[i]) << 8) | static_cast<uint16_t>(frame[i + 1]);
  }

  // 显示后8步的计算过程
  for (size_t i = 70, step = 0; i < 86; i += 2, step++)
  {
    uint16_t word = (static_cast<uint16_t>(frame[i]) << 8) | static_cast<uint16_t>(frame[i + 1]);
    crc += word;
    ROS_INFO_STREAM("Step " << (28 + step) << ": bytes[" << i << "," << (i + 1) << "] = 0x"
                            << std::hex << std::setfill('0') << std::setw(2) << (int)frame[i]
                            << std::setw(2) << (int)frame[i + 1]
                            << " -> word=0x" << std::setw(4) << word
                            << ", crc=0x" << std::setw(4) << crc);
  }
  #endif

  // 重新完整计算CRC（确保一致性）
  crc = 0;
  for (size_t i = 14; i < 86; i += 2)
  {
    crc += (static_cast<uint16_t>(frame[i]) << 8) | static_cast<uint16_t>(frame[i + 1]);
  }

  // ROS_INFO_STREAM("Final CRC: 0x" << std::hex << std::setfill('0') << std::setw(4) << crc);

  // 7.5 CRC16校验和 (2 B, BE)
  frame.push_back((crc >> 8) & 0xFF);
  frame.push_back(crc & 0xFF);

  // 7.6 帧尾 (2字节)
  frame.push_back(0xCC);
  frame.push_back(0xDD);

  // —— 8. 串口发送 ——
  ser.write(frame);

  // —— 9. ROS端调试信息 ——
#if CRC_DEBUG_ENABLED
  for (size_t i = 0; i < frame.size(); ++i)
  {
    ROS_INFO_STREAM("frame[" << i << "]: " << std::hex << (int)frame[i]);
  }
#endif
  // 使用 ROS_INFO_STREAM_THROTTLE(1.0) 将打印频率限制为每秒一次。
  // 这既能让我们看到实时数据，又不会阻塞ROS日志系统，还能让终端显示清晰。
  // 同时，移除了开头的 "\r"。
  ROS_INFO_STREAM_THROTTLE(1.0,
                           "--- Frame " << seq << " ---" << "\nFrame sent: " << frame.size() << " bytes. | Final CRC: 0x" << std::hex << std::setfill('0') << std::setw(4) << crc << "\nDesired Position: [" << desired_state.pose.position.x << ", " << desired_state.pose.position.y << ", " << desired_state.pose.position.z << "]" << "\nActual  Position: [" << pos[0] << ", " << pos[1] << ", " << pos[2] << "]" << "\nDesired Velocity: [" << desired_state.velocity.linear.x << ", " << desired_state.velocity.linear.y << ", " << desired_state.velocity.linear.z << "]" << "\nActual  Velocity: [" << vel[0] << ", " << vel[1] << ", " << vel[2] << "]");
}

// ===========================================================
// @brief 主函数：初始化 ROS 节点、串口、订阅器、TF2 监听、定时器
// ===========================================================

int main(int argc, char **argv)
{
  // —— 初始化ROS节点 ——
  ros::init(argc, argv, "rs_t265_serial_bridge_node");
  ros::NodeHandle nh;
  ros::NodeHandle pnh("~"); // **MODIFIED**：私有命名空间，对应 <node> 下的 <param>，用于读取私有参数

  // —— 读取参数 ——
  // 里程计&IMU订阅话题
  pnh.param<std::string>("odom_topic", odom_topic, "/rs_t265/odom/sample");
  pnh.param<std::string>("imu_topic", imu_topic, "/rs_t265/imu");

  // base_link 下发自 launch 的 <param name="base_link"…>
  pnh.param<std::string>("base_link", base_link, "base_link");
  pnh.param<std::string>("odom", odom, "rs_t265_odom_frame");
  pnh.param<std::string>("pose", pose, "rs_t265_pose_frame");

  // 静态偏置下发自 launch 的 <param name="offset_…" value="$(arg offset_…)"/>
  pnh.param<double>("offset_x", offset_x_, 0.0);
  pnh.param<double>("offset_y", offset_y_, 0.0);
  pnh.param<double>("offset_z", offset_z_, 0.0);

  // port 下发自 launch 的 <param name="port"…>
  std::string port;
  pnh.param<std::string>("port", port, "/dev/ttyTHS0");

  // baud 下发自 launch 的 <param name="baud"…>
  int baud;
  pnh.param<int>("baud", baud, 230400);

  // send_rate 下发自 launch 的 <param name="send_rate"…>
  double send_rate;
  pnh.param<double>("send_rate", send_rate, 100.0);

  // —— 串口初始化 ——
  try
  {
    ser.setPort(port);
    ser.setBaudrate(baud);
    serial::Timeout to = serial::Timeout::simpleTimeout(1000);
    ser.setTimeout(to);
    ser.open();
  }
  catch (serial::IOException &e)
  {
    ROS_FATAL("Unable to open serial port %s", port.c_str());
    return -1;
  }
  if (!ser.isOpen())
  {
    ROS_FATAL("Serial port %s not open", port.c_str());
    return -1;
  }
  ROS_INFO("Serial port %s initialized at %d baud", port.c_str(), baud);

  // —— TF Listener ——
  // **MODIFIED**：raw pointer 用 new 赋值
  tf_buffer_ptr = new tf2_ros::Buffer();
  tf_listener_ptr = new tf2_ros::TransformListener(*tf_buffer_ptr);

  // —— 订阅T265的位姿和IMU数据 ——
  ros::Subscriber odom_sub = nh.subscribe(odom_topic, 100, odomCallback);
  ros::Subscriber imu_sub = nh.subscribe(imu_topic, 100, imuCallback);

  // —— 初始化可视化发布器 ——
  actual_path_pub = nh.advertise<nav_msgs::Path>("/actual_path", 1);
  actual_path_msg.header.frame_id = "rs_t265_odom_frame";

  plot_pos_x_des_pub = nh.advertise<std_msgs::Float64>("/plot/pos/x/desired", 1);
  plot_pos_x_act_pub = nh.advertise<std_msgs::Float64>("/plot/pos/x/actual", 1);
  plot_pos_y_des_pub = nh.advertise<std_msgs::Float64>("/plot/pos/y/desired", 1);
  plot_pos_y_act_pub = nh.advertise<std_msgs::Float64>("/plot/pos/y/actual", 1);
  plot_pos_z_des_pub = nh.advertise<std_msgs::Float64>("/plot/pos/z/desired", 1);
  plot_pos_z_act_pub = nh.advertise<std_msgs::Float64>("/plot/pos/z/actual", 1);

  plot_vel_x_des_pub = nh.advertise<std_msgs::Float64>("/plot/vel/x/desired", 1);
  plot_vel_x_act_pub = nh.advertise<std_msgs::Float64>("/plot/vel/x/actual", 1);
  plot_vel_y_des_pub = nh.advertise<std_msgs::Float64>("/plot/vel/y/desired", 1);
  plot_vel_y_act_pub = nh.advertise<std_msgs::Float64>("/plot/vel/y/actual", 1);
  plot_vel_z_des_pub = nh.advertise<std_msgs::Float64>("/plot/vel/z/desired", 1);
  plot_vel_z_act_pub = nh.advertise<std_msgs::Float64>("/plot/vel/z/actual", 1);

  plot_acc_x_des_pub = nh.advertise<std_msgs::Float64>("/plot/acc/x/desired", 1);
  plot_acc_x_act_pub = nh.advertise<std_msgs::Float64>("/plot/acc/x/actual", 1);
  plot_acc_y_des_pub = nh.advertise<std_msgs::Float64>("/plot/acc/y/desired", 1);
  plot_acc_y_act_pub = nh.advertise<std_msgs::Float64>("/plot/acc/y/actual", 1);
  plot_acc_z_des_pub = nh.advertise<std_msgs::Float64>("/plot/acc/z/desired", 1);
  plot_acc_z_act_pub = nh.advertise<std_msgs::Float64>("/plot/acc/z/actual", 1);

  plot_ang_x_des_pub = nh.advertise<std_msgs::Float64>("/plot/ang/x/desired", 1);
  plot_ang_x_act_pub = nh.advertise<std_msgs::Float64>("/plot/ang/x/actual", 1);
  plot_ang_y_des_pub = nh.advertise<std_msgs::Float64>("/plot/ang/y/desired", 1);
  plot_ang_y_act_pub = nh.advertise<std_msgs::Float64>("/plot/ang/y/actual", 1);
  plot_ang_z_des_pub = nh.advertise<std_msgs::Float64>("/plot/ang/z/desired", 1);
  plot_ang_z_act_pub = nh.advertise<std_msgs::Float64>("/plot/ang/z/actual", 1);

  plot_ang_vel_x_des_pub = nh.advertise<std_msgs::Float64>("/plot/ang_vel/x/desired", 1);
  plot_ang_vel_x_act_pub = nh.advertise<std_msgs::Float64>("/plot/ang_vel/x/actual", 1);
  plot_ang_vel_y_des_pub = nh.advertise<std_msgs::Float64>("/plot/ang_vel/y/desired", 1);
  plot_ang_vel_y_act_pub = nh.advertise<std_msgs::Float64>("/plot/ang_vel/y/actual", 1);
  plot_ang_vel_z_des_pub = nh.advertise<std_msgs::Float64>("/plot/ang_vel/z/desired", 1);
  plot_ang_vel_z_act_pub = nh.advertise<std_msgs::Float64>("/plot/ang_vel/z/actual", 1);

  plot_ang_acc_x_des_pub = nh.advertise<std_msgs::Float64>("/plot/ang_acc/x/desired", 1);
  plot_ang_acc_x_act_pub = nh.advertise<std_msgs::Float64>("/plot/ang_acc/x/actual", 1);
  plot_ang_acc_y_des_pub = nh.advertise<std_msgs::Float64>("/plot/ang_acc/y/desired", 1);
  plot_ang_acc_y_act_pub = nh.advertise<std_msgs::Float64>("/plot/ang_acc/y/actual", 1);
  plot_ang_acc_z_des_pub = nh.advertise<std_msgs::Float64>("/plot/ang_acc/z/desired", 1);
  plot_ang_acc_z_act_pub = nh.advertise<std_msgs::Float64>("/plot/ang_acc/z/actual", 1);

  // —— 期望状态订阅器 ——
  ros::Subscriber desired_state_sub = nh.subscribe("/desired_state_topic", 1, desiredStateCallback);

  // —— 定时器：使用 send_rate 而非硬编码 ——
  ros::Timer timer = nh.createTimer(ros::Duration(1.0 / send_rate), timerCallback);

  // —— 进入循环 ——
  ros::spin();
  return 0;
}
