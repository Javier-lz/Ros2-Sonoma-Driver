import rclpy
from rclpy.node import Node 
from message_filters import Subscriber, TimeSynchronizer
from sensor_msgs.msg import Image
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge
from pathlib import Path
import csv 
import os 
import matplotlib.pyplot as plt 
import numpy as np
import torch.nn as nn
import torch
from torchvision import transforms
from four_wheels_robot_nn.config import *
import cv2 as cv 

class controller_node(Node): 
    def __init__(self): 
        super().__init__('ai_controller_node')
        
        self.path_data:Path = Path.cwd() / "src/four_wheels_robot_nn/four_wheels_robot_nn/data/training_dat/data.csv"
        
        self.path_images=  Path("src/four_wheels_robot_nn/four_wheels_robot_nn/data/training_dat/images")
        # 128*64 --> 32 (32,16) 64 (8,2)

        # MOdel preparing 
        conv_layers = nn.Sequential(
                nn.Conv2d(conv_attr_1[0],conv_attr_1[1],kernel_size=conv_attr_1[2]["kernel_size"],padding=conv_attr_1[3]["padding"]), 
                nn.ReLU(),
                nn.MaxPool2d(2, 2),                         
                
                nn.Conv2d(conv_attr_2[0],conv_attr_2[1],kernel_size=conv_attr_2[2]["kernel_size"],padding=conv_attr_2[3]["padding"]), 
                nn.ReLU(),
                nn.MaxPool2d(2, 2),                         
                
                nn.Flatten()
            )

        with torch.no_grad():
            dummy = torch.zeros(1, 3, y_max-y_min, x_max-x_min)
            n_features = conv_layers(dummy).numel()

        self.network = nn.Sequential(
            conv_layers,
            nn.Linear(n_features, number_of_neurons_1),
            nn.ReLU(),  
            nn.Linear(number_of_neurons_1,number_of_neurons_2),
            nn.ReLU(),
            nn.Linear(number_of_neurons_2, number_of_outputs)
            )
        
        self.model_path = Path("src/four_wheels_robot_nn/four_wheels_robot_nn/data/training_dat/robot_model.pth")
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        state_dict = torch.load(self.model_path,map_location=device)
        self.network.load_state_dict(state_dict=state_dict)

        self.network.eval()
        self.network.to(device)
        self.device = device 
        self.transf = transforms.Compose([
            transforms.ToTensor(),
        ])


        # Subscriber Publisher ROS2 preparation

        self.bridge = CvBridge()
        self.subscr = self.create_subscription(Image,"/processed_image",self.read,10)
        self.publisher= self.create_publisher(Twist,"/cmd_vel",10)


        



        

        
    def read(self,msg:Image):
        img = self.bridge.imgmsg_to_cv2(msg,"rgb8")
        img= cv.cvtColor(img,cv.COLOR_BGR2HSV) 


        vel,angle= self.predict(img) 

        vel_message:Twist= Twist()
        vel_message.linear.x=float(vel)
        vel_message.angular.z=float(angle)
        self.get_logger().info(f"velocity published {vel_message.linear.x}  steer {vel_message.angular.z}")
        
        self.publisher.publish(vel_message)


        

    def predict(self,img):
        

        image = img.astype(np.float32)
        target_width=x_max-x_min
        target_height= y_max-y_min
        image = cv.resize(image, (target_width, target_height), interpolation=cv.INTER_LINEAR)
        image[:,:,0]/=179.0
        image[:,:,1]/=255.0 
        image[:,:,2]/=255.0 
        # plt.figure()
        # plt.imshow(image) 
        # plt.show() 
        image = np.transpose(image,(2,0,1)) 
        image= torch.from_numpy(image) 
        
        image=image.unsqueeze(0)
        image=image.to(self.device)
        with torch.no_grad():
            prediction = self.network(image)
        #[speed, steer]
        return prediction.cpu().numpy()[0]

        


def main():
    rclpy.init()

    node = controller_node()
    try: 
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally: 
        node.destroy_node()
        rclpy.shutdown()






    
