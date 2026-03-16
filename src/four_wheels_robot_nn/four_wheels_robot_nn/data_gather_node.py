import rclpy
from rclpy.node import Node 
from message_filters import Subscriber, TimeSynchronizer
from sensor_msgs.msg import Image
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Twist
from pathlib import Path
import csv 
import os 
import time

DATA_PATH="../data/training_data"
class DataGatherer(Node): 
    def __init__(self): 
        super().__init__('data_gathering_node')
        
        # Now i want to save image, velocity position and angle ||4|| elements 
        # in a state which will be saved for the training 
        header=["time","velocity","odometry","steer","image"]
        self.state_buffer={"time":time.time_ns(),"velocity":0,"odometry":"","steer":0,"image":""}
        self.velocity_buffer=[0]
        self.position_buffer=[0]
        self.image_buffer=[0]
        self.path=Path.cwd() / "src" / "four_wheels_robot_nn" / "four_wheels_robot_nn" / "data" / "training_data"
        self.path.mkdir(parents=True,exist_ok=True)
        self.image_subscriber=self.create_subscription(Image,'/processed_image',self.add_image,10)
        self.velocity_steer_subscriber=self.create_subscription(Twist,'/cmd_vel',self.add_velocity_steer,10)
        self.position_subscriber=self.create_subscription(Odometry,'/odometry',self.add_odometry,10)
        self.timer= self.create_timer(0.5,self.call_back)
        self.path = self.path / "data.csv"
        self.path.touch(exist_ok=True)
        
        self.fp= open(self.path,"a")
        self.writer = csv.DictWriter(self.fp,fieldnames=header)

        
        

    def call_back(self): 
        self.writer.writerow(self.state_buffer)



        return 
    
    def add_velocity_steer(self,msg:Twist): 
        # Saves the last two velocities to calculate acceleration 
     
        self.velocity_buffer[0]= msg.linear.x

        self.state_buffer["velocity"]=(self.velocity_buffer[0])
        return 
    def add_odometry(self,msg:Odometry): 
        self.state_buffer["steer"]=msg.pose.pose.orientation.z
     
        
        self.state_buffer["odometry"]=f"{msg.pose.pose.position.x},{msg.pose.pose.position.y},{msg.pose.pose.position.z}"

        return
    def add_image(self,msg:Image): 
        self.image_buffer[0]= msg.data
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

    



        

        

        