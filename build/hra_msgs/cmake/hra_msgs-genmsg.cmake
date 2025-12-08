# generated from genmsg/cmake/pkg-genmsg.cmake.em

message(STATUS "hra_msgs: 8 messages, 0 services")

set(MSG_I_FLAGS "-Ihra_msgs:/home/hra/catkin_ws/src/hra_msgs/msg;-Ihra_msgs:/home/hra/catkin_ws/build/devel/share/hra_msgs/msg;-Istd_msgs:/opt/ros/noetic/share/std_msgs/cmake/../msg;-Igeometry_msgs:/opt/ros/noetic/share/geometry_msgs/cmake/../msg;-Iactionlib_msgs:/opt/ros/noetic/share/actionlib_msgs/cmake/../msg")

# Find all generators
find_package(gencpp REQUIRED)
find_package(geneus REQUIRED)
find_package(genlisp REQUIRED)
find_package(gennodejs REQUIRED)
find_package(genpy REQUIRED)

add_custom_target(hra_msgs_generate_messages ALL)

# verify that message/service dependencies have not changed since configure



get_filename_component(_filename "/home/hra/catkin_ws/src/hra_msgs/msg/TrajectoryPoint.msg" NAME_WE)
add_custom_target(_hra_msgs_generate_messages_check_deps_${_filename}
  COMMAND ${CATKIN_ENV} ${PYTHON_EXECUTABLE} ${GENMSG_CHECK_DEPS_SCRIPT} "hra_msgs" "/home/hra/catkin_ws/src/hra_msgs/msg/TrajectoryPoint.msg" "geometry_msgs/Accel:geometry_msgs/Quaternion:geometry_msgs/Pose:geometry_msgs/Twist:geometry_msgs/Point:geometry_msgs/Vector3"
)

get_filename_component(_filename "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryAction.msg" NAME_WE)
add_custom_target(_hra_msgs_generate_messages_check_deps_${_filename}
  COMMAND ${CATKIN_ENV} ${PYTHON_EXECUTABLE} ${GENMSG_CHECK_DEPS_SCRIPT} "hra_msgs" "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryAction.msg" "geometry_msgs/Accel:hra_msgs/ExecuteTrajectoryActionGoal:geometry_msgs/Quaternion:geometry_msgs/Pose:std_msgs/Header:actionlib_msgs/GoalStatus:hra_msgs/ExecuteTrajectoryResult:hra_msgs/ExecuteTrajectoryActionFeedback:hra_msgs/TrajectoryPoint:geometry_msgs/Point:geometry_msgs/Twist:hra_msgs/ExecuteTrajectoryActionResult:geometry_msgs/Vector3:actionlib_msgs/GoalID:hra_msgs/ExecuteTrajectoryFeedback:hra_msgs/ExecuteTrajectoryGoal"
)

get_filename_component(_filename "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryActionGoal.msg" NAME_WE)
add_custom_target(_hra_msgs_generate_messages_check_deps_${_filename}
  COMMAND ${CATKIN_ENV} ${PYTHON_EXECUTABLE} ${GENMSG_CHECK_DEPS_SCRIPT} "hra_msgs" "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryActionGoal.msg" "geometry_msgs/Quaternion:geometry_msgs/Pose:std_msgs/Header:geometry_msgs/Point:actionlib_msgs/GoalID:hra_msgs/ExecuteTrajectoryGoal"
)

get_filename_component(_filename "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryActionResult.msg" NAME_WE)
add_custom_target(_hra_msgs_generate_messages_check_deps_${_filename}
  COMMAND ${CATKIN_ENV} ${PYTHON_EXECUTABLE} ${GENMSG_CHECK_DEPS_SCRIPT} "hra_msgs" "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryActionResult.msg" "std_msgs/Header:actionlib_msgs/GoalStatus:actionlib_msgs/GoalID:hra_msgs/ExecuteTrajectoryResult"
)

get_filename_component(_filename "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryActionFeedback.msg" NAME_WE)
add_custom_target(_hra_msgs_generate_messages_check_deps_${_filename}
  COMMAND ${CATKIN_ENV} ${PYTHON_EXECUTABLE} ${GENMSG_CHECK_DEPS_SCRIPT} "hra_msgs" "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryActionFeedback.msg" "geometry_msgs/Accel:geometry_msgs/Quaternion:geometry_msgs/Pose:std_msgs/Header:actionlib_msgs/GoalStatus:hra_msgs/TrajectoryPoint:geometry_msgs/Point:geometry_msgs/Twist:geometry_msgs/Vector3:actionlib_msgs/GoalID:hra_msgs/ExecuteTrajectoryFeedback"
)

get_filename_component(_filename "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryGoal.msg" NAME_WE)
add_custom_target(_hra_msgs_generate_messages_check_deps_${_filename}
  COMMAND ${CATKIN_ENV} ${PYTHON_EXECUTABLE} ${GENMSG_CHECK_DEPS_SCRIPT} "hra_msgs" "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryGoal.msg" "geometry_msgs/Quaternion:geometry_msgs/Point:geometry_msgs/Pose"
)

get_filename_component(_filename "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryResult.msg" NAME_WE)
add_custom_target(_hra_msgs_generate_messages_check_deps_${_filename}
  COMMAND ${CATKIN_ENV} ${PYTHON_EXECUTABLE} ${GENMSG_CHECK_DEPS_SCRIPT} "hra_msgs" "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryResult.msg" ""
)

get_filename_component(_filename "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryFeedback.msg" NAME_WE)
add_custom_target(_hra_msgs_generate_messages_check_deps_${_filename}
  COMMAND ${CATKIN_ENV} ${PYTHON_EXECUTABLE} ${GENMSG_CHECK_DEPS_SCRIPT} "hra_msgs" "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryFeedback.msg" "geometry_msgs/Accel:geometry_msgs/Quaternion:geometry_msgs/Pose:hra_msgs/TrajectoryPoint:geometry_msgs/Twist:geometry_msgs/Point:geometry_msgs/Vector3"
)

#
#  langs = gencpp;geneus;genlisp;gennodejs;genpy
#

### Section generating for lang: gencpp
### Generating Messages
_generate_msg_cpp(hra_msgs
  "/home/hra/catkin_ws/src/hra_msgs/msg/TrajectoryPoint.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Accel.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Quaternion.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Pose.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Twist.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Point.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Vector3.msg"
  ${CATKIN_DEVEL_PREFIX}/${gencpp_INSTALL_DIR}/hra_msgs
)
_generate_msg_cpp(hra_msgs
  "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryAction.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Accel.msg;/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryActionGoal.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Quaternion.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Pose.msg;/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg;/opt/ros/noetic/share/actionlib_msgs/cmake/../msg/GoalStatus.msg;/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryResult.msg;/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryActionFeedback.msg;/home/hra/catkin_ws/src/hra_msgs/msg/TrajectoryPoint.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Point.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Twist.msg;/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryActionResult.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Vector3.msg;/opt/ros/noetic/share/actionlib_msgs/cmake/../msg/GoalID.msg;/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryFeedback.msg;/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryGoal.msg"
  ${CATKIN_DEVEL_PREFIX}/${gencpp_INSTALL_DIR}/hra_msgs
)
_generate_msg_cpp(hra_msgs
  "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryActionGoal.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Quaternion.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Pose.msg;/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Point.msg;/opt/ros/noetic/share/actionlib_msgs/cmake/../msg/GoalID.msg;/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryGoal.msg"
  ${CATKIN_DEVEL_PREFIX}/${gencpp_INSTALL_DIR}/hra_msgs
)
_generate_msg_cpp(hra_msgs
  "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryActionResult.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg;/opt/ros/noetic/share/actionlib_msgs/cmake/../msg/GoalStatus.msg;/opt/ros/noetic/share/actionlib_msgs/cmake/../msg/GoalID.msg;/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryResult.msg"
  ${CATKIN_DEVEL_PREFIX}/${gencpp_INSTALL_DIR}/hra_msgs
)
_generate_msg_cpp(hra_msgs
  "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryActionFeedback.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Accel.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Quaternion.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Pose.msg;/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg;/opt/ros/noetic/share/actionlib_msgs/cmake/../msg/GoalStatus.msg;/home/hra/catkin_ws/src/hra_msgs/msg/TrajectoryPoint.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Point.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Twist.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Vector3.msg;/opt/ros/noetic/share/actionlib_msgs/cmake/../msg/GoalID.msg;/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryFeedback.msg"
  ${CATKIN_DEVEL_PREFIX}/${gencpp_INSTALL_DIR}/hra_msgs
)
_generate_msg_cpp(hra_msgs
  "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryGoal.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Quaternion.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Point.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Pose.msg"
  ${CATKIN_DEVEL_PREFIX}/${gencpp_INSTALL_DIR}/hra_msgs
)
_generate_msg_cpp(hra_msgs
  "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryResult.msg"
  "${MSG_I_FLAGS}"
  ""
  ${CATKIN_DEVEL_PREFIX}/${gencpp_INSTALL_DIR}/hra_msgs
)
_generate_msg_cpp(hra_msgs
  "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryFeedback.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Accel.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Quaternion.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Pose.msg;/home/hra/catkin_ws/src/hra_msgs/msg/TrajectoryPoint.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Twist.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Point.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Vector3.msg"
  ${CATKIN_DEVEL_PREFIX}/${gencpp_INSTALL_DIR}/hra_msgs
)

### Generating Services

### Generating Module File
_generate_module_cpp(hra_msgs
  ${CATKIN_DEVEL_PREFIX}/${gencpp_INSTALL_DIR}/hra_msgs
  "${ALL_GEN_OUTPUT_FILES_cpp}"
)

add_custom_target(hra_msgs_generate_messages_cpp
  DEPENDS ${ALL_GEN_OUTPUT_FILES_cpp}
)
add_dependencies(hra_msgs_generate_messages hra_msgs_generate_messages_cpp)

# add dependencies to all check dependencies targets
get_filename_component(_filename "/home/hra/catkin_ws/src/hra_msgs/msg/TrajectoryPoint.msg" NAME_WE)
add_dependencies(hra_msgs_generate_messages_cpp _hra_msgs_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryAction.msg" NAME_WE)
add_dependencies(hra_msgs_generate_messages_cpp _hra_msgs_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryActionGoal.msg" NAME_WE)
add_dependencies(hra_msgs_generate_messages_cpp _hra_msgs_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryActionResult.msg" NAME_WE)
add_dependencies(hra_msgs_generate_messages_cpp _hra_msgs_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryActionFeedback.msg" NAME_WE)
add_dependencies(hra_msgs_generate_messages_cpp _hra_msgs_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryGoal.msg" NAME_WE)
add_dependencies(hra_msgs_generate_messages_cpp _hra_msgs_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryResult.msg" NAME_WE)
add_dependencies(hra_msgs_generate_messages_cpp _hra_msgs_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryFeedback.msg" NAME_WE)
add_dependencies(hra_msgs_generate_messages_cpp _hra_msgs_generate_messages_check_deps_${_filename})

# target for backward compatibility
add_custom_target(hra_msgs_gencpp)
add_dependencies(hra_msgs_gencpp hra_msgs_generate_messages_cpp)

# register target for catkin_package(EXPORTED_TARGETS)
list(APPEND ${PROJECT_NAME}_EXPORTED_TARGETS hra_msgs_generate_messages_cpp)

### Section generating for lang: geneus
### Generating Messages
_generate_msg_eus(hra_msgs
  "/home/hra/catkin_ws/src/hra_msgs/msg/TrajectoryPoint.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Accel.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Quaternion.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Pose.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Twist.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Point.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Vector3.msg"
  ${CATKIN_DEVEL_PREFIX}/${geneus_INSTALL_DIR}/hra_msgs
)
_generate_msg_eus(hra_msgs
  "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryAction.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Accel.msg;/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryActionGoal.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Quaternion.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Pose.msg;/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg;/opt/ros/noetic/share/actionlib_msgs/cmake/../msg/GoalStatus.msg;/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryResult.msg;/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryActionFeedback.msg;/home/hra/catkin_ws/src/hra_msgs/msg/TrajectoryPoint.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Point.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Twist.msg;/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryActionResult.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Vector3.msg;/opt/ros/noetic/share/actionlib_msgs/cmake/../msg/GoalID.msg;/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryFeedback.msg;/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryGoal.msg"
  ${CATKIN_DEVEL_PREFIX}/${geneus_INSTALL_DIR}/hra_msgs
)
_generate_msg_eus(hra_msgs
  "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryActionGoal.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Quaternion.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Pose.msg;/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Point.msg;/opt/ros/noetic/share/actionlib_msgs/cmake/../msg/GoalID.msg;/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryGoal.msg"
  ${CATKIN_DEVEL_PREFIX}/${geneus_INSTALL_DIR}/hra_msgs
)
_generate_msg_eus(hra_msgs
  "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryActionResult.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg;/opt/ros/noetic/share/actionlib_msgs/cmake/../msg/GoalStatus.msg;/opt/ros/noetic/share/actionlib_msgs/cmake/../msg/GoalID.msg;/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryResult.msg"
  ${CATKIN_DEVEL_PREFIX}/${geneus_INSTALL_DIR}/hra_msgs
)
_generate_msg_eus(hra_msgs
  "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryActionFeedback.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Accel.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Quaternion.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Pose.msg;/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg;/opt/ros/noetic/share/actionlib_msgs/cmake/../msg/GoalStatus.msg;/home/hra/catkin_ws/src/hra_msgs/msg/TrajectoryPoint.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Point.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Twist.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Vector3.msg;/opt/ros/noetic/share/actionlib_msgs/cmake/../msg/GoalID.msg;/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryFeedback.msg"
  ${CATKIN_DEVEL_PREFIX}/${geneus_INSTALL_DIR}/hra_msgs
)
_generate_msg_eus(hra_msgs
  "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryGoal.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Quaternion.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Point.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Pose.msg"
  ${CATKIN_DEVEL_PREFIX}/${geneus_INSTALL_DIR}/hra_msgs
)
_generate_msg_eus(hra_msgs
  "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryResult.msg"
  "${MSG_I_FLAGS}"
  ""
  ${CATKIN_DEVEL_PREFIX}/${geneus_INSTALL_DIR}/hra_msgs
)
_generate_msg_eus(hra_msgs
  "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryFeedback.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Accel.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Quaternion.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Pose.msg;/home/hra/catkin_ws/src/hra_msgs/msg/TrajectoryPoint.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Twist.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Point.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Vector3.msg"
  ${CATKIN_DEVEL_PREFIX}/${geneus_INSTALL_DIR}/hra_msgs
)

### Generating Services

### Generating Module File
_generate_module_eus(hra_msgs
  ${CATKIN_DEVEL_PREFIX}/${geneus_INSTALL_DIR}/hra_msgs
  "${ALL_GEN_OUTPUT_FILES_eus}"
)

add_custom_target(hra_msgs_generate_messages_eus
  DEPENDS ${ALL_GEN_OUTPUT_FILES_eus}
)
add_dependencies(hra_msgs_generate_messages hra_msgs_generate_messages_eus)

# add dependencies to all check dependencies targets
get_filename_component(_filename "/home/hra/catkin_ws/src/hra_msgs/msg/TrajectoryPoint.msg" NAME_WE)
add_dependencies(hra_msgs_generate_messages_eus _hra_msgs_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryAction.msg" NAME_WE)
add_dependencies(hra_msgs_generate_messages_eus _hra_msgs_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryActionGoal.msg" NAME_WE)
add_dependencies(hra_msgs_generate_messages_eus _hra_msgs_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryActionResult.msg" NAME_WE)
add_dependencies(hra_msgs_generate_messages_eus _hra_msgs_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryActionFeedback.msg" NAME_WE)
add_dependencies(hra_msgs_generate_messages_eus _hra_msgs_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryGoal.msg" NAME_WE)
add_dependencies(hra_msgs_generate_messages_eus _hra_msgs_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryResult.msg" NAME_WE)
add_dependencies(hra_msgs_generate_messages_eus _hra_msgs_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryFeedback.msg" NAME_WE)
add_dependencies(hra_msgs_generate_messages_eus _hra_msgs_generate_messages_check_deps_${_filename})

# target for backward compatibility
add_custom_target(hra_msgs_geneus)
add_dependencies(hra_msgs_geneus hra_msgs_generate_messages_eus)

# register target for catkin_package(EXPORTED_TARGETS)
list(APPEND ${PROJECT_NAME}_EXPORTED_TARGETS hra_msgs_generate_messages_eus)

### Section generating for lang: genlisp
### Generating Messages
_generate_msg_lisp(hra_msgs
  "/home/hra/catkin_ws/src/hra_msgs/msg/TrajectoryPoint.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Accel.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Quaternion.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Pose.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Twist.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Point.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Vector3.msg"
  ${CATKIN_DEVEL_PREFIX}/${genlisp_INSTALL_DIR}/hra_msgs
)
_generate_msg_lisp(hra_msgs
  "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryAction.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Accel.msg;/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryActionGoal.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Quaternion.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Pose.msg;/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg;/opt/ros/noetic/share/actionlib_msgs/cmake/../msg/GoalStatus.msg;/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryResult.msg;/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryActionFeedback.msg;/home/hra/catkin_ws/src/hra_msgs/msg/TrajectoryPoint.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Point.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Twist.msg;/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryActionResult.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Vector3.msg;/opt/ros/noetic/share/actionlib_msgs/cmake/../msg/GoalID.msg;/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryFeedback.msg;/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryGoal.msg"
  ${CATKIN_DEVEL_PREFIX}/${genlisp_INSTALL_DIR}/hra_msgs
)
_generate_msg_lisp(hra_msgs
  "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryActionGoal.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Quaternion.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Pose.msg;/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Point.msg;/opt/ros/noetic/share/actionlib_msgs/cmake/../msg/GoalID.msg;/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryGoal.msg"
  ${CATKIN_DEVEL_PREFIX}/${genlisp_INSTALL_DIR}/hra_msgs
)
_generate_msg_lisp(hra_msgs
  "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryActionResult.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg;/opt/ros/noetic/share/actionlib_msgs/cmake/../msg/GoalStatus.msg;/opt/ros/noetic/share/actionlib_msgs/cmake/../msg/GoalID.msg;/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryResult.msg"
  ${CATKIN_DEVEL_PREFIX}/${genlisp_INSTALL_DIR}/hra_msgs
)
_generate_msg_lisp(hra_msgs
  "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryActionFeedback.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Accel.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Quaternion.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Pose.msg;/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg;/opt/ros/noetic/share/actionlib_msgs/cmake/../msg/GoalStatus.msg;/home/hra/catkin_ws/src/hra_msgs/msg/TrajectoryPoint.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Point.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Twist.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Vector3.msg;/opt/ros/noetic/share/actionlib_msgs/cmake/../msg/GoalID.msg;/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryFeedback.msg"
  ${CATKIN_DEVEL_PREFIX}/${genlisp_INSTALL_DIR}/hra_msgs
)
_generate_msg_lisp(hra_msgs
  "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryGoal.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Quaternion.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Point.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Pose.msg"
  ${CATKIN_DEVEL_PREFIX}/${genlisp_INSTALL_DIR}/hra_msgs
)
_generate_msg_lisp(hra_msgs
  "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryResult.msg"
  "${MSG_I_FLAGS}"
  ""
  ${CATKIN_DEVEL_PREFIX}/${genlisp_INSTALL_DIR}/hra_msgs
)
_generate_msg_lisp(hra_msgs
  "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryFeedback.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Accel.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Quaternion.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Pose.msg;/home/hra/catkin_ws/src/hra_msgs/msg/TrajectoryPoint.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Twist.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Point.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Vector3.msg"
  ${CATKIN_DEVEL_PREFIX}/${genlisp_INSTALL_DIR}/hra_msgs
)

### Generating Services

### Generating Module File
_generate_module_lisp(hra_msgs
  ${CATKIN_DEVEL_PREFIX}/${genlisp_INSTALL_DIR}/hra_msgs
  "${ALL_GEN_OUTPUT_FILES_lisp}"
)

add_custom_target(hra_msgs_generate_messages_lisp
  DEPENDS ${ALL_GEN_OUTPUT_FILES_lisp}
)
add_dependencies(hra_msgs_generate_messages hra_msgs_generate_messages_lisp)

# add dependencies to all check dependencies targets
get_filename_component(_filename "/home/hra/catkin_ws/src/hra_msgs/msg/TrajectoryPoint.msg" NAME_WE)
add_dependencies(hra_msgs_generate_messages_lisp _hra_msgs_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryAction.msg" NAME_WE)
add_dependencies(hra_msgs_generate_messages_lisp _hra_msgs_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryActionGoal.msg" NAME_WE)
add_dependencies(hra_msgs_generate_messages_lisp _hra_msgs_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryActionResult.msg" NAME_WE)
add_dependencies(hra_msgs_generate_messages_lisp _hra_msgs_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryActionFeedback.msg" NAME_WE)
add_dependencies(hra_msgs_generate_messages_lisp _hra_msgs_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryGoal.msg" NAME_WE)
add_dependencies(hra_msgs_generate_messages_lisp _hra_msgs_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryResult.msg" NAME_WE)
add_dependencies(hra_msgs_generate_messages_lisp _hra_msgs_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryFeedback.msg" NAME_WE)
add_dependencies(hra_msgs_generate_messages_lisp _hra_msgs_generate_messages_check_deps_${_filename})

# target for backward compatibility
add_custom_target(hra_msgs_genlisp)
add_dependencies(hra_msgs_genlisp hra_msgs_generate_messages_lisp)

# register target for catkin_package(EXPORTED_TARGETS)
list(APPEND ${PROJECT_NAME}_EXPORTED_TARGETS hra_msgs_generate_messages_lisp)

### Section generating for lang: gennodejs
### Generating Messages
_generate_msg_nodejs(hra_msgs
  "/home/hra/catkin_ws/src/hra_msgs/msg/TrajectoryPoint.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Accel.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Quaternion.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Pose.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Twist.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Point.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Vector3.msg"
  ${CATKIN_DEVEL_PREFIX}/${gennodejs_INSTALL_DIR}/hra_msgs
)
_generate_msg_nodejs(hra_msgs
  "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryAction.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Accel.msg;/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryActionGoal.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Quaternion.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Pose.msg;/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg;/opt/ros/noetic/share/actionlib_msgs/cmake/../msg/GoalStatus.msg;/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryResult.msg;/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryActionFeedback.msg;/home/hra/catkin_ws/src/hra_msgs/msg/TrajectoryPoint.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Point.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Twist.msg;/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryActionResult.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Vector3.msg;/opt/ros/noetic/share/actionlib_msgs/cmake/../msg/GoalID.msg;/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryFeedback.msg;/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryGoal.msg"
  ${CATKIN_DEVEL_PREFIX}/${gennodejs_INSTALL_DIR}/hra_msgs
)
_generate_msg_nodejs(hra_msgs
  "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryActionGoal.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Quaternion.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Pose.msg;/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Point.msg;/opt/ros/noetic/share/actionlib_msgs/cmake/../msg/GoalID.msg;/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryGoal.msg"
  ${CATKIN_DEVEL_PREFIX}/${gennodejs_INSTALL_DIR}/hra_msgs
)
_generate_msg_nodejs(hra_msgs
  "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryActionResult.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg;/opt/ros/noetic/share/actionlib_msgs/cmake/../msg/GoalStatus.msg;/opt/ros/noetic/share/actionlib_msgs/cmake/../msg/GoalID.msg;/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryResult.msg"
  ${CATKIN_DEVEL_PREFIX}/${gennodejs_INSTALL_DIR}/hra_msgs
)
_generate_msg_nodejs(hra_msgs
  "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryActionFeedback.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Accel.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Quaternion.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Pose.msg;/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg;/opt/ros/noetic/share/actionlib_msgs/cmake/../msg/GoalStatus.msg;/home/hra/catkin_ws/src/hra_msgs/msg/TrajectoryPoint.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Point.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Twist.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Vector3.msg;/opt/ros/noetic/share/actionlib_msgs/cmake/../msg/GoalID.msg;/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryFeedback.msg"
  ${CATKIN_DEVEL_PREFIX}/${gennodejs_INSTALL_DIR}/hra_msgs
)
_generate_msg_nodejs(hra_msgs
  "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryGoal.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Quaternion.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Point.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Pose.msg"
  ${CATKIN_DEVEL_PREFIX}/${gennodejs_INSTALL_DIR}/hra_msgs
)
_generate_msg_nodejs(hra_msgs
  "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryResult.msg"
  "${MSG_I_FLAGS}"
  ""
  ${CATKIN_DEVEL_PREFIX}/${gennodejs_INSTALL_DIR}/hra_msgs
)
_generate_msg_nodejs(hra_msgs
  "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryFeedback.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Accel.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Quaternion.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Pose.msg;/home/hra/catkin_ws/src/hra_msgs/msg/TrajectoryPoint.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Twist.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Point.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Vector3.msg"
  ${CATKIN_DEVEL_PREFIX}/${gennodejs_INSTALL_DIR}/hra_msgs
)

### Generating Services

### Generating Module File
_generate_module_nodejs(hra_msgs
  ${CATKIN_DEVEL_PREFIX}/${gennodejs_INSTALL_DIR}/hra_msgs
  "${ALL_GEN_OUTPUT_FILES_nodejs}"
)

add_custom_target(hra_msgs_generate_messages_nodejs
  DEPENDS ${ALL_GEN_OUTPUT_FILES_nodejs}
)
add_dependencies(hra_msgs_generate_messages hra_msgs_generate_messages_nodejs)

# add dependencies to all check dependencies targets
get_filename_component(_filename "/home/hra/catkin_ws/src/hra_msgs/msg/TrajectoryPoint.msg" NAME_WE)
add_dependencies(hra_msgs_generate_messages_nodejs _hra_msgs_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryAction.msg" NAME_WE)
add_dependencies(hra_msgs_generate_messages_nodejs _hra_msgs_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryActionGoal.msg" NAME_WE)
add_dependencies(hra_msgs_generate_messages_nodejs _hra_msgs_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryActionResult.msg" NAME_WE)
add_dependencies(hra_msgs_generate_messages_nodejs _hra_msgs_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryActionFeedback.msg" NAME_WE)
add_dependencies(hra_msgs_generate_messages_nodejs _hra_msgs_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryGoal.msg" NAME_WE)
add_dependencies(hra_msgs_generate_messages_nodejs _hra_msgs_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryResult.msg" NAME_WE)
add_dependencies(hra_msgs_generate_messages_nodejs _hra_msgs_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryFeedback.msg" NAME_WE)
add_dependencies(hra_msgs_generate_messages_nodejs _hra_msgs_generate_messages_check_deps_${_filename})

# target for backward compatibility
add_custom_target(hra_msgs_gennodejs)
add_dependencies(hra_msgs_gennodejs hra_msgs_generate_messages_nodejs)

# register target for catkin_package(EXPORTED_TARGETS)
list(APPEND ${PROJECT_NAME}_EXPORTED_TARGETS hra_msgs_generate_messages_nodejs)

### Section generating for lang: genpy
### Generating Messages
_generate_msg_py(hra_msgs
  "/home/hra/catkin_ws/src/hra_msgs/msg/TrajectoryPoint.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Accel.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Quaternion.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Pose.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Twist.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Point.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Vector3.msg"
  ${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/hra_msgs
)
_generate_msg_py(hra_msgs
  "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryAction.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Accel.msg;/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryActionGoal.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Quaternion.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Pose.msg;/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg;/opt/ros/noetic/share/actionlib_msgs/cmake/../msg/GoalStatus.msg;/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryResult.msg;/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryActionFeedback.msg;/home/hra/catkin_ws/src/hra_msgs/msg/TrajectoryPoint.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Point.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Twist.msg;/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryActionResult.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Vector3.msg;/opt/ros/noetic/share/actionlib_msgs/cmake/../msg/GoalID.msg;/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryFeedback.msg;/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryGoal.msg"
  ${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/hra_msgs
)
_generate_msg_py(hra_msgs
  "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryActionGoal.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Quaternion.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Pose.msg;/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Point.msg;/opt/ros/noetic/share/actionlib_msgs/cmake/../msg/GoalID.msg;/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryGoal.msg"
  ${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/hra_msgs
)
_generate_msg_py(hra_msgs
  "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryActionResult.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg;/opt/ros/noetic/share/actionlib_msgs/cmake/../msg/GoalStatus.msg;/opt/ros/noetic/share/actionlib_msgs/cmake/../msg/GoalID.msg;/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryResult.msg"
  ${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/hra_msgs
)
_generate_msg_py(hra_msgs
  "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryActionFeedback.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Accel.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Quaternion.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Pose.msg;/opt/ros/noetic/share/std_msgs/cmake/../msg/Header.msg;/opt/ros/noetic/share/actionlib_msgs/cmake/../msg/GoalStatus.msg;/home/hra/catkin_ws/src/hra_msgs/msg/TrajectoryPoint.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Point.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Twist.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Vector3.msg;/opt/ros/noetic/share/actionlib_msgs/cmake/../msg/GoalID.msg;/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryFeedback.msg"
  ${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/hra_msgs
)
_generate_msg_py(hra_msgs
  "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryGoal.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Quaternion.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Point.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Pose.msg"
  ${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/hra_msgs
)
_generate_msg_py(hra_msgs
  "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryResult.msg"
  "${MSG_I_FLAGS}"
  ""
  ${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/hra_msgs
)
_generate_msg_py(hra_msgs
  "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryFeedback.msg"
  "${MSG_I_FLAGS}"
  "/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Accel.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Quaternion.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Pose.msg;/home/hra/catkin_ws/src/hra_msgs/msg/TrajectoryPoint.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Twist.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Point.msg;/opt/ros/noetic/share/geometry_msgs/cmake/../msg/Vector3.msg"
  ${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/hra_msgs
)

### Generating Services

### Generating Module File
_generate_module_py(hra_msgs
  ${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/hra_msgs
  "${ALL_GEN_OUTPUT_FILES_py}"
)

add_custom_target(hra_msgs_generate_messages_py
  DEPENDS ${ALL_GEN_OUTPUT_FILES_py}
)
add_dependencies(hra_msgs_generate_messages hra_msgs_generate_messages_py)

# add dependencies to all check dependencies targets
get_filename_component(_filename "/home/hra/catkin_ws/src/hra_msgs/msg/TrajectoryPoint.msg" NAME_WE)
add_dependencies(hra_msgs_generate_messages_py _hra_msgs_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryAction.msg" NAME_WE)
add_dependencies(hra_msgs_generate_messages_py _hra_msgs_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryActionGoal.msg" NAME_WE)
add_dependencies(hra_msgs_generate_messages_py _hra_msgs_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryActionResult.msg" NAME_WE)
add_dependencies(hra_msgs_generate_messages_py _hra_msgs_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryActionFeedback.msg" NAME_WE)
add_dependencies(hra_msgs_generate_messages_py _hra_msgs_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryGoal.msg" NAME_WE)
add_dependencies(hra_msgs_generate_messages_py _hra_msgs_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryResult.msg" NAME_WE)
add_dependencies(hra_msgs_generate_messages_py _hra_msgs_generate_messages_check_deps_${_filename})
get_filename_component(_filename "/home/hra/catkin_ws/build/devel/share/hra_msgs/msg/ExecuteTrajectoryFeedback.msg" NAME_WE)
add_dependencies(hra_msgs_generate_messages_py _hra_msgs_generate_messages_check_deps_${_filename})

# target for backward compatibility
add_custom_target(hra_msgs_genpy)
add_dependencies(hra_msgs_genpy hra_msgs_generate_messages_py)

# register target for catkin_package(EXPORTED_TARGETS)
list(APPEND ${PROJECT_NAME}_EXPORTED_TARGETS hra_msgs_generate_messages_py)



if(gencpp_INSTALL_DIR AND EXISTS ${CATKIN_DEVEL_PREFIX}/${gencpp_INSTALL_DIR}/hra_msgs)
  # install generated code
  install(
    DIRECTORY ${CATKIN_DEVEL_PREFIX}/${gencpp_INSTALL_DIR}/hra_msgs
    DESTINATION ${gencpp_INSTALL_DIR}
  )
endif()
if(TARGET std_msgs_generate_messages_cpp)
  add_dependencies(hra_msgs_generate_messages_cpp std_msgs_generate_messages_cpp)
endif()
if(TARGET geometry_msgs_generate_messages_cpp)
  add_dependencies(hra_msgs_generate_messages_cpp geometry_msgs_generate_messages_cpp)
endif()
if(TARGET actionlib_msgs_generate_messages_cpp)
  add_dependencies(hra_msgs_generate_messages_cpp actionlib_msgs_generate_messages_cpp)
endif()

if(geneus_INSTALL_DIR AND EXISTS ${CATKIN_DEVEL_PREFIX}/${geneus_INSTALL_DIR}/hra_msgs)
  # install generated code
  install(
    DIRECTORY ${CATKIN_DEVEL_PREFIX}/${geneus_INSTALL_DIR}/hra_msgs
    DESTINATION ${geneus_INSTALL_DIR}
  )
endif()
if(TARGET std_msgs_generate_messages_eus)
  add_dependencies(hra_msgs_generate_messages_eus std_msgs_generate_messages_eus)
endif()
if(TARGET geometry_msgs_generate_messages_eus)
  add_dependencies(hra_msgs_generate_messages_eus geometry_msgs_generate_messages_eus)
endif()
if(TARGET actionlib_msgs_generate_messages_eus)
  add_dependencies(hra_msgs_generate_messages_eus actionlib_msgs_generate_messages_eus)
endif()

if(genlisp_INSTALL_DIR AND EXISTS ${CATKIN_DEVEL_PREFIX}/${genlisp_INSTALL_DIR}/hra_msgs)
  # install generated code
  install(
    DIRECTORY ${CATKIN_DEVEL_PREFIX}/${genlisp_INSTALL_DIR}/hra_msgs
    DESTINATION ${genlisp_INSTALL_DIR}
  )
endif()
if(TARGET std_msgs_generate_messages_lisp)
  add_dependencies(hra_msgs_generate_messages_lisp std_msgs_generate_messages_lisp)
endif()
if(TARGET geometry_msgs_generate_messages_lisp)
  add_dependencies(hra_msgs_generate_messages_lisp geometry_msgs_generate_messages_lisp)
endif()
if(TARGET actionlib_msgs_generate_messages_lisp)
  add_dependencies(hra_msgs_generate_messages_lisp actionlib_msgs_generate_messages_lisp)
endif()

if(gennodejs_INSTALL_DIR AND EXISTS ${CATKIN_DEVEL_PREFIX}/${gennodejs_INSTALL_DIR}/hra_msgs)
  # install generated code
  install(
    DIRECTORY ${CATKIN_DEVEL_PREFIX}/${gennodejs_INSTALL_DIR}/hra_msgs
    DESTINATION ${gennodejs_INSTALL_DIR}
  )
endif()
if(TARGET std_msgs_generate_messages_nodejs)
  add_dependencies(hra_msgs_generate_messages_nodejs std_msgs_generate_messages_nodejs)
endif()
if(TARGET geometry_msgs_generate_messages_nodejs)
  add_dependencies(hra_msgs_generate_messages_nodejs geometry_msgs_generate_messages_nodejs)
endif()
if(TARGET actionlib_msgs_generate_messages_nodejs)
  add_dependencies(hra_msgs_generate_messages_nodejs actionlib_msgs_generate_messages_nodejs)
endif()

if(genpy_INSTALL_DIR AND EXISTS ${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/hra_msgs)
  install(CODE "execute_process(COMMAND \"/usr/bin/python3\" -m compileall \"${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/hra_msgs\")")
  # install generated code
  install(
    DIRECTORY ${CATKIN_DEVEL_PREFIX}/${genpy_INSTALL_DIR}/hra_msgs
    DESTINATION ${genpy_INSTALL_DIR}
  )
endif()
if(TARGET std_msgs_generate_messages_py)
  add_dependencies(hra_msgs_generate_messages_py std_msgs_generate_messages_py)
endif()
if(TARGET geometry_msgs_generate_messages_py)
  add_dependencies(hra_msgs_generate_messages_py geometry_msgs_generate_messages_py)
endif()
if(TARGET actionlib_msgs_generate_messages_py)
  add_dependencies(hra_msgs_generate_messages_py actionlib_msgs_generate_messages_py)
endif()
