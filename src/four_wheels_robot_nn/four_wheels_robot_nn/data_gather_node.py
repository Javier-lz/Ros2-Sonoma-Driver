import rclpy
from rclpy.node import Node 
from message_filters import Subscriber, TimeSynchronizer
from sensor_msgs.msg import Image
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Twist
from pathlib import Path
import csv 
import os 
import datetime
import time
import cv2
from cv_bridge import CvBridge
import shutil


DATA_PATH="../data/training_dat"
class DataGatherer(Node): 
    def __init__(self): 
        super().__init__('data_gathering_node')
        self.declare_parameter('live',0)
        live_recording=self.get_parameter('live').get_parameter_value().integer_value
        # Now i want to save image, velocity position and angle ||4|| elements 
        # in a state which will be saved for the training 
        self.get_logger().info("Initialized the node ")
        self.bridge=CvBridge()
        header=["time","velocity","odometry","steer","image"]
        self.state_buffer={"time":time.time_ns(),"velocity":0,"odometry":"","steer":0,"image":""}
        self.velocity_buffer=[0]
        self.position_buffer=[0]
        self.image_buffer=["",""]
        self.get_logger().info("Initialized Buffers ")
        self.path=Path.cwd() / "src" / "four_wheels_robot_nn" / "four_wheels_robot_nn" / "data" / "training_dat"
        
        self.get_logger().info(f"The value of live-recording{live_recording}")
        if live_recording==1: 
            self.image_path=self.path /"images"
            self.image_path.mkdir(parents=True,exist_ok=True)
            self.path = self.path / "data.csv"
            self.path.touch(exist_ok=True)
            self.fp= open(self.path,"a",buffering=2)
            
            
        else:
            self.image_path=self.path  /"batch"
            self.get_logger().info("Tha paths are accessed???? ")
            if self.image_path.exists():
                shutil.rmtree(self.image_path)
            self.image_path.mkdir(parents=True,exist_ok=True)
            
            
            self.path = self.path / "data_batch.csv"
            self.path.touch(exist_ok=True)
            self.fp= open(self.path,"w",buffering=2)

       
        self.image_subscriber=self.create_subscription(Image,'/processed_image',self.add_image,10)
        self.velocity_steer_subscriber=self.create_subscription(Twist,'/cmd_vel',self.add_velocity_steer,10)
        self.position_subscriber=self.create_subscription(Odometry,'/odometry',self.add_odometry,10)
        self.timer= self.create_timer(0.1,self.call_back)
        #self.get_logger().info("Create subscriptions")
        
        self.path.touch(exist_ok=True)
        
        
        self.writer = csv.DictWriter(self.fp,fieldnames=header)
        # if os.path.getsize(self.path) == 0: 
        #     self.writer.writeheader() 
     
        self.gazebo_detected= False
        #self.get_logger().info("Finishing initializing")
    

    def call_back(self): 
        #self.get_logger().info("Entering callback")
        # try:
    

        if self.image_buffer[0] != "":
            # 1. Write Image
            cv2.imshow("name",self.image_buffer[1]) 
            cv2.waitKey(1) 
            cv2.imwrite(str(self.image_path / self.image_buffer[0]), self.image_buffer[1])
            
            # 2. Write CSV
            self.writer.writerow(self.state_buffer)
            self.image_buffer[0]= ""
            
            
            # 3. CRITICAL: Flush the file to disk
            self.fp.flush()
        else:
            #self.get_logger().warn("Waiting for first image...")

            pass
        #     self.get_logger().info(f"{self.image_path} ,    {self.image_buffer[1]}")
        #     self.get_logger().error("Image written incorrectly")
        return 
    
    def add_velocity_steer(self,msg:Twist): 
        # Saves the last two velocities to calculate acceleration 
     
        self.velocity_buffer[0]= msg.linear.x
        self.state_buffer["steer"]=msg.angular.z 
        self.state_buffer["velocity"]=(self.velocity_buffer[0])
        return 
    def add_odometry(self,msg:Odometry): 
        
     
        
        self.state_buffer["odometry"]=f"{msg.pose.pose.position.x},{msg.pose.pose.position.y},{msg.pose.pose.position.z}"

        return
    def add_image(self,msg:Image): 
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        self.image_buffer[0]= f"frame_{timestamp}.jpg"
        self.image_buffer[1]=cv2.cvtColor(self.bridge.imgmsg_to_cv2(msg,"bgr8"),cv2.COLOR_BGR2HSV)

        self.state_buffer["image"]=self.image_buffer[0]
        self.state_buffer["time"]=time.time_ns()
        




        

        return 
    





   

    
        
    



def main():
    rclpy.init()

    data_gatherer=DataGatherer()

    try: 
        rclpy.spin(data_gatherer)
    
    except KeyboardInterrupt:
        pass
    finally:

        data_gatherer.destroy_node()
        rclpy.shutdown()

    



        

        

        