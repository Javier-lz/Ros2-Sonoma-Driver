#include "rclcpp/rclcpp.hpp"
#include "geometry_msgs/msg/twist.hpp"

#include <memory>


class car_velocity_publisher : public rclcpp::Node 
{
private:
    rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr publisher_;
    rclcpp::TimerBase::SharedPtr timer_;
    float linear_velocity_=0.8;
    float angular_velocity_=0.5;
    int sign=1; 
public:
    car_velocity_publisher():Node("car_velocity_publisher")
    {
        publisher_ =
          this->create_publisher<geometry_msgs::msg::Twist>("/cmd_vel", 10);

        auto topic_callback = [this]() -> void {
            auto message = geometry_msgs::msg::Twist();
            message.linear.x = linear_velocity_;
            message.angular.z = sign*angular_velocity_;
            sign*= -1;
            linear_velocity_ += 0.1; 
            if(linear_velocity_ > 2.0){
                linear_velocity_ = 0.0;
            }


            RCLCPP_INFO(this->get_logger(), "Publishing: '%f' and '%f'", message.linear.x, message.angular.z);
            this->publisher_->publish(message);
    
          };
        _ = this->create_wall_timer(
            std::chrono::milliseconds(2500), topic_callback);
        
    }
 
};
int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<car_velocity_publisher>());
  rclcpp::shutdown();
  return 0;
}




