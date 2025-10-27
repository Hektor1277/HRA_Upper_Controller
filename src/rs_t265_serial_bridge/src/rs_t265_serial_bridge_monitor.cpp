/*********************************************************************
 * rs_t265_serial_bridge_monitor.cpp  (ROS-Noetic, C++17)
 *
 * 构建：
 *   在 rs_t265_serial_bridge/CMakeLists.txt 末尾加入
 *     add_executable(rs_t265_serial_bridge_monitor src/rs_t265_serial_bridge_monitor.cpp)
 *     target_link_libraries(rs_t265_serial_bridge_monitor ${catkin_LIBRARIES} boost_system)
 *
 *   并在 package.xml <exec_depend> 加 <exec_depend>boost</exec_depend>
 *
 * 运行示例：
 *   rosrun rs_t265_serial_bridge rs_t265_serial_bridge_monitor _port:=/dev/pts/2 _baud:=230400
 *********************************************************************/
#include <ros/ros.h>
#include <std_msgs/UInt32.h>
#include <std_msgs/Float32.h>
#include <boost/asio.hpp>
#include <vector>

using boost::asio::io_service;
using boost::asio::serial_port;

namespace
{

  constexpr uint8_t HDR[2] = {0xAA, 0xBB};
  constexpr uint8_t FTR[2] = {0xCC, 0xDD};
  constexpr size_t FRAME_LEN = 90;
  constexpr size_t CRC_BEG = 2;  // inclusive
  constexpr size_t CRC_END = 86; // exclusive

  // --- 16-bit 累加和：输入须为偶数长度 ---
  uint16_t crc16_sum(const uint8_t *data, size_t n)
  {
    uint32_t sum = 0;
    for (size_t i = 0; i < n; i += 2)
      sum += (data[i] << 8) | data[i + 1];
    return static_cast<uint16_t>(sum); // mod 65536
  }

  class BridgeMonitor
  {
  public:
    BridgeMonitor(const std::string &port, uint32_t baud, ros::NodeHandle &nh)
        : io_(), sp_(io_, port),
          ok_cnt_(0), crc_err_(0), lost_pkts_(0),
          prev_seq_(0), has_prev_(false), prev_ns_(0)
    {
      sp_.set_option(serial_port::baud_rate(baud));
      sp_.set_option(serial_port::character_size(8));
      sp_.set_option(serial_port::parity(serial_port::parity::none));
      sp_.set_option(serial_port::stop_bits(serial_port::stop_bits::one));
      sp_.set_option(serial_port::flow_control(serial_port::flow_control::none));

      pub_ok_ = nh.advertise<std_msgs::UInt32>("/bridge_stats/frame_ok", 10);
      pub_crc_ = nh.advertise<std_msgs::UInt32>("/bridge_stats/crc_error", 10);
      pub_gap_ = nh.advertise<std_msgs::UInt32>("/bridge_stats/seq_gap", 10);
      pub_lat_ = nh.advertise<std_msgs::Float32>("/bridge_stats/latency_ms", 10);

      ROS_INFO_STREAM("Serial open " << port << " @ " << baud << "bps");
    }

    void spin()
    {
      ros::Rate idle(1000); // 1 kHz idle loop
      while (ros::ok())
      {
        readSerial();
        idle.sleep();
      }
    }

  private:
    void readSerial()
    {
      uint8_t tmp[256];
      boost::system::error_code ec;
      size_t n = sp_.read_some(boost::asio::buffer(tmp), ec);
      if (ec)
      {
        ROS_WARN_STREAM_THROTTLE(1.0, "Serial read error: " << ec.message());
        return;
      }
      buf_.insert(buf_.end(), tmp, tmp + n);
      parseBuffer();
    }

    void parseBuffer()
    {
      while (buf_.size() >= FRAME_LEN)
      {
        if (buf_[0] != HDR[0] || buf_[1] != HDR[1])
        {
          buf_.erase(buf_.begin());
          continue;
        }
        if (buf_[FRAME_LEN - 2] != FTR[0] || buf_[FRAME_LEN - 1] != FTR[1])
        {
          buf_.erase(buf_.begin());
          continue;
        }

        // 取帧
        uint8_t frame[FRAME_LEN];
        std::copy_n(buf_.begin(), FRAME_LEN, frame);
        buf_.erase(buf_.begin(), buf_.begin() + FRAME_LEN);

        // CRC
        uint16_t crc_calc = crc16_sum(frame + CRC_BEG, CRC_END - CRC_BEG);
        uint16_t crc_rx = (frame[CRC_END] << 8) | frame[CRC_END + 1];
        if (crc_calc != crc_rx)
        {
          ++crc_err_;
          publishUInt(pub_crc_, crc_err_);
          continue;
        }

        // ---- 成功帧 ----
        ++ok_cnt_;
        publishUInt(pub_ok_, ok_cnt_);

        uint32_t seq = 0;
        for (int i = 0; i < 4; ++i)
          seq = (seq << 8) | frame[2 + i];

        uint64_t unix_ns = 0;
        for (int i = 0; i < 8; ++i)
          unix_ns = (unix_ns << 8) | frame[6 + i];

        // latency
        float lat_ms = 0.f;
        uint64_t now_ns = ros::Time::now().toNSec();
        if (unix_ns < now_ns)
          lat_ms = static_cast<float>(now_ns - unix_ns) * 1e-6f;
        publishFloat(pub_lat_, lat_ms);

        // seq gap
        if (has_prev_)
        {
          uint32_t gap = seq - prev_seq_ - 1; // uint32 wrap safe
          if (gap)
          {
            lost_pkts_ += gap;
            publishUInt(pub_gap_, lost_pkts_);
          }
        }
        prev_seq_ = seq;
        prev_ns_ = unix_ns;
        has_prev_ = true;
      }
    }

    void publishUInt(ros::Publisher &p, uint32_t val)
    {
      std_msgs::UInt32 msg;
      msg.data = val;
      p.publish(msg);
    }
    void publishFloat(ros::Publisher &p, float v)
    {
      std_msgs::Float32 msg;
      msg.data = v;
      p.publish(msg);
    }

    // ----- members -----
    io_service io_;
    serial_port sp_;
    std::vector<uint8_t> buf_;

    // stats
    uint32_t ok_cnt_, crc_err_, lost_pkts_;
    uint32_t prev_seq_;
    bool has_prev_;
    uint64_t prev_ns_;

    // ros pub
    ros::Publisher pub_ok_, pub_crc_, pub_gap_, pub_lat_;
  };

} // anonymous namespace

int main(int argc, char **argv)
{
  ros::init(argc, argv, "rs_t265_serial_bridge_monitor");
  ros::NodeHandle nh("~");
  std::string port;
  nh.param<std::string>("port", port, "/dev/pts/2");
  int baud;
  nh.param<int>("baud", baud, 230400);

  try
  {
    BridgeMonitor mon(port, static_cast<uint32_t>(baud), nh);
    mon.spin();
  }
  catch (std::exception &e)
  {
    ROS_FATAL_STREAM("BridgeMonitor exception: " << e.what());
  }
  return 0;
}
