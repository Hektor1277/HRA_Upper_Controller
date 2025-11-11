# [FINAL & ENHANCED VERSION V2] hra_control_plugin.py
# - Fixes the 'NULL' total time display.
# - Integrates automated rosbag recording.

import os
import rospy
import rospkg
import actionlib
import subprocess
import signal
from datetime import datetime

# RQT and Qt imports
from qt_gui.plugin import Plugin
from python_qt_binding import loadUi
from python_qt_binding.QtWidgets import QMainWindow 

# ROS message and action imports
from hra_msgs.msg import ExecuteTrajectoryAction, ExecuteTrajectoryGoal, TrajectoryPoint
from nav_msgs.msg import Odometry
from tf.transformations import quaternion_from_euler


class HraControlPlugin(Plugin):

    def __init__(self, context):
        """
        插件的构造函数，在RQT加载插件时被调用。
        :param context: RQT提供的上下文对象，用于与主框架交互。
        """
        super(HraControlPlugin, self).__init__(context)
        self.setObjectName('HraControlPlugin')

        self._widget = QMainWindow()
        # --------------------
        # 2. 获取 .ui 文件的绝对路径
        #    rospkg.RosPack().get_path() 是在ROS中查找包路径的标准方法。
        ui_file = os.path.join(rospkg.RosPack().get_path('hra_control_ui'), 'resource', 'HraControlUi.ui')
        # 3. 使用 loadUi 将 .ui 文件中的设计加载到我们的 QMainWindow 实例上。
        #    这会自动创建 .ui 文件中定义的所有控件，并使它们成为 self._widget 的子控件。
        loadUi(ui_file, self._widget)
        self._widget.setObjectName('HraControlUi')
        # 4. 将我们配置好的 widget 添加到 RQT 的主界面中。
        #    context.serial_number() 用于区分同一插件的多个实例。
        if context.serial_number() > 1:
            self._widget.setWindowTitle(self._widget.windowTitle() + (' (%d)' % context.serial_number()))
        context.add_widget(self._widget)

        # --- ROS & UI Logic ---

        # 5. 将UI控件的信号（如 "clicked"）连接到我们的处理函数（slots）。
        self._widget.pushButton_send_goal.clicked.connect(self.on_send_goal_clicked)
        self._widget.pushButton_cancel_goal.clicked.connect(self.on_cancel_goal_clicked)
        self._widget.pushButton_cancel_goal.setEnabled(False) # 初始时禁用取消按钮
        # --- 新增: rosbag 相关的成员变量 ---
        self.rosbag_process = None
        self.bags_dir = os.path.join(rospkg.RosPack().get_path('hra_control_ui'), 'bags')
        if not os.path.exists(self.bags_dir):
            os.makedirs(self.bags_dir)

        self.desired_state_sub = rospy.Subscriber('/desired_state_topic', TrajectoryPoint, self.desired_state_callback)
        self.actual_state_sub = rospy.Subscriber('/rs_t265/odom/sample', Odometry, self.actual_state_callback)

        # 6. 初始化 Action 客户端。
        #    使用 try-except 块来处理 roscore 未运行或 action server 不可用的情况。
        try:
            if not rospy.is_shutdown():
                self.action_client = actionlib.SimpleActionClient('execute_trajectory', ExecuteTrajectoryAction)
                self._widget.label_status.setText('Status: Waiting for Action Server...')
            
                # 等待服务器连接，设置一个较短的超时时间。
                if self.action_client.wait_for_server(rospy.Duration(2.0)):
                    self._widget.label_status.setText('Status: Connected. Ready.')
                else:
                    self._widget.label_status.setText('Status: Action Server NOT FOUND.')
                    self._widget.pushButton_send_goal.setEnabled(False)
                    self.operating_mode = rospy.get_param('/trajectory_generator/operating_mode', 'free_flying')
                    self.update_ui_for_mode()
        except Exception as e:
             self._widget.label_status.setText('Status: ROS Init Error!')
             rospy.logerr("HRA Control UI: Error initializing action client: %s" % str(e))

    def update_ui_for_mode(self):
        """ 根据运行模式启用或禁用UI控件 """
        is_3dof = (self.operating_mode == 'ground_testing')
        
        self._widget.lineEdit_pos_z.setEnabled(not is_3dof)
        self._widget.lineEdit_ori_r.setEnabled(not is_3dof)
        self._widget.lineEdit_ori_p.setEnabled(not is_3dof)
        
        if is_3dof:
            self._widget.lineEdit_pos_z.setText("0.0")
            self._widget.lineEdit_ori_r.setText("0.0")
            self._widget.lineEdit_ori_p.setText("0.0")
            # 可以在这里改变标签颜色或添加提示
            self._widget.label_status.setText('Status: ground_testing Mode. Ready.')

    # --- 更新UI ---
    def desired_state_callback(self, msg):
        pos = msg.pose.position
        vel = msg.velocity.linear
        self._widget.label_desired_pos.setText("X: {:.3f}, Y: {:.3f}, Z: {:.3f}".format(pos.x, pos.y, pos.z))
        self._widget.label_desired_vel.setText("X: {:.3f}, Y: {:.3f}, Z: {:.3f}".format(vel.x, vel.y, vel.z))

    def actual_state_callback(self, msg):
        # 注意: 这里显示的是T265 odom frame下的位姿，与最终map frame下的位姿可能因静态变换而不同
        # 但对于实时观察速度和大致位置足够了
        pos = msg.pose.pose.position
        vel = msg.twist.twist.linear
        self._widget.label_actual_pos.setText("X: {:.3f}, Y: {:.3f}, Z: {:.3f}".format(pos.x, pos.y, pos.z))
        self._widget.label_actual_vel.setText("X: {:.3f}, Y: {:.3f}, Z: {:.3f}".format(vel.x, vel.y, vel.z))

    def on_send_goal_clicked(self):
        """ 当 'SEND GOAL' 按钮被点击时调用的函数 """
        try:
            # 读取输入框文本，如果为空，则默认为0.0，增强鲁棒性。
            pos_x = float(self._widget.lineEdit_pos_x.text() or 0.0)
            pos_y = float(self._widget.lineEdit_pos_y.text() or 0.0)
            pos_z = float(self._widget.lineEdit_pos_z.text() or 0.0)
            ori_r = float(self._widget.lineEdit_ori_r.text() or 0.0)
            ori_p = float(self._widget.lineEdit_ori_p.text() or 0.0)
            ori_y = float(self._widget.lineEdit_ori_y.text() or 0.0)
            duration = float(self._widget.lineEdit_duration.text() or 0.0)
            
            if duration <= 0:
                self._widget.label_status.setText('Status: Error! Duration must be > 0.')
                return
        except ValueError:
            self._widget.label_status.setText('Status: Error! Invalid input. Use numbers.')
            
        # --- 启动 rosbag 录制 ---
        self.start_rosbag_recording(pos_x, pos_y, pos_z, duration)

        # 创建并填充 Action Goal
        goal = ExecuteTrajectoryGoal()
        goal.target_pose.position.x = pos_x
        goal.target_pose.position.y = pos_y
        goal.target_pose.position.z = pos_z
        q = quaternion_from_euler(ori_r, ori_p, ori_y)
        goal.target_pose.orientation.x = q[0]
        goal.target_pose.orientation.y = q[1]
        goal.target_pose.orientation.z = q[2]
        goal.target_pose.orientation.w = q[3]
        goal.duration = duration
        
        # 发送目标，并注册完成和反馈的回调函数
        self.action_client.send_goal(goal, done_cb=self.goal_done_cb, active_cb=self.goal_active_cb, feedback_cb=self.goal_feedback_cb)
        
        # 更新UI状态
        self._widget.label_status.setText('Status: Goal sent. Executing...')
        self._widget.label_total_time.setText("{:.2f} s".format(duration))
        self._widget.pushButton_send_goal.setEnabled(False)
        self._widget.pushButton_cancel_goal.setEnabled(True)

    def on_cancel_goal_clicked(self):
        """ 当 'CANCEL' 按钮被点击时调用的函数 """
        self.action_client.cancel_goal()
        self._widget.label_status.setText('Status: Goal cancellation requested.')

    def goal_active_cb(self):
        """ 当任务开始时调用的回调 """
        self._widget.label_status.setText('Status: Goal accepted. Executing...')

    def goal_done_cb(self, state, result):
        """ Action 完成时的回调函数 """
        self._widget.label_status.setText('Status: Task finished with state code: ' + str(state))
        self._widget.pushButton_send_goal.setEnabled(True)
        self._widget.pushButton_cancel_goal.setEnabled(False)
        self._widget.label_elapsed_time.setText("0.00 s") # 任务结束后重置时间
        self._widget.label_total_time.setText("NULL") # 任务结束后重置总时长
        
        # --- 停止 rosbag 录制 ---
        self.stop_rosbag_recording()
    def goal_feedback_cb(self, feedback):
        """ Action 执行过程中的反馈回调 """
        # --- 更新已执行时长 ---
        self._widget.label_elapsed_time.setText("{:.2f} s".format(feedback.elapsed_time))

    def start_rosbag_recording(self, x, y, z, dur):
        """ 构建rosbag命令并启动录制进程 """
        if self.rosbag_process is not None:
            rospy.logwarn("A rosbag process is already running. Stopping it first.")
            self.stop_rosbag_recording()

        # 1. 定义要录制的话题
        topics_to_record = [
            "/desired_state_topic",
            "/desired_path",
            "/actual_path",
            "/rs_t265/odom/sample",
            "/tf",
            "/tf_static"
        ]

        # 2. 生成文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = "{}_goal_X{:.1f}_Y{:.1f}_Z{:.1f}_dur{:.1f}s.bag".format(timestamp, x, y, z, dur)
        full_path = os.path.join(self.bags_dir, filename)

        # 3. 构建命令并启动子进程
        command = ['rosbag', 'record', '-O', full_path] + topics_to_record
        rospy.loginfo("Starting rosbag recording with command: %s" % ' '.join(command))
        self.rosbag_process = subprocess.Popen(command)
        self._widget.label_status.setText('Status: Recording started...')

    def stop_rosbag_recording(self):
        """ 停止正在运行的rosbag录制进程 """
        if self.rosbag_process is None:
            return

        rospy.loginfo("Stopping rosbag recording (PID: %d)..." % self.rosbag_process.pid)
        try:
            # 向rosbag进程发送SIGINT信号，等同于Ctrl+C
            self.rosbag_process.send_signal(signal.SIGINT)
            
            # 等待进程终止，设置一个超时
            self.rosbag_process.wait(timeout=5)
            rospy.loginfo("Rosbag process terminated successfully.")
        except subprocess.TimeoutExpired:
            rospy.logwarn("Rosbag process did not terminate in time, killing it.")
            self.rosbag_process.kill()
        except Exception as e:
            rospy.logerr("Error stopping rosbag process: %s" % str(e))
        
        self.rosbag_process = None

    def shutdown_plugin(self):
        """ 在关闭插件时由RQT调用的函数，用于清理资源 """
        if hasattr(self, 'action_client'):
            self.action_client.cancel_all_goals()
        self.stop_rosbag_recording() # 确保插件关闭时也停止录制
        pass

    def save_settings(self, plugin_settings, instance_settings):
        """ 用于保存插件设置（当前未使用） """
        pass

    def restore_settings(self, plugin_settings, instance_settings):
        """ 用于恢复插件设置（当前未使用） """
        pass