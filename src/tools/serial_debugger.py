#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
               HRA 串口调试工具使用手册 (HRA Serial Debugger Manual)
===============================================================================

[1. 简介]
    这是一个"旁路"工具，用于在不启动 ROS 的情况下，直接通过串口控制下位机。
    它可以发送控制指令，也可以伪造反馈数据，用于测试底层电气连接和电机响应。

[2. 极速上手
    -----------------------------------------------------------------------
    步骤 A: 准备环境 (只需做一次)
        1. 确保已连接 Jetson 和 下位机(STM32) 的串口线。
        2. 打开一个终端窗口 (Ctrl+Alt+T)。
        3. 赋予串口权限:
           $ sudo chmod 777 /dev/ttyTHS0
        4. 安装依赖库:
           $ pip3 install pyserial

    步骤 B: 启动工具
        1. 必须先关闭所有正在运行的 ROS 程序 (如 dashboard 或 bridge 节点)!
           (如果在运行，请在那个窗口按 Ctrl+C 停止)
        2. 运行本脚本:
           $ cd ~/catkin_ws/src/tools/
           $ python3 serial_debugger.py

    步骤 C: 开始输入指令
        看到 "HRA-DBG> " 提示符后，即可输入下方列出的指令。
    -----------------------------------------------------------------------

[3. 指令大全与真实示例]
    (提示: 所有指令均不区分大小写，直接复制示例即可运行)

    -----------------------------------
    3.1 基础控制 (最常用)
    -----------------------------------
    * 设定期望位置 (单位: 米)
      语法: set pos <x> <y> <z>
      示例 (设置高度为 0.5米):
        HRA-DBG> set pos 0 0 0.5

    * 设定期望速度 (单位: 米/秒)
      语法: set vel <vx> <vy> <vz>
      示例 (设置向前速度 0.1m/s):
        HRA-DBG> set vel 0.1 0 0

    * 发送单帧 (设置好数据后，必须输入 send 才会发送!)
      HRA-DBG> send
      (现象: 屏幕显示 "[TX] Frame #1 sent...", 电机可能会动一下)

    * 连续发送 (模拟真实运行, 推荐!)
      语法: loop <频率Hz>
      示例 (以 100Hz 频率持续发送):
        HRA-DBG> loop 100
      (现象: 电机持续转动。想停止时，按键盘上的 Ctrl+C)

    -----------------------------------
    3.2 进阶控制 (混合参数)
    -----------------------------------
    * 一次性设置多个参数
      示例 (同时设置位置和速度):
        HRA-DBG> set pos 1 0 0.5 vel 0.2 0 0

    * 设置期望姿态 (单位: 弧度)
      示例 (设置 Roll=0.1弧度):
        HRA-DBG> set ang 0.1 0 0

    -----------------------------------
    3.3 反馈伪造 (用于测试下位机逻辑)
    -----------------------------------
    * 告诉下位机"我现在在这个位置" (伪造传感器反馈)
      语法: set actual pos <x> <y> <z>
      示例 (伪造当前在 0.9米 高度):
        HRA-DBG> set actual pos 0 0 0.9

    -----------------------------------
    3.4 快捷指令与重置
    -----------------------------------
    * 一键起飞测试 (Z=1.0米)
        HRA-DBG> set fan 1

    * 重置所有数据为 0
        HRA-DBG> reset

    * 退出工具
        HRA-DBG> q

    -----------------------------------
    3.5 专家模式 (直接发十六进制)
    -----------------------------------
    * 发送原始字节 (用于测试协议健壮性)
      示例 (发送AA BB和一些随机数):
        HRA-DBG> raw AA BB 01 02 03 04

[4. 典型测试流程]
    场景: 想测试电机能不能转
    1. 输入: set fan 1   (设定起飞指令)
    2. 输入: send        (发送一次，听听有没有声音)
    3. 输入: loop 50     (持续发送，观察电机转速是否稳定)
    4. 按 Ctrl+C 停止
    5. 输入: reset       (归零)
    6. 输入: send        (发送归零指令，电机应停转)

===============================================================================
"""
# (后续 Imports 和代码保持不变)

import serial
import struct
import time
import sys
import threading

# ================= 配置区 =================
SERIAL_PORT = '/dev/ttyTHS0'  
BAUD_RATE = 230400
# =========================================

class HraFrameBuilder:
    def __init__(self):
        # 18 float values for Desire: Pos(3), Vel(3), Acc(3), Ang(3), AngVel(3), AngAcc(3)
        self.desire = [0.0] * 18
        # 18 float values for Actual
        self.actual = [0.0] * 18
        self.seq = 0

    def reset(self):
        self.desire = [0.0] * 18
        self.actual = [0.0] * 18
        print(" [INFO] All states reset to 0.0")

    def _get_offset(self, key):
        # Map keyword to index offset (0-15)
        key = key.lower()
        if key == 'pos': return 0
        if key == 'vel': return 3
        if key == 'acc': return 6
        if key == 'ang': return 9
        if key in ['ang_vel', 'angvel']: return 12
        if key in ['ang_acc', 'angacc']: return 15
        return -1

    def parse_set_cmd(self, args):
        # args example: ['pos', '1', '2', '3', 'vel', '0.1', '0', '0']
        # or: ['actual', 'pos', '1', '2', '3']
        
        target_buffer = self.desire # Default target
        idx = 0
        
        # Check if first arg is 'actual'
        if args and args[0].lower() == 'actual':
            target_buffer = self.actual
            idx = 1 # Skip 'actual' keyword
            print(" [MODE] Setting ACTUAL (Feedback) State...")
        
        while idx < len(args):
            key = args[idx]
            offset = self._get_offset(key)
            
            if offset == -1:
                print(f" [ERR] Unknown keyword: {key}")
                return

            if idx + 3 >= len(args):
                print(f" [ERR] Not enough values for {key} (needs 3: x y z)")
                return

            try:
                x = float(args[idx+1])
                y = float(args[idx+2])
                z = float(args[idx+3])
                
                target_buffer[offset]   = x
                target_buffer[offset+1] = y
                target_buffer[offset+2] = z
                
                print(f"   -> Set {key.upper()}: [{x}, {y}, {z}]")
                idx += 4 # Move to next keyword
            except ValueError:
                print(f" [ERR] Invalid number format after {key}")
                return

    def build_bytes(self):
        self.seq += 1
        # 1. Header
        frame = bytearray([0xAA, 0xBB])
        # 2. Seq
        frame.extend(struct.pack('>I', self.seq))
        # 3. Timestamp
        ts = int(time.time() * 1e9)
        frame.extend(struct.pack('>Q', ts))
        
        # 4. Payload (Desire + Actual) = 36 int16
        payload_floats = self.desire + self.actual
        payload_bytes = bytearray()
        
        for val in payload_floats:
            int_val = int(val * 1000.0)
            int_val = max(-32768, min(32767, int_val))
            payload_bytes.extend(struct.pack('>h', int_val))
            
        frame.extend(payload_bytes)
        
        # 5. CRC
        crc = 0
        for i in range(0, len(payload_bytes), 2):
            val = (payload_bytes[i] << 8) | payload_bytes[i+1]
            crc = (crc + val) & 0xFFFF
        frame.extend(struct.pack('>H', crc))
        
        # 6. Tail
        frame.extend(bytearray([0xCC, 0xDD]))
        return frame

def main():
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
        print(f"[INFO] Port {SERIAL_PORT} @ {BAUD_RATE} OPEN.")
    except Exception as e:
        print(f"[ERROR] Serial Open Failed: {e}")
        return

    builder = HraFrameBuilder()

    while True:
        try:
            line = input("HRA-DBG> ").strip()
        except EOFError:
            break
            
        if not line: continue
        parts = line.split()
        cmd = parts[0].lower()

        if cmd in ['q', 'quit', 'exit']:
            break

        elif cmd == 'reset':
            builder.reset()

        elif cmd == 'set':
            # Handle special shortcut: set fan 1
            if len(parts) == 3 and parts[1] == 'fan' and parts[2] == '1':
                builder.reset()
                builder.desire[2] = 1.0 # Z=1.0
                print(" [OK] Preset: Takeoff (Z=1.0)")
            else:
                builder.parse_set_cmd(parts[1:])

        elif cmd == 'send':
            data = builder.build_bytes()
            ser.write(data)
            print(f" [TX] Frame #{builder.seq} sent ({len(data)} bytes).")

        elif cmd == 'loop':
            freq = 100.0
            if len(parts) > 1:
                try:
                    freq = float(parts[1])
                except: pass
            
            delay = 1.0 / freq
            print(f" [INFO] Streaming at {freq}Hz. Press Ctrl+C to stop.")
            try:
                while True:
                    data = builder.build_bytes()
                    ser.write(data)
                    time.sleep(delay)
            except KeyboardInterrupt:
                print("\n [INFO] Stopped.")

        elif cmd == 'raw':
            # Syntax: raw AA BB 01 02 ...
            hex_str = "".join(parts[1:])
            try:
                raw_bytes = bytearray.fromhex(hex_str)
                ser.write(raw_bytes)
                print(f" [TX-RAW] Sent {len(raw_bytes)} bytes: {raw_bytes.hex().upper()}")
            except ValueError:
                print(" [ERR] Invalid Hex String")

        else:
            print(" [?] Unknown command. Try: set, send, loop, raw, reset, q")

    ser.close()

if __name__ == '__main__':
    main()