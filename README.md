# T265 Serial Bridge for ROS

本项目实现了将 Intel RealSense T265 相机采集的六组运动数据（位置、速度、加速度、欧拉角、角速度、角加速度）通过 ROS 处理后，通过串口以 100 Hz 速率发送给下位机滑模控制器的完整流程。

---

## 1. 项目目标

* **采集**：通过 Intel RealSense T265 相机获取机器人状态数据。
* **处理**：在 ROS 中完成坐标系转换、静态偏置补偿、重力补偿、刚体速度补偿。
* **通信**：按协议打包数据，通过串口发送给下位机滑模控制器。
* **应用**：为滑模控制算法提供高频、低延迟的姿态与运动状态反馈。

---

## 2. 系统架构

```
Intel T265 (rs_t265)
      ↓
 realsense2_camera (nodelet)
      ↓
rs_t265_serial_bridge_node  ── 串口(UART)
      ↓                       ↓
 下位机滑模控制器 (SMC)
```

---

## 3. 数据处理流程

| 序号 | 数据项       | 来源 Topic / TF                           | 原始坐标系               | 目标坐标系    | 处理方法概述                                                                              |
| -: | :-------- | :-------------------------------------- | :------------------ | :------- | :---------------------------------------------------------------------------------- |
|  1 | 位置 (pos)  | `/rs_t265/odom/sample.pose`             | odom → base\_link   | 世界 / 机器人 | 1. `lookupTransform(odom, base_link)`<br>2. 提取平移向量 p\_raw<br>3. 静态偏置补偿：`p_raw - p₀` |
|  2 | 线速度 (vel) | `/rs_t265/odom/sample.twist.linear`     | pose\_frame         | 世界 / 机器人 | 1. 读 v\_pose<br>2. 刚体补偿：`v_base = v_pose + ω × (p_base - p_pose)`                   |
|  3 | 线加速度(acc) | `/rs_t265/imu.linear_acceleration`      | imu\_frame(optical) | 机体系      | 1. `tf2::transform` 转 base\_link<br>2. 重力补偿：`a - R⁻¹·[0,0,-9.8]`                    |
|  4 | 欧拉角 (ang) | `/rs_t265/odom/sample.pose.orientation` | —                   | 世界       | 四元数 → `tf2::Matrix3x3.getRPY(roll,pitch,yaw)`                                       |
|  5 | 角速度 (ω)   | `/rs_t265/imu.angular_velocity`         | imu\_frame(optical) | 机体系      | `tf2::transform` 转 base\_link                                                       |
|  6 | 角加速度 (α)  | 差分 + 滑动平均                               | 机体系                 | 机体系      | 1. 差分：`dω/dt`<br>2. 滑动平均滤波                                                          |

---

## 4. 核心实现要点

1. **缓冲与选帧**：

   * 维护 `odom_buffer`、`imu_buffer`，互斥锁保护，定时回调选取与当前时刻最接近的数据。
2. **坐标系转换**：

   * `tf2_ros::Buffer.lookupTransform` 获取动态 & 静态 TF。
   * Eigen 处理位置、四元数；Orocos KDL（tf2\_kdl）处理 `Twist` 旋转。
3. **补偿策略**：

   * **静态偏置**：`p_corrected = p_raw - offset`。
   * **重力补偿**：`a_corrected = a_measured - R⁻¹·g_world`。
   * **刚体速度**：`v_base = v_pose + ω × r` (`r = p_base - p_pose`)。
4. **协议打包**：

   * 帧头(2B)、数据帧序号(4B)、时间戳(8B)、数据段(72B)、校验(2B)、帧尾(2B)，共90字节。
   * 串口以 100 Hz 速率发送。

---

## 5. 测试结果与观察

* **功能验证**：编译、运行稳定；静止回零，运动平滑；串口帧完整。
* **加速度特性**：T265 IMU 线加速度噪声较大，各轴差异显著，后续可加滤波或融合。
* **控制验证**：反馈数据满足滑模控制器世界系运算需求；机体系角速度/加速度正确。

---

## 6. 后续拓展

* **滤波与融合**：加入低通、卡尔曼滤波或多传感器融合提升精度。
* **多传感器**：集成编码器、其他 IMU 做冗余。
* **性能优化**：简化协议或下移部分计算以降低延迟。
* **多相机**：支持多台 T265 或与其他 SLAM 设备融合。

---

## 7. 结论

本项目完整实现了 T265 → ROS → 串口 → 滑模控制器的数据流，满足验证阶段需求。未来可在滤波、融合和性能优化方面深入完善。
