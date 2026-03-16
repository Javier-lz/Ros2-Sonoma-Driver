# import rclpy
# from rclpy.node import Node 
# from message_filters import Subscriber, TimeSynchronizer
# from sensor_msgs.msg import Image
# from nav_msgs.msg import Odometry
# from geometry_msgs.msg import Twist
# from pathlib import Path
import csv 
import os 
import time


# class controller_node(Node): 
#     def __init__(self): 
#         pass 


with open("src/four_wheels_robot_nn/four_wheels_robot_nn/data/training_data/data.csv",'+rt') as f:

    print(f.readlines())
    print(f.readline())

    
