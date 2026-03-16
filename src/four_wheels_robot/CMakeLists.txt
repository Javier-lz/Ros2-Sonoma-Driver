cmake_minimum_required(VERSION 3.8)
project(four_wheels_robot)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclpy REQUIRED)
find_package(std_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(OpenCV REQUIRED)
find_package(cv_bridge REQUIRED)

add_executable(publisher src/camera_publisher_cpp.cpp)

ament_target_dependencies(publisher rclcpp std_msgs sensor_msgs)
# uncomment the following section in order to fill in
# further dependencies manually.
# find_package(<dependency> REQUIRED)
add_executable(subscriber src/camera_subscriber_cpp.cpp)
ament_target_dependencies(subscriber rclcpp std_msgs sensor_msgs OpenCV cv_bridge)




#add_executable(velocity_publisher src/car_velocity_publisher.cpp)
#ament_target_dependencies(velocity_publisher rclcpp std_msgs geometry_msgs)

add_executable(keyboard_control src/keyboard_publisher.cpp)
ament_target_dependencies(keyboard_control rclcpp geometry_msgs)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  # the following line skips the linter which checks for copyrights
  # comment the line when a copyright and license is added to all source files
  set(ament_cmake_copyright_FOUND TRUE)
  # the following line skips cpplint (only works in a git repo)
  # comment the line when this package is in a git repo and when
  # a copyright and license is added to all source files
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()
install(
  DIRECTORY
    urdf
    config
    launch
    worlds
  DESTINATION
    share/${PROJECT_NAME}/
)
install(TARGETS 
publisher 
subscriber
##velocity_publisher
keyboard_control

DESTINATION lib/${PROJECT_NAME}
)
ament_package()
