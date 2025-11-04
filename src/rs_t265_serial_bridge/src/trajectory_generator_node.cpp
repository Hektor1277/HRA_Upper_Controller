/**
 * trajectory_generator_node.cpp
 *
 * 功能:
 *   1. 提供一个 Action Server，接收点到点轨迹生成任务。
 *   2. 订阅机器人当前位姿，作为轨迹规划的起点。
 *   3. 内部实现一个五次多项式轨迹求解器。
 *   4. 任务执行期间，以100Hz频率采样轨迹并发布期望状态。
 *
 * 新增功能:
 *   - 包含 nav_msgs/Path.h
 *   - 新增 /desired_path 发布器，用于 RViz 可视化
 *   - 规划成功后，密集采样整条轨迹并发布 Path 消息
 *
 * 作者：Hektor Sun
 * 日期：2025-10-25
 */

#include <ros/ros.h>
#include <actionlib/server/simple_action_server.h>
#include <nav_msgs/Odometry.h>
#include <nav_msgs/Path.h>
#include <geometry_msgs/Pose.h>
#include <geometry_msgs/PoseStamped.h>
#include <tf2/LinearMath/Quaternion.h>
#include <tf2/LinearMath/Matrix3x3.h>
#include <Eigen/Core>
#include <Eigen/Dense>
#include <mutex>

#include "hra_msgs/ExecuteTrajectoryAction.h"
#include "hra_msgs/TrajectoryPoint.h"

// 帮助函数，用于处理Yaw角的周期性（从 PI 到 -PI 的最短路径）
double unwrap_angle(double wrapped_angle, double prev_angle)
{
    double diff = wrapped_angle - prev_angle;
    while (diff > M_PI)
        diff -= 2.0 * M_PI;
    while (diff < -M_PI)
        diff += 2.0 * M_PI;
    return prev_angle + diff;
}

// 五次多项式轨迹求解器
class QuinticPolynomialSolver
{
public:
    Eigen::Matrix<double, 6, 1> coeffs;

    // 计算系数
    void computeCoeffs(double p0, double v0, double a0, double p1, double v1, double a1, double T)
    {
        Eigen::Matrix<double, 6, 6> M;
        M << 1, 0, 0, 0, 0, 0,
            0, 1, 0, 0, 0, 0,
            0, 0, 2, 0, 0, 0,
            1, T, pow(T, 2), pow(T, 3), pow(T, 4), pow(T, 5),
            0, 1, 2 * T, 3 * pow(T, 2), 4 * pow(T, 3), 5 * pow(T, 4),
            0, 0, 2, 6 * T, 12 * pow(T, 2), 20 * pow(T, 3);

        Eigen::Matrix<double, 6, 1> b;
        b << p0, v0, a0, p1, v1, a1;

        coeffs = M.inverse() * b;
    }

    // 在时间t采样轨迹
    std::tuple<double, double, double> sample(double t)
    {
        double p = coeffs(0) + coeffs(1) * t + coeffs(2) * pow(t, 2) + coeffs(3) * pow(t, 3) + coeffs(4) * pow(t, 4) + coeffs(5) * pow(t, 5);
        double v = coeffs(1) + 2 * coeffs(2) * t + 3 * coeffs(3) * pow(t, 2) + 4 * coeffs(4) * pow(t, 3) + 5 * coeffs(5) * pow(t, 4);
        double a = 2 * coeffs(2) + 6 * coeffs(3) * t + 12 * coeffs(4) * pow(t, 2) + 20 * coeffs(5) * pow(t, 3);
        return {p, v, a};
    }
};

class TrajectoryGenerator
{
protected:
    ros::NodeHandle nh_;
    actionlib::SimpleActionServer<hra_msgs::ExecuteTrajectoryAction> as_;
    std::string action_name_;

    ros::Subscriber odom_sub_;
    ros::Publisher traj_point_pub_;
    ros::Publisher desired_path_pub_;
    ros::Timer sampling_timer_;

    nav_msgs::Odometry current_odom_;
    std::mutex odom_mutex_;
    bool odom_received_ = false;

    std::array<QuinticPolynomialSolver, 6> solvers_;
    ros::Time trajectory_start_time_;
    double trajectory_duration_ = 0.0;

public:
    TrajectoryGenerator(std::string name) : as_(nh_, name, boost::bind(&TrajectoryGenerator::executeCB, this, _1), false),
                                            action_name_(name)
    {
        odom_sub_ = nh_.subscribe("/rs_t265/odom/sample", 1, &TrajectoryGenerator::odomCB, this);
        traj_point_pub_ = nh_.advertise<hra_msgs::TrajectoryPoint>("/desired_state_topic", 10);
        desired_path_pub_ = nh_.advertise<nav_msgs::Path>("/desired_path", 1, true); // <-- 新增: true表示latched，新订阅者能收到最后一条消息

        as_.start();
        ROS_INFO("TrajectoryGenerator Action Server started.");
    }

    void odomCB(const nav_msgs::Odometry::ConstPtr &msg)
    {
        std::lock_guard<std::mutex> lock(odom_mutex_);
        current_odom_ = *msg;
        if (!odom_received_)
        {
            odom_received_ = true;
        }
    }

    void executeCB(const hra_msgs::ExecuteTrajectoryGoalConstPtr &goal)
    {
        if (!odom_received_)
        {
            ROS_ERROR("Cannot plan trajectory, no odometry received yet.");
            as_.setAborted();
            return;
        }

        // --- 1. 获取起点和终点状态 ---
        nav_msgs::Odometry start_odom;
        {
            std::lock_guard<std::mutex> lock(odom_mutex_);
            start_odom = current_odom_;
        }

        // 起点状态
        double start_p[6], start_v[6], start_a[6] = {0}; // x, y, z, roll, pitch, yaw
        start_p[0] = start_odom.pose.pose.position.x;
        start_p[1] = start_odom.pose.pose.position.y;
        start_p[2] = start_odom.pose.pose.position.z;
        start_v[0] = start_odom.twist.twist.linear.x;
        start_v[1] = start_odom.twist.twist.linear.y;
        start_v[2] = start_odom.twist.twist.linear.z;

        tf2::Quaternion q_start(start_odom.pose.pose.orientation.x, start_odom.pose.pose.orientation.y, start_odom.pose.pose.orientation.z, start_odom.pose.pose.orientation.w);
        tf2::Matrix3x3(q_start).getRPY(start_p[3], start_p[4], start_p[5]);

        // 终点状态
        double end_p[6], end_v[6] = {0}, end_a[6] = {0};
        end_p[0] = goal->target_pose.position.x;
        end_p[1] = goal->target_pose.position.y;
        end_p[2] = goal->target_pose.position.z;

        tf2::Quaternion q_end(goal->target_pose.orientation.x, goal->target_pose.orientation.y, goal->target_pose.orientation.z, goal->target_pose.orientation.w);
        tf2::Matrix3x3(q_end).getRPY(end_p[3], end_p[4], end_p[5]);

        // 对Yaw角进行解算，确保走最短路径
        end_p[5] = unwrap_angle(end_p[5], start_p[5]);

        // --- 2. 为6个DOF计算轨迹系数 ---
        trajectory_duration_ = goal->duration;
        for (int i = 0; i < 6; ++i)
        {
            solvers_[i].computeCoeffs(start_p[i], start_v[i], start_a[i], end_p[i], end_v[i], end_a[i], trajectory_duration_);
        }

        // --- 新增: 发布可视化路径 ---
        publishVisualPath();

        ROS_INFO("Trajectory planned successfully. Executing for %.2f seconds.", trajectory_duration_);

        // --- 3. 启动100Hz定时器开始执行 ---
        trajectory_start_time_ = ros::Time::now();
        sampling_timer_ = nh_.createTimer(ros::Duration(0.01), &TrajectoryGenerator::timerCB, this);

        // --- 4. 等待轨迹执行完成 ---
        ros::Rate r(10); // Check for completion at 10 Hz
        while (ros::ok())
        {
            if (as_.isPreemptRequested())
            {
                sampling_timer_.stop();
                as_.setPreempted();
                ROS_WARN("Trajectory execution preempted.");
                return;
            }

            if ((ros::Time::now() - trajectory_start_time_).toSec() >= trajectory_duration_)
            {
                break;
            }
            r.sleep();
        }

        sampling_timer_.stop();
        hra_msgs::ExecuteTrajectoryResult result;
        result.success = true;
        as_.setSucceeded(result);
        ROS_INFO("Trajectory execution finished.");
    }

    // 发布完整路径给RViz
    void publishVisualPath()
    {
        nav_msgs::Path path_msg;
        path_msg.header.stamp = ros::Time::now();
        path_msg.header.frame_id = "rs_t265_odom_frame"; // 路径在世界坐标系下

        // 密集采样，例如每20ms一个点
        for (double t = 0.0; t <= trajectory_duration_; t += 0.02)
        {
            geometry_msgs::PoseStamped pose_stamped;
            pose_stamped.header.stamp = path_msg.header.stamp; // 所有点用同一个时间戳
            pose_stamped.header.frame_id = path_msg.header.frame_id;

            double p[6], v[6], a[6];
            for (int i = 0; i < 6; ++i)
            {
                std::tie(p[i], v[i], a[i]) = solvers_[i].sample(t);
            }

            pose_stamped.pose.position.x = p[0];
            pose_stamped.pose.position.y = p[1];
            pose_stamped.pose.position.z = p[2];

            tf2::Quaternion q;
            q.setRPY(p[3], p[4], p[5]);
            pose_stamped.pose.orientation.x = q.x();
            pose_stamped.pose.orientation.y = q.y();
            pose_stamped.pose.orientation.z = q.z();
            pose_stamped.pose.orientation.w = q.w();

            path_msg.poses.push_back(pose_stamped);
        }
        desired_path_pub_.publish(path_msg);
    }

    void timerCB(const ros::TimerEvent &event)
    {
        double t = (ros::Time::now() - trajectory_start_time_).toSec();
        if (t > trajectory_duration_)
        {
            t = trajectory_duration_; // Clamp to final time
        }

        hra_msgs::TrajectoryPoint point_msg;
        point_msg.time_from_start = ros::Duration(t);

        double p[6], v[6], a[6];
        for (int i = 0; i < 6; ++i)
        {
            std::tie(p[i], v[i], a[i]) = solvers_[i].sample(t);
        }

        point_msg.pose.position.x = p[0];
        point_msg.pose.position.y = p[1];
        point_msg.pose.position.z = p[2];

        tf2::Quaternion q;
        q.setRPY(p[3], p[4], p[5]);
        point_msg.pose.orientation.x = q.x();
        point_msg.pose.orientation.y = q.y();
        point_msg.pose.orientation.z = q.z();
        point_msg.pose.orientation.w = q.w();

        point_msg.velocity.linear.x = v[0];
        point_msg.velocity.linear.y = v[1];
        point_msg.velocity.linear.z = v[2];
        point_msg.velocity.angular.x = v[3];
        point_msg.velocity.angular.y = v[4];
        point_msg.velocity.angular.z = v[5];

        point_msg.acceleration.linear.x = a[0];
        point_msg.acceleration.linear.y = a[1];
        point_msg.acceleration.linear.z = a[2];
        point_msg.acceleration.angular.x = a[3];
        point_msg.acceleration.angular.y = a[4];
        point_msg.acceleration.angular.z = a[5];

        traj_point_pub_.publish(point_msg);

        // --- 新增: 发布Action Feedback ---
        if (as_.isActive())
        {
            hra_msgs::ExecuteTrajectoryFeedback feedback;
            feedback.current_point = point_msg;
            feedback.elapsed_time = t;
            as_.publishFeedback(feedback);
        }
    }
};

int main(int argc, char **argv)
{
    ros::init(argc, argv, "trajectory_generator");
    TrajectoryGenerator generator("execute_trajectory");
    ros::spin();
    return 0;
}