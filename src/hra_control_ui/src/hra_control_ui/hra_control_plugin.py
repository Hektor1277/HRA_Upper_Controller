# [FINAL & CORRECTED VERSION] hra_control_plugin.py
# This version strictly follows ROS Noetic RQT plugin best practices.

import os
import rospy
import rospkg
import actionlib

# RQT and Qt imports
from qt_gui.plugin import Plugin
from python_qt_binding import loadUi
# --- [核心修正] ---
# 我们不再使用通用的 QWidget，而是明确导入 .ui 文件对应的顶层控件类型 QMainWindow
from python_qt_binding.QtWidgets import QMainWindow 
# --------------------

# ROS message and action imports
from hra_msgs.msg import ExecuteTrajectoryAction, ExecuteTrajectoryGoal
from geometry_msgs.msg import Pose
from tf.transformations import quaternion_from_euler


class HraControlPlugin(Plugin):

    def __init__(self, context):
        """
        插件的构造函数，在RQT加载插件时被调用。
        :param context: RQT提供的上下文对象，用于与主框架交互。
        """
        super(HraControlPlugin, self).__init__(context)
        self.setObjectName('HraControlPlugin')

        # --- [核心修正] ---
        # 1. 创建一个 QMainWindow 实例，而不是 QWidget。
        #    这必须与你在 Qt Designer 中选择的顶层控件类型（"Main Window"）完全匹配。
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
        except Exception as e:
             self._widget.label_status.setText('Status: ROS Init Error!')
             rospy.logerr("HRA Control UI: Error initializing action client: %s" % str(e))

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
            return

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
        self.action_client.send_goal(goal, done_cb=self.goal_done_cb, feedback_cb=self.goal_feedback_cb)
        
        # 更新UI状态
        self._widget.label_status.setText('Status: Goal sent. Executing...')
        self._widget.pushButton_send_goal.setEnabled(False)
        self._widget.pushButton_cancel_goal.setEnabled(True)

    def on_cancel_goal_clicked(self):
        """ 当 'CANCEL' 按钮被点击时调用的函数 """
        self.action_client.cancel_goal()
        self._widget.label_status.setText('Status: Goal cancellation requested.')

    def goal_done_cb(self, state, result):
        """ Action 完成时的回调函数 """
        self._widget.label_status.setText('Status: Task finished with state code: ' + str(state))
        self._widget.pushButton_send_goal.setEnabled(True)
        self._widget.pushButton_cancel_goal.setEnabled(False)

    def goal_feedback_cb(self, feedback):
        """ Action 执行过程中的反馈回调（当前未使用） """
        pass

    def shutdown_plugin(self):
        """ 在关闭插件时由RQT调用的函数，用于清理资源 """
        if hasattr(self, 'action_client'):
            self.action_client.cancel_all_goals()
        pass

    def save_settings(self, plugin_settings, instance_settings):
        """ 用于保存插件设置（当前未使用） """
        pass

    def restore_settings(self, plugin_settings, instance_settings):
        """ 用于恢复插件设置（当前未使用） """
        pass