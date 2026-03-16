#include <memory>

#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"
#include "sensor_msgs/msg/image.hpp"

#include <opencv2/opencv.hpp> 
#include "cv_bridge/cv_bridge.hpp"


class MinimalSubscriber : public rclcpp::Node
{
public:
  MinimalSubscriber()
  : Node("minimal_subscriber")
  {
    auto topic_callback =
      [this](sensor_msgs::msg::Image::SharedPtr msg) -> void {

       
        try {
         
          cv::Mat img = cv_bridge::toCvShare(msg, "bgr8")->image;

          cv::Mat out;
          cv::threshold(img,out,56, 255, cv::THRESH_BINARY);
          cv::cvtColor(out, out, cv::COLOR_BGR2GRAY);
          
          cv::imshow("Received Image", out);
          cv::waitKey(1);
          cv::imshow("Original Image", img);
          cv::waitKey(1);
           RCLCPP_INFO(this->get_logger(), "Received image of size: %d x %d size %ld", msg->width, msg->height, out.total()*out.elemSize());
        } catch (cv_bridge::Exception& e) {
          RCLCPP_ERROR(this->get_logger(), "cv_bridge exception: %s", e.what());
          return;
        }

      };
    subscription_ =
      this->create_subscription<sensor_msgs::msg::Image>("/front_camera", 10, topic_callback);
  }

private:
  rclcpp::Subscription<sensor_msgs::msg::Image>::SharedPtr subscription_;
};

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<MinimalSubscriber>());
  rclcpp::shutdown();
  return 0;
}