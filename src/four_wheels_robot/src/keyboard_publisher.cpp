#include "rclcpp/rclcpp.hpp"
#include <iostream>
#include "geometry_msgs/msg/twist.hpp"
#include "rclcpp/node.hpp"
#include <chrono>
#include <termios.h>
#include <queue>
#include <thread>
#include <mutex>
#include <unistd.h>
#include <poll.h>
#define MAX_VELOCITY 5.0 // in [m/s] also, do make it a float for division to work 

#define MAX_ANGLE 0.4
#define KEY_BUFFER 10
#define KEYS_PER_SECOND 15
#define LOOPS_PER_KEY_RECOGNIZED ((20.0 / KEYS_PER_SECOND) + 1)

class keyboard_node : public rclcpp::Node
{
private:
  rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr publisher_key;
  rclcpp::TimerBase::SharedPtr timer_key;
  std::mutex buffer_muter; 
  std::queue<char> keys_buffer;
  std::thread key_thread;
  geometry_msgs::msg::Twist data_message;
  bool running;
  struct termios oldt,newt;

  char get_key_pressed()
  {
    
    char ch;
    
    
    ch = getchar();
    
    return ch;
  }

  void key_listener()
  {
    newt = oldt;
    newt.c_lflag &= ~(ICANON | ECHO);
    tcsetattr(STDIN_FILENO, TCSANOW, &newt);
    // Structure to poll STDIN
        struct pollfd pfd = { STDIN_FILENO, POLLIN, 0 };

       while (running && rclcpp::ok()) {
        // Timeout set to 100ms
        int ret = poll(&pfd, 1, 100);
        
        if (ret > 0 && (pfd.revents & POLLIN)) {
            char c;
            // Read exactly 1 byte directly from the OS file descriptor
            if (read(STDIN_FILENO, &c, 1) > 0) { 
                std::lock_guard<std::mutex> lock(buffer_muter);
                if (keys_buffer.size() < KEY_BUFFER) {
                    keys_buffer.push(c);
                }
            }
        }
    }
        tcsetattr(STDIN_FILENO, TCSANOW, &oldt);
  }

public:
  keyboard_node() : rclcpp::Node("keyboard_node")
  {
    using namespace std::chrono_literals;
    tcgetattr(STDIN_FILENO, &oldt);
    
    running = true;
 // how many callbacks until executing the key so that a light tap does not give docens of inputs.

    publisher_key = this->create_publisher<geometry_msgs::msg::Twist>("/cmd_vel", 10);

    timer_key = this->create_wall_timer(100ms, std::bind(&keyboard_node::key_callback, this));
    key_thread =std::thread(&keyboard_node::key_listener, this);
    std::cout << key_thread.get_id() << "\n";

    
    RCLCPP_INFO(this->get_logger(), "========================================");
    RCLCPP_INFO(this->get_logger(), "   KEYBOARD CONTROL NODE STARTED");
    RCLCPP_INFO(this->get_logger(), "   Click THIS terminal to drive!");
    RCLCPP_INFO(this->get_logger(), "   Controls: W/S (Speed), A/D (Turn)");
    RCLCPP_INFO(this->get_logger(), "   Press Ctrl+C to exit safely");
    RCLCPP_INFO(this->get_logger(), "========================================");
  }


  ~keyboard_node()
  {
    running = false;
    
    if (key_thread.joinable()) {
            key_thread.join(); // Clean up on shutdown
        }
  }


  void key_callback( )
  { 
    char character= '\0';
    {
    
    std::lock_guard<std::mutex> lock(buffer_muter);
    if (!this->keys_buffer.empty())
    {
      
    
    character=this->keys_buffer.front();
    this->keys_buffer.pop();
    }
  }
 if (character == 'w'){
        if(this->data_message.linear.x < MAX_VELOCITY){
            this->data_message.linear.x+= MAX_VELOCITY/10;
        }

    }
    else if (character == 's'){
        if(this->data_message.linear.x >-MAX_VELOCITY){
            this->data_message.linear.x-= MAX_VELOCITY/10;
        }

    }
    else if (character == 'd'){
        if(this->data_message.angular.z > 0){
            this->data_message.angular.z = 0;
        }
        else if (this->data_message.angular.z > -MAX_ANGLE){
          this->data_message.angular.z-= MAX_ANGLE/20;
        }

    }
       else if (character == 'a'){
        if(this->data_message.angular.z < 0){
            this->data_message.angular.z = 0;
        }
        else if (this->data_message.angular.z < MAX_ANGLE){

            this->data_message.angular.z+= MAX_ANGLE/20;

        }

    }
    else{
        // if (this->data_message.angular.z > 0)
        // {
        //     this->data_message.angular.z -= MAX_ANGLE/100;
        // }
        // else
        // {
        //       this->data_message.angular.z += MAX_ANGLE/100;
        // }
        // if (this->data_message.linear.x >0)
        // {
        //     this->data_message.linear.x -= MAX_VELOCITY/500;

        // }
        // else
        // {
        //     this->data_message.linear.x += MAX_VELOCITY/100; 

        // }

    }
    
  
  this->publisher_key->publish(data_message);
}
};


int main(int argc, char * argv[]){
  rclcpp::init(argc,argv);
  
  rclcpp::spin(std::make_shared<keyboard_node>());
  rclcpp::shutdown();
  return 0;


}