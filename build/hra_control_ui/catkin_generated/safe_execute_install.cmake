execute_process(COMMAND "/home/hra/catkin_ws/build/hra_control_ui/catkin_generated/python_distutils_install.sh" RESULT_VARIABLE res)

if(NOT res EQUAL 0)
  message(FATAL_ERROR "execute_process(/home/hra/catkin_ws/build/hra_control_ui/catkin_generated/python_distutils_install.sh) returned error code ")
endif()
