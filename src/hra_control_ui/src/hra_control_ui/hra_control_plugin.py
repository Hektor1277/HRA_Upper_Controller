# [FINAL FIXED VERSION] hra_control_plugin.py

import os
import csv
import rospy
import rospkg
import actionlib
import subprocess
import signal
import math
from datetime import datetime

# RQT and Qt imports
from qt_gui.plugin import Plugin
from python_qt_binding import loadUi
from python_qt_binding.QtWidgets import QMainWindow, QFileDialog, QMessageBox
from python_qt_binding.QtCore import QTimer, Qt 

# ROS message and action imports
from hra_msgs.msg import ExecuteTrajectoryAction, ExecuteTrajectoryGoal, TrajectoryPoint
from nav_msgs.msg import Odometry, Path
from geometry_msgs.msg import PoseStamped
from tf.transformations import quaternion_from_euler

class HraControlPlugin(Plugin):

    def __init__(self, context):
        super(HraControlPlugin, self).__init__(context)
        self.setObjectName('HraControlPlugin')

        self._widget = QMainWindow()
        # 加载 UI 文件
        ui_file = os.path.join(rospkg.RosPack().get_path('hra_control_ui'), 'resource', 'HraControlUi.ui')
        loadUi(ui_file, self._widget)
        self._widget.setObjectName('HraControlUi')
        
        if context.serial_number() > 1:
            self._widget.setWindowTitle(self._widget.windowTitle() + (' (%d)' % context.serial_number()))
        context.add_widget(self._widget)

        # --- 初始化变量 ---
        self.csv_trajectory_data = [] 
        self.csv_playing = False
        self.csv_start_time = None
        self.manual_active = False
        self.rosbag_process = None

        # --- 路径设置 ---
        self.traj_dir = os.path.join(rospkg.RosPack().get_path('hra_control_ui'), 'resource', 'trajectories')
        if not os.path.exists(self.traj_dir):
            os.makedirs(self.traj_dir)
        
        self.bags_dir = os.path.join(rospkg.RosPack().get_path('hra_control_ui'), 'bags')
        if not os.path.exists(self.bags_dir):
            os.makedirs(self.bags_dir)

        # --- ROS 通信 ---
        self.pub_desired = rospy.Publisher('/desired_state_topic', TrajectoryPoint, queue_size=1)
        self.pub_path_viz = rospy.Publisher('/desired_csv_path', Path, queue_size=1, latch=True)
        # 实时目标点可视化
        self.pub_pose_viz = rospy.Publisher('/desired_pose_viz', PoseStamped, queue_size=1)
        
        self.desired_state_sub = rospy.Subscriber('/desired_state_topic', TrajectoryPoint, self.desired_state_callback)
        self.actual_state_sub = rospy.Subscriber('/rs_t265/odom/sample', Odometry, self.actual_state_callback)

        # [FIXED] Action Client 初始化移回 __init__
        try:
            if not rospy.is_shutdown():
                self.action_client = actionlib.SimpleActionClient('execute_trajectory', ExecuteTrajectoryAction)
                self._widget.label_status.setText('Status: Waiting for Action Server...')
                # 使用较短超时，非阻塞 GUI 太久
                if self.action_client.wait_for_server(rospy.Duration(1.0)):
                    self._widget.label_status.setText('Status: Connected. Ready.')
                else:
                    self._widget.label_status.setText('Status: Action Server NOT FOUND.')
                    self._widget.pushButton_send_goal.setEnabled(False)
                    # 尝试获取参数以适配界面 (可选)
                    self.operating_mode = rospy.get_param('/trajectory_generator/operating_mode', 'free_flying')
                    self.update_ui_for_mode()
        except Exception as e:
             self._widget.label_status.setText('Status: ROS Init Error!')
             rospy.logerr("HRA Control UI: Error initializing action client: %s" % str(e))

        # --- 定时器 ---
        # 1. CSV 播放定时器 (100Hz)
        self.play_timer = QTimer(self)
        self.play_timer.timeout.connect(self.update_csv_playback)
        
        # 2. 手动模式定时器 (100Hz)
        self.manual_timer = QTimer(self)
        self.manual_timer.timeout.connect(self.update_manual_setpoint)

        # --- 信号绑定 ---
        # Tab 1: CSV & Manual
        self._widget.btn_csv_refresh.clicked.connect(self.refresh_csv_list)
        self._widget.btn_csv_load.clicked.connect(self.load_selected_csv)
        self._widget.btn_csv_play.clicked.connect(self.toggle_csv_playback)
        self._widget.chk_manual_stream.stateChanged.connect(self.toggle_manual_stream)
        if hasattr(self._widget, 'btn_manual_single'):
             self._widget.btn_manual_single.clicked.connect(self.send_manual_single_frame)
        else:
             rospy.logwarn("UI missing 'btn_manual_single' button!")
        
        # 初始刷新列表
        self.refresh_csv_list() 

        # Tab 2: Polynomial Solver
        self._widget.pushButton_send_goal.clicked.connect(self.on_send_goal_clicked)
        self._widget.pushButton_cancel_goal.clicked.connect(self.on_cancel_goal_clicked)
        self._widget.pushButton_cancel_goal.setEnabled(False) 

    # ================= CSV 功能区 =================
    def refresh_csv_list(self):
        self._widget.comboBox_csv_files.clear()
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
                
                # 智能读取循环
                for i, row in enumerate(reader):
                    # 1. 忽略空行
                    if not row: continue 
                    
                    # 2. 尝试解析数值
                    try:
                        vals = [float(x) for x in row]
                    except ValueError:
                        # 解析失败（可能是标题行或含有非数字字符），跳过
                        continue

                    # 3. 检查列数是否足够
                    if len(vals) < 19: continue
                    
                    # 4. 构建数据点 (按照 DOF-Grouped 顺序)
                    point = {
                        't': vals[0],
                        'pos': [vals[1], vals[4], vals[7]],     # x, y, z
                        'vel': [vals[2], vals[5], vals[8]],     # vx, vy, vz
                        'acc': [vals[3], vals[6], vals[9]],     # ax, ay, az
                        'ang': [vals[10], vals[13], vals[16]],  # r, p, y
                        'ang_vel': [vals[11], vals[14], vals[17]], # wx, wy, wz
                        'ang_acc': [vals[12], vals[15], vals[18]]  # alx, aly, alz
                    }
                    self.csv_trajectory_data.append(point)

                       # --- [新增] 数据重采样/插值处理 ---
            if self.csv_trajectory_data:
                # 检查是否太稀疏 (例如只有首尾两帧)
                # 如果点数太少，且总时长很长，说明需要插值
                duration = self.csv_trajectory_data[-1]['t']
                count = len(self.csv_trajectory_data)
                
                # 预期的点数 (按 100Hz 计算)
                expected_count = int(duration * 100) 
                
                # 如果实际点数远少于预期 (例如少于 10%)，则启动插值
                if count < expected_count * 0.1 and count >= 2:
                    rospy.loginfo(f"Sparse trajectory detected ({count} pts). Resampling to 100Hz...")
                    new_data = []
                    curr_idx = 0
                    
                    # 以 0.01s 为步长生成新时间轴
                    # 生成 t = 0, 0.01, 0.02 ... duration
                    t_resampled = 0.0
                    while t_resampled <= duration:
                        # 找到包含 t_resampled 的区间 [p1, p2]
                        # 确保 curr_idx 指向 p1
                        while curr_idx < count - 1 and self.csv_trajectory_data[curr_idx+1]['t'] < t_resampled:
                            curr_idx += 1
                        
                        p1 = self.csv_trajectory_data[curr_idx]
                        p2 = self.csv_trajectory_data[min(curr_idx+1, count-1)]
                        
                        # 简单的零阶保持 (Zero-Order Hold) 插值
                        # 对于静态轨迹，这是完美的。对于稀疏的动态轨迹，可能不够平滑，
                        # 但这里主要为了解决 Static Keeping 问题。
                        # 如果需要线性插值，代码会更复杂一些，暂且使用复制最近点策略。
                        
                        new_pt = p1.copy() # 复制状态
                        new_pt['t'] = t_resampled # 更新时间戳
                        new_data.append(new_pt)
                        
                        t_resampled += 0.01 # 100Hz
                        
                    self.csv_trajectory_data = new_data
                    rospy.loginfo(f"Resampling complete. New count: {len(new_data)}")

            # --- 加载后检查 ---
            if self.csv_trajectory_data:
                # 检查第一帧是否接近 T=0
                first_t = self.csv_trajectory_data[0]['t']
                if not math.isclose(first_t, 0.0, abs_tol=1e-3):
                    rospy.logwarn(f"CSV Warning: Trajectory starts at T={first_t:.4f}, not 0.0!")
                    # 自动修复：强制插入一个 T=0 的帧，状态与第一帧相同
                    first_pt_copy = self.csv_trajectory_data[0].copy()
                    first_pt_copy['t'] = 0.0
                    self.csv_trajectory_data.insert(0, first_pt_copy)

                duration = self.csv_trajectory_data[-1]['t']
                count = len(self.csv_trajectory_data)
                self._widget.label_csv_info.setText(f"Loaded: {count} pts, T={duration:.2f}s")
                self._widget.progressBar_csv.setValue(0)
                self.publish_csv_path_viz() # Rviz 预览
                self._widget.label_status.setText(f"CSV Loaded: {filename}")
            else:
                self._widget.label_csv_info.setText("Error: Valid data not found")

        except Exception as e:
            self._widget.label_csv_info.setText("Load Error")
            rospy.logerr(f"CSV Load Error: {e}")

    def publish_csv_path_viz(self):
        path_msg = Path()
        path_msg.header.stamp = rospy.Time.now()
        path_msg.header.frame_id = "rs_t265_odom_frame"
        
        for pt in self.csv_trajectory_data:
            pose = PoseStamped()
            pose.header.frame_id = path_msg.header.frame_id
            pose.pose.position.x = pt['pos'][0]
            pose.pose.position.y = pt['pos'][1]
            pose.pose.position.z = pt['pos'][2]
            
            q = quaternion_from_euler(pt['ang'][0], pt['ang'][1], pt['ang'][2])
            pose.pose.orientation.x = q[0]
            pose.pose.orientation.y = q[1]
            pose.pose.orientation.z = q[2]
            pose.pose.orientation.w = q[3]
            path_msg.poses.append(pose)
            
        self.pub_path_viz.publish(path_msg)

    def toggle_csv_playback(self):
        if not self.csv_trajectory_data: return

        if self.csv_playing:
            # 停止
            self.csv_playing = False
            self.play_timer.stop()
            self._widget.btn_csv_play.setText("Play")
            self._widget.label_status.setText("CSV Playback Stopped")
        else:
            # 开始
            self.csv_playing = True
            self.csv_start_time = rospy.Time.now().to_sec()
            self.play_timer.start(10) # 10ms = 100Hz
            self._widget.btn_csv_play.setText("Stop")
            self._widget.label_status.setText("CSV Playing...")

    def update_csv_playback(self):
        if not self.csv_playing or not self.csv_trajectory_data: return

        elapsed = rospy.Time.now().to_sec() - self.csv_start_time
        total_duration = self.csv_trajectory_data[-1]['t']
        
        # 进度条
        if total_duration > 0:
            progress = int((elapsed / total_duration) * 100)
            self._widget.progressBar_csv.setValue(min(100, progress))

        if elapsed > total_duration:
            self.toggle_csv_playback() # 自动结束
            return

        # 线性查找 (因为数据有序且频率匹配，此方法足够高效)
        target_pt = None
        for pt in self.csv_trajectory_data:
            if pt['t'] >= elapsed:
                target_pt = pt
                break
        
        if target_pt:
            self.publish_trajectory_point(target_pt)

    # ================= Manual 功能区 =================
    def toggle_manual_stream(self, state):
        """ 切换 100Hz 连续发送模式 """
        if state == Qt.Checked:
            self.manual_active = True
            self.manual_timer.start(10) # 100Hz
            self._widget.label_status.setText("Manual Stream ON (100Hz)")
            
            # 互斥处理：
            # 1. 禁用 CSV 播放
            if self.csv_playing: self.toggle_csv_playback()
            self._widget.btn_csv_play.setEnabled(False)
            
            # 2. 禁用单步按钮 (避免混淆)
            if hasattr(self._widget, 'btn_manual_single'):
                self._widget.btn_manual_single.setEnabled(False)
                
        else:
            self.manual_active = False
            self.manual_timer.stop()
            self._widget.label_status.setText("Manual Stream OFF")
            
            # 恢复其他控件
            self._widget.btn_csv_play.setEnabled(True)
            if hasattr(self._widget, 'btn_manual_single'):
                self._widget.btn_manual_single.setEnabled(True)

    def send_manual_single_frame(self):
        """ 发送单帧手动设定数据 """
        self._widget.label_status.setText("Manual Single Shot Sent")
        self.update_manual_setpoint() # 复用这个函数来读取UI并发送一次

    def update_manual_setpoint(self):
        # 注意：请确保 .ui 文件中的 ObjectName 与此处一致！
        try:
            x = self._widget.X_doubleSpinBox.value()
            y = self._widget.Y_doubleSpinBox.value()
            z = self._widget.Z_doubleSpinBox.value()
            r = self._widget.Roll_doubleSpinBox.value()
            p = self._widget.Pitch_doubleSpinBox.value()
            yw = self._widget.Yaw_doubleSpinBox.value()

            pt = {
                't': 0.0,
                'pos': [x, y, z],
                'vel': [0, 0, 0], 
                'acc': [0, 0, 0],
                'ang': [r, p, yw],
                'ang_vel': [0, 0, 0],
                'ang_acc': [0, 0, 0]
            }
            self.publish_trajectory_point(pt)
        except AttributeError:
            rospy.logwarn_throttle(1, "UI Control Name Mismatch! Check dsb_manual_x vs X_doubleSpinBox")

    # ================= 公共发布函数 =================
    def publish_trajectory_point(self, pt_dict):
        msg = TrajectoryPoint()
        msg.time_from_start = rospy.Duration(pt_dict['t'])
        
        # Pos
        msg.pose.position.x = pt_dict['pos'][0]
        msg.pose.position.y = pt_dict['pos'][1]
        msg.pose.position.z = pt_dict['pos'][2]
        
        q = quaternion_from_euler(pt_dict['ang'][0], pt_dict['ang'][1], pt_dict['ang'][2])
        msg.pose.orientation.x = q[0]
        msg.pose.orientation.y = q[1]
        msg.pose.orientation.z = q[2]
        msg.pose.orientation.w = q[3]

        # Vel
        msg.velocity.linear.x = pt_dict['vel'][0]
        msg.velocity.linear.y = pt_dict['vel'][1]
        msg.velocity.linear.z = pt_dict['vel'][2]
        msg.velocity.angular.x = pt_dict['ang_vel'][0]
        msg.velocity.angular.y = pt_dict['ang_vel'][1]
        msg.velocity.angular.z = pt_dict['ang_vel'][2]

        # Acc
        msg.acceleration.linear.x = pt_dict['acc'][0]
        msg.acceleration.linear.y = pt_dict['acc'][1]
        msg.acceleration.linear.z = pt_dict['acc'][2]
        msg.acceleration.angular.x = pt_dict['ang_acc'][0]
        msg.acceleration.angular.y = pt_dict['ang_acc'][1]
        msg.acceleration.angular.z = pt_dict['ang_acc'][2]

        self.pub_desired.publish(msg)

        # ---------------------------------------------------------
        # 可视化当前目标 Pose (箭头)
        # ---------------------------------------------------------
        viz_msg = PoseStamped()
        viz_msg.header.stamp = rospy.Time.now()
        viz_msg.header.frame_id = "rs_t265_odom_frame" # 与 T265 坐标系一致
        
        # 填充位置
        viz_msg.pose.position.x = msg.pose.position.x
        viz_msg.pose.position.y = msg.pose.position.y
        viz_msg.pose.position.z = msg.pose.position.z
        
        # 填充姿态
        viz_msg.pose.orientation = msg.pose.orientation
        
        self.pub_pose_viz.publish(viz_msg)
        # ---------------------------------------------------------

    # ================= P2P 功能区 =================
    def update_ui_for_mode(self):
        """ 根据运行模式屏蔽 Z/Roll/Pitch 输入 (Ground Testing) """
        try:
            is_3dof = (self.operating_mode == 'ground_testing')
            
            self._widget.lineEdit_pos_z.setEnabled(not is_3dof)
            self._widget.lineEdit_ori_r.setEnabled(not is_3dof)
            self._widget.lineEdit_ori_p.setEnabled(not is_3dof)
            
            if is_3dof:
                self._widget.lineEdit_pos_z.setText("0.0")
                self._widget.lineEdit_ori_r.setText("0.0")
                self._widget.lineEdit_ori_p.setText("0.0")
        except:
            pass

    # --- 更新UI状态显示 ---
    def desired_state_callback(self, msg):
        pos = msg.pose.position
        vel = msg.velocity.linear
        self._widget.label_desired_pos.setText("X:{:.2f} Y:{:.2f} Z:{:.2f}".format(pos.x, pos.y, pos.z))
        self._widget.label_desired_vel.setText("X:{:.2f} Y:{:.2f} Z:{:.2f}".format(vel.x, vel.y, vel.z))

    def actual_state_callback(self, msg):
        pos = msg.pose.pose.position
        vel = msg.twist.twist.linear
        self._widget.label_actual_pos.setText("X:{:.2f} Y:{:.2f} Z:{:.2f}".format(pos.x, pos.y, pos.z))
        self._widget.label_actual_vel.setText("X:{:.2f} Y:{:.2f} Z:{:.2f}".format(vel.x, vel.y, vel.z))

    def on_send_goal_clicked(self):
        try:
            pos_x = float(self._widget.lineEdit_pos_x.text() or 0.0)
            pos_y = float(self._widget.lineEdit_pos_y.text() or 0.0)
            pos_z = float(self._widget.lineEdit_pos_z.text() or 0.0)
            ori_r = float(self._widget.lineEdit_ori_r.text() or 0.0)
            ori_p = float(self._widget.lineEdit_ori_p.text() or 0.0)
            ori_y = float(self._widget.lineEdit_ori_y.text() or 0.0)
            duration = float(self._widget.lineEdit_duration.text() or 0.0)
            
            if duration <= 0:
                self._widget.label_status.setText('Error: Duration <= 0')
                return
        except ValueError:
            self._widget.label_status.setText('Error: Invalid Number')
            return
            
        # 启动录制
        self.start_rosbag_recording(pos_x, pos_y, pos_z, duration)

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
        
        self.action_client.send_goal(goal, done_cb=self.goal_done_cb, active_cb=self.goal_active_cb, feedback_cb=self.goal_feedback_cb)
        
        self._widget.label_status.setText('Goal Sent.')
        self._widget.label_total_time.setText("{:.2f} s".format(duration))
        self._widget.pushButton_send_goal.setEnabled(False)
        self._widget.pushButton_cancel_goal.setEnabled(True)

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
        self._widget.label_elapsed_time.setText("{:.2f} s".format(feedback.elapsed_time))

    def start_rosbag_recording(self, x, y, z, dur):
        if self.rosbag_process is not None:
            self.stop_rosbag_recording()

        topics_to_record = ["/desired_state_topic", "/desired_path", "/actual_path", "/rs_t265/odom/sample", "/tf", "/tf_static"]
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = "{}_goal_X{:.1f}_Y{:.1f}_Z{:.1f}_dur{:.1f}s.bag".format(timestamp, x, y, z, dur)
        full_path = os.path.join(self.bags_dir, filename)

        command = ['rosbag', 'record', '-O', full_path] + topics_to_record
        self.rosbag_process = subprocess.Popen(command)

    def stop_rosbag_recording(self):
        if self.rosbag_process is None: return
        try:
            self.rosbag_process.send_signal(signal.SIGINT)
            self.rosbag_process.wait(timeout=5)
        except:
            self.rosbag_process.kill()
        self.rosbag_process = None

    def shutdown_plugin(self):
        """ 在关闭插件时由RQT调用的函数，用于清理资源 """
        if hasattr(self, 'action_client'):
            try:
                self.action_client.cancel_all_goals()
            except:
                pass
        
        # 强制停止所有定时器
        self.play_timer.stop()
        self.manual_timer.stop()
        
        # 确保 rosbag 进程被杀掉
        self.stop_rosbag_recording()

    def save_settings(self, plugin_settings, instance_settings): pass
    def restore_settings(self, plugin_settings, instance_settings): pass