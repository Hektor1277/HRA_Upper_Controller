cmake_minimum_required(VERSION 3.0.2)
project(hra_control_ui)

find_package(catkin REQUIRED COMPONENTS
  rospy
  rqt_gui
  rqt_gui_py
  std_msgs
  hra_msgs
  actionlib
)

catkin_python_setup()

catkin_package(
  #LIBRARIES
  #CATKIN_DEPENDS
  #DEPENDS
)

install(FILES
  plugin.xml
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)

install(DIRECTORY resource/
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/resource
)
