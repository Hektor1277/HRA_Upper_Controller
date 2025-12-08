# [FINAL UPDATED VERSION V4] hra_control_plugin.py
# Features: 
# - Subscribes to processed /plot topics from C++ bridge (No local math)
# - Adapted to new Tabbed UI (Pos/Ang, Vel, Acc)
# - Implements Peak-Hold (Max Abs) monitoring
# - Auto-reset metrics on task start

import os
import csv
import rospy
import rospkg
import actionlib
import subprocess
import signal
import math
import numpy as np
from functools import partial
from datetime import datetime

# RQT and Qt imports
from qt_gui.plugin import Plugin
from python_qt_binding import loadUi
from python_qt_binding.QtWidgets import QMainWindow
from python_qt_binding.QtCore import QTimer, Qt 

# ROS message imports
from hra_msgs.msg import ExecuteTrajectoryAction, ExecuteTrajectoryGoal, TrajectoryPoint
from nav_msgs.msg import Path
from geometry_msgs.msg import PoseStamped
from std_msgs.msg import Float64
from tf.transformations import quaternion_from_euler

class HraControlPlugin(Plugin):

    def __init__(self, context):
        super(HraControlPlugin, self).__init__(context)
        self.setObjectName('HraControlPlugin')

        self._widget = QMainWindow()
        ui_file = os.path.join(rospkg.RosPack().get_path('hra_control_ui'), 'resource', 'HraControlUi.ui')
        loadUi(ui_file, self._widget)
        self._widget.setObjectName('HraControlUi')
        
        if context.serial_number() > 1:
            self._widget.setWindowTitle(self._widget.windowTitle() + (' (%d)' % context.serial_number()))
        context.add_widget(self._widget)

        # --- 变量初始化 ---
        self.csv_trajectory_data = [] 
        self.csv_playing = False
        self.csv_start_time = None
        self.manual_active = False
        self.rosbag_process = None
        
        # 数据缓存字典 (用于 UI 显示)
        # 结构: self.data_cache['pos']['x']
        self.data_keys = ['pos', 'vel', 'acc', 'ang', 'ang_vel', 'ang_acc']
        self.axes = ['x', 'y', 'z']
        
        self.actual_vals = {key: {ax: 0.0 for ax in self.axes} for key in self.data_keys}
        self.desired_vals = {key: {ax: 0.0 for ax in self.axes} for key in self.data_keys}
        self.max_vals = {key: {ax: 0.0 for ax in self.axes} for key in self.data_keys}

        # --- 路径设置 ---
        self.traj_dir = os.path.join(rospkg.RosPack().get_path('hra_control_ui'), 'resource', 'trajectories')
        if not os.path.exists(self.traj_dir): os.makedirs(self.traj_dir)
        self.bags_dir = os.path.join(rospkg.RosPack().get_path('hra_control_ui'), 'bags')
        if not os.path.exists(self.bags_dir): os.makedirs(self.bags_dir)

        # --- ROS 通信 ---
        # 发布器
        self.pub_desired = rospy.Publisher('/desired_state_topic', TrajectoryPoint, queue_size=1)
        self.pub_path_viz = rospy.Publisher('/desired_csv_path', Path, queue_size=1, latch=True)
        self.pub_pose_viz = rospy.Publisher('/desired_pose_viz', PoseStamped, queue_size=1)
        
        # 订阅器 1: 期望状态 (TrajectoryPoint 包含所有期望值)
        self.desired_state_sub = rospy.Subscriber('/desired_state_topic', TrajectoryPoint, self.desired_state_callback)
        
        # 订阅器 2: 实际状态 (批量订阅 /plot/.../actual)
        # 这种方式避免了在 Python 端做复杂的 TF 变换和重力补偿，直接显示下位机收到的数据
        for key in self.data_keys:
            for ax in self.axes:
                topic_name = f"/plot/{key}/{ax}/actual"
                rospy.Subscriber(topic_name, Float64, partial(self.actual_data_callback, key, ax))

        # Action Client
        try:
            if not rospy.is_shutdown():
                self.action_client = actionlib.SimpleActionClient('execute_trajectory', ExecuteTrajectoryAction)
                self._widget.label_status.setText('Status: Waiting for Action Server...')
                if self.action_client.wait_for_server(rospy.Duration(1.0)):
                    self._widget.label_status.setText('Status: Connected. Ready.')
                else:
                    self._widget.label_status.setText('Status: Action Server NOT FOUND.')
                    self._widget.pushButton_send_goal.setEnabled(False)
                    self.operating_mode = rospy.get_param('/trajectory_generator/operating_mode', 'free_flying')
                    self.update_ui_for_mode()
        except Exception as e:
             self._widget.label_status.setText('Status: ROS Init Error!')
             rospy.logerr(str(e))

        # --- 定时器 ---
        # 1. CSV 播放 (100Hz)
        self.play_timer = QTimer(self)
        self.play_timer.timeout.connect(self.update_csv_playback)
        
        # 2. 手动模式 (100Hz)
        self.manual_timer = QTimer(self)
        self.manual_timer.timeout.connect(self.update_manual_setpoint)
        
        # 3. UI 刷新 (10Hz) - 解耦数据接收和显示，避免界面卡顿
        self.ui_timer = QTimer(self)
        self.ui_timer.timeout.connect(self.update_ui_display)
        self.ui_timer.start(100) # 100ms interval

        # --- 信号绑定 ---
        # CSV
        self._widget.btn_csv_refresh.clicked.connect(self.refresh_csv_list)
        self._widget.btn_csv_load.clicked.connect(self.load_selected_csv)
        self._widget.btn_csv_play.clicked.connect(self.toggle_csv_playback)
        self.refresh_csv_list() 
        
        # Manual
        self._widget.chk_manual_stream.stateChanged.connect(self.toggle_manual_stream)
        if hasattr(self._widget, 'btn_manual_single'):
             self._widget.btn_manual_single.clicked.connect(self.send_manual_single_frame)

        # P2P Action
        self._widget.pushButton_send_goal.clicked.connect(self.on_send_goal_clicked)
        self._widget.pushButton_cancel_goal.clicked.connect(self.on_cancel_goal_clicked)
        self._widget.pushButton_cancel_goal.setEnabled(False) 

    # ================= 核心逻辑：数据回调与处理 =================

    def reset_performance_metrics(self):
        """ 清零所有最大值记录 (分轴清零) """
        # 遍历字典的每一层进行清零
        for key in self.max_vals:
            for ax in self.axes:
                self.max_vals[key][ax] = 0.0
                
        # 立即刷新一次 UI 显示归零
        self.update_ui_display()

    def actual_data_callback(self, key, ax, msg):
        """ 通用回调：处理 C++ 节点发来的单个浮点数据 """
        val = msg.data
        # 1. 存储当前值
        self.actual_vals[key][ax] = val
        
        # 2. 更新特定轴的最大值 (Peak Hold per Axis)
        if abs(val) > abs(self.max_vals[key][ax]):
            self.max_vals[key][ax] = val

    def desired_state_callback(self, msg):
        """ 处理期望状态消息 (TrajectoryPoint) 并解包到字典 """
        # Pos
        self.desired_vals['pos']['x'] = msg.pose.position.x
        self.desired_vals['pos']['y'] = msg.pose.position.y
        self.desired_vals['pos']['z'] = msg.pose.position.z
        
        # Vel
        self.desired_vals['vel']['x'] = msg.velocity.linear.x
        self.desired_vals['vel']['y'] = msg.velocity.linear.y
        self.desired_vals['vel']['z'] = msg.velocity.linear.z
        
        # Acc
        self.desired_vals['acc']['x'] = msg.acceleration.linear.x
        self.desired_vals['acc']['y'] = msg.acceleration.linear.y
        self.desired_vals['acc']['z'] = msg.acceleration.linear.z
        
        # Ang (Quat -> Euler)
        q = msg.pose.orientation
        import tf.transformations
        (r, p, y) = tf.transformations.euler_from_quaternion([q.x, q.y, q.z, q.w])
        self.desired_vals['ang']['x'] = r
        self.desired_vals['ang']['y'] = p
        self.desired_vals['ang']['z'] = y
        
        # Ang Vel
        self.desired_vals['ang_vel']['x'] = msg.velocity.angular.x
        self.desired_vals['ang_vel']['y'] = msg.velocity.angular.y
        self.desired_vals['ang_vel']['z'] = msg.velocity.angular.z
        
        # Ang Acc
        self.desired_vals['ang_acc']['x'] = msg.acceleration.angular.x
        self.desired_vals['ang_acc']['y'] = msg.acceleration.angular.y
        self.desired_vals['ang_acc']['z'] = msg.acceleration.angular.z

    def update_ui_display(self):
        """ 定时刷新 UI 标签 (10Hz) """
        # 定义 UI Label 与 数据 Key 的映射关系
        # 格式: (key, label_actual, label_desired, label_max, is_angle)
        ui_map = [
            ('pos', 'label_actual_pos', 'label_desired_pos', 'label_max_pos', False),
            ('ang', 'label_actual_ang', 'label_desired_ang', 'label_max_ang', True), # Ang uses R/P/Y
            ('vel', 'label_actual_vel', 'label_desired_vel', 'label_max_vel', False),
            ('ang_vel', 'label_actual_ang_vel', 'label_desired_ang_vel', 'label_max_ang_vel', False),
            ('acc', 'label_actual_acc', 'label_desired_acc', 'label_max_acc', False),
            ('ang_acc', 'label_actual_ang_acc', 'label_desired_ang_acc', 'label_max_ang_acc', False),
        ]

        for key, lbl_act, lbl_des, lbl_max, is_ang in ui_map:
            # 1. Update Actual
            if hasattr(self._widget, lbl_act):
                vals = self.actual_vals[key]
                prefix = ['R', 'P', 'Y'] if is_ang else ['X', 'Y', 'Z']
                text = f"{prefix[0]}:{vals['x']:.3f} {prefix[1]}:{vals['y']:.3f} {prefix[2]}:{vals['z']:.3f}"
                getattr(self._widget, lbl_act).setText(text)
            
            # 2. Update Desired
            if hasattr(self._widget, lbl_des):
                vals = self.desired_vals[key]
                prefix = ['R', 'P', 'Y'] if is_ang else ['X', 'Y', 'Z']
                text = f"{prefix[0]}:{vals['x']:.3f} {prefix[1]}:{vals['y']:.3f} {prefix[2]}:{vals['z']:.3f}"
                getattr(self._widget, lbl_des).setText(text)
            
            # 3. Update Max (Vector Display)
            # 现在 max_vals[key] 是一个字典，包含 x,y,z
            if hasattr(self._widget, lbl_max):
                vals = self.max_vals[key]
                # 格式化字符串：保留3位小数，显示各轴最大值
                text = f"{prefix[0]}:{vals['x']:.3f} {prefix[1]}:{vals['y']:.3f} {prefix[2]}:{vals['z']:.3f}"
                getattr(self._widget, lbl_max).setText(text)

    # ================= CSV 功能区 =================
    def refresh_csv_list(self):
        self._widget.comboBox_csv_files.clear()
        # [Reset Trigger] Refreshing list resets metrics
        self.reset_performance_metrics()
        
        if os.path.exists(self.traj_dir):
            files = [f for f in os.listdir(self.traj_dir) if f.endswith('.csv')]
            files.sort()
            self._widget.comboBox_csv_files.addItems(files)

    def load_selected_csv(self):
        filename = self._widget.comboBox_csv_files.currentText()
        if not filename: return
        filepath = os.path.join(self.traj_dir, filename)
        try:
            self.csv_trajectory_data = []
            with open(filepath, 'r') as f:
                reader = csv.reader(f)
                for i, row in enumerate(reader):
                    if not row: continue 
                    try: vals = [float(x) for x in row]
                    except ValueError: continue
                    if len(vals) < 19: continue
                    point = {
                        't': vals[0],
                        'pos': [vals[1], vals[4], vals[7]], 'vel': [vals[2], vals[5], vals[8]], 'acc': [vals[3], vals[6], vals[9]],
                        'ang': [vals[10], vals[13], vals[16]], 'ang_vel': [vals[11], vals[14], vals[17]], 'ang_acc': [vals[12], vals[15], vals[18]]
                    }
                    self.csv_trajectory_data.append(point)
            
            # 稀疏数据重采样逻辑 (处理 Static Keeping 等 2行数据的情况)
            if self.csv_trajectory_data:
                duration = self.csv_trajectory_data[-1]['t']
                count = len(self.csv_trajectory_data)
                expected_count = int(duration * 100)
                
                if count < expected_count * 0.1 and count >= 2:
                    rospy.loginfo(f"Resampling sparse CSV ({count} pts)...")
                    new_data = []
                    curr_idx = 0
                    t_res = 0.0
                    while t_res <= duration:
                        while curr_idx < count - 1 and self.csv_trajectory_data[curr_idx+1]['t'] < t_res:
                            curr_idx += 1
                        pt = self.csv_trajectory_data[curr_idx].copy()
                        pt['t'] = t_res
                        new_data.append(pt)
                        t_res += 0.01
                    self.csv_trajectory_data = new_data

                # 检查首帧时间
                first_t = self.csv_trajectory_data[0]['t']
                if not math.isclose(first_t, 0.0, abs_tol=1e-3):
                    pt0 = self.csv_trajectory_data[0].copy()
                    pt0['t'] = 0.0
                    self.csv_trajectory_data.insert(0, pt0)

                self._widget.label_csv_info.setText(f"Loaded: {len(self.csv_trajectory_data)} pts, T={duration:.3f}s")
                self.publish_csv_path_viz()
                self._widget.label_status.setText(f"CSV Loaded: {filename}")

        except Exception as e:
            rospy.logerr(f"CSV Load Error: {e}")

    def publish_csv_path_viz(self):
        path_msg = Path()
        path_msg.header.stamp = rospy.Time.now()
        path_msg.header.frame_id = "rs_t265_odom_frame"
        for pt in self.csv_trajectory_data:
            pose = PoseStamped()
            pose.header = path_msg.header
            pose.pose.position.x = pt['pos'][0]; pose.pose.position.y = pt['pos'][1]; pose.pose.position.z = pt['pos'][2]
            q = quaternion_from_euler(pt['ang'][0], pt['ang'][1], pt['ang'][2])
            pose.pose.orientation.x = q[0]; pose.pose.orientation.y = q[1]; pose.pose.orientation.z = q[2]; pose.pose.orientation.w = q[3]
            path_msg.poses.append(pose)
        self.pub_path_viz.publish(path_msg)

    def toggle_csv_playback(self):
        if not self.csv_trajectory_data: return
        if self.csv_playing:
            self.csv_playing = False
            self.play_timer.stop()
            self._widget.btn_csv_play.setText("Play")
        else:
            # [Reset Trigger] Start Playback
            self.reset_performance_metrics()
            self.csv_playing = True
            self.csv_start_time = rospy.Time.now().to_sec()
            self.play_timer.start(10)
            self._widget.btn_csv_play.setText("Stop")

    def update_csv_playback(self):
        if not self.csv_playing: return
        elapsed = rospy.Time.now().to_sec() - self.csv_start_time
        total_duration = self.csv_trajectory_data[-1]['t']
        if total_duration > 0:
            self._widget.progressBar_csv.setValue(min(100, int((elapsed/total_duration)*100)))
        if elapsed > total_duration:
            self.toggle_csv_playback()
            return
        target_pt = None
        for pt in self.csv_trajectory_data:
            if pt['t'] >= elapsed:
                target_pt = pt
                break
        if target_pt: self.publish_trajectory_point(target_pt)

    # ================= Manual & P2P 功能区 =================
    def toggle_manual_stream(self, state):
        if state == Qt.Checked:
            # [Reset Trigger] Enable Manual Stream
            self.reset_performance_metrics()
            self.manual_active = True
            self.manual_timer.start(10)
            self._widget.btn_csv_play.setEnabled(False)
            if hasattr(self._widget, 'btn_manual_single'): self._widget.btn_manual_single.setEnabled(False)
        else:
            self.manual_active = False
            self.manual_timer.stop()
            self._widget.btn_csv_play.setEnabled(True)
            if hasattr(self._widget, 'btn_manual_single'): self._widget.btn_manual_single.setEnabled(True)

    def send_manual_single_frame(self):
        # [Reset Trigger] Single Shot
        self.reset_performance_metrics()
        self.update_manual_setpoint()

    def update_manual_setpoint(self):
        try:
            # 适配新的 UI 命名 (假设你也更新了 UI 文件中的对象名)
            # 这里为了兼容性，尝试读取 dsb_manual_x 或 X_doubleSpinBox
            x = self.get_spinbox_val('dsb_manual_x', 'X_doubleSpinBox')
            y = self.get_spinbox_val('dsb_manual_y', 'Y_doubleSpinBox')
            z = self.get_spinbox_val('dsb_manual_z', 'Z_doubleSpinBox')
            r = self.get_spinbox_val('dsb_manual_roll', 'Roll_doubleSpinBox')
            p = self.get_spinbox_val('dsb_manual_pitch', 'Pitch_doubleSpinBox')
            yw = self.get_spinbox_val('dsb_manual_yaw', 'Yaw_doubleSpinBox')
            
            pt = {'t':0,'pos':[x,y,z],'vel':[0,0,0],'acc':[0,0,0],'ang':[r,p,yw],'ang_vel':[0,0,0],'ang_acc':[0,0,0]}
            self.publish_trajectory_point(pt)
        except: pass

    def get_spinbox_val(self, name1, name2):
        if hasattr(self._widget, name1): return getattr(self._widget, name1).value()
        if hasattr(self._widget, name2): return getattr(self._widget, name2).value()
        return 0.0

    def on_send_goal_clicked(self):
        try:
            pos_x = float(self._widget.lineEdit_pos_x.text() or 0.0)
            pos_y = float(self._widget.lineEdit_pos_y.text() or 0.0)
            pos_z = float(self._widget.lineEdit_pos_z.text() or 0.0)
            ori_r = float(self._widget.lineEdit_ori_r.text() or 0.0)
            ori_p = float(self._widget.lineEdit_ori_p.text() or 0.0)
            ori_y = float(self._widget.lineEdit_ori_y.text() or 0.0)
            duration = float(self._widget.lineEdit_duration.text() or 0.0)
            if duration <= 0: return
        except ValueError: return
            
        # [Reset Trigger] Send Goal
        self.reset_performance_metrics()
        self.start_rosbag_recording(pos_x, pos_y, pos_z, duration)

        goal = ExecuteTrajectoryGoal()
        goal.target_pose.position.x = pos_x; goal.target_pose.position.y = pos_y; goal.target_pose.position.z = pos_z
        q = quaternion_from_euler(ori_r, ori_p, ori_y)
        goal.target_pose.orientation.x = q[0]; goal.target_pose.orientation.y = q[1]; goal.target_pose.orientation.z = q[2]; goal.target_pose.orientation.w = q[3]
        goal.duration = duration
        
        self.action_client.send_goal(goal, done_cb=self.goal_done_cb, active_cb=self.goal_active_cb, feedback_cb=self.goal_feedback_cb)
        
        self._widget.label_status.setText('Goal Sent.')
        self._widget.label_total_time.setText("{:.3f} s".format(duration))
        self._widget.pushButton_send_goal.setEnabled(False)
        self._widget.pushButton_cancel_goal.setEnabled(True)

    # ... (辅助函数：on_cancel, callbacks, rosbag, shutdown) ...
    def on_cancel_goal_clicked(self):
        self.action_client.cancel_goal()
        self._widget.label_status.setText('Canceling...')

    def goal_active_cb(self):
        self._widget.label_status.setText('Executing...')

    def goal_done_cb(self, state, result):
        self._widget.label_status.setText(f'Finished: {state}')
        self._widget.pushButton_send_goal.setEnabled(True)
        self._widget.pushButton_cancel_goal.setEnabled(False)
        self._widget.label_elapsed_time.setText("0.00 s") 
        self.stop_rosbag_recording()

    def goal_feedback_cb(self, feedback):
        self._widget.label_elapsed_time.setText("{:.3f} s".format(feedback.elapsed_time))

    def start_rosbag_recording(self, x, y, z, dur):
        if self.rosbag_process is not None: self.stop_rosbag_recording()
        topics = ["/desired_state_topic", "/desired_path", "/actual_path", "/rs_t265/odom/sample", "/tf", "/tf_static"]
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        fn = "{}_goal_X{:.1f}_Y{:.1f}_Z{:.1f}_dur{:.1f}s.bag".format(ts, x, y, z, dur)
        cmd = ['rosbag', 'record', '-O', os.path.join(self.bags_dir, fn)] + topics
        self.rosbag_process = subprocess.Popen(cmd)

    def stop_rosbag_recording(self):
        if self.rosbag_process is None: return
        try:
            self.rosbag_process.send_signal(signal.SIGINT)
            self.rosbag_process.wait(timeout=5)
        except: self.rosbag_process.kill()
        self.rosbag_process = None
    
    def publish_trajectory_point(self, pt_dict):
        msg = TrajectoryPoint()
        msg.time_from_start = rospy.Duration(pt_dict['t'])
        msg.pose.position.x = pt_dict['pos'][0]; msg.pose.position.y = pt_dict['pos'][1]; msg.pose.position.z = pt_dict['pos'][2]
        q = quaternion_from_euler(pt_dict['ang'][0], pt_dict['ang'][1], pt_dict['ang'][2])
        msg.pose.orientation.x = q[0]; msg.pose.orientation.y = q[1]; msg.pose.orientation.z = q[2]; msg.pose.orientation.w = q[3]
        msg.velocity.linear.x = pt_dict['vel'][0]; msg.velocity.linear.y = pt_dict['vel'][1]; msg.velocity.linear.z = pt_dict['vel'][2]
        msg.velocity.angular.x = pt_dict['ang_vel'][0]; msg.velocity.angular.y = pt_dict['ang_vel'][1]; msg.velocity.angular.z = pt_dict['ang_vel'][2]
        msg.acceleration.linear.x = pt_dict['acc'][0]; msg.acceleration.linear.y = pt_dict['acc'][1]; msg.acceleration.linear.z = pt_dict['acc'][2]
        msg.acceleration.angular.x = pt_dict['ang_acc'][0]; msg.acceleration.angular.y = pt_dict['ang_acc'][1]; msg.acceleration.angular.z = pt_dict['ang_acc'][2]
        
        self.pub_desired.publish(msg)
        
        viz_msg = PoseStamped()
        viz_msg.header.stamp = rospy.Time.now()
        viz_msg.header.frame_id = "rs_t265_odom_frame"
        viz_msg.pose = msg.pose
        self.pub_pose_viz.publish(viz_msg)

    def shutdown_plugin(self):
        if hasattr(self, 'action_client'): self.action_client.cancel_all_goals()
        self.stop_rosbag_recording()
        self.play_timer.stop()
        self.manual_timer.stop()
        self.ui_timer.stop()

    def save_settings(self, plugin_settings, instance_settings): pass
    def restore_settings(self, plugin_settings, instance_settings): pass