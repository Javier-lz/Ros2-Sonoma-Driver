import cv2 as cv 
import os

from cv_bridge import CvBridge
from ament_index_python.packages import get_package_share_directory
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
import cv_bridge
import numpy as np

import torch
class ImageProcessingNode(Node):
    def __init__(self):
        super().__init__('image_processing_node')
        
        # Initialize Bridge once to save CPU
        self.bridge = CvBridge()
        
        
        self.y_min, self.y_max = 64, 128
        self.x_min, self.x_max = 0,128
        
        self.subscription = self.create_subscription(
            Image,
            '/front_camera',
            self.image_callback,
            10)
        self.publisher_ = self.create_publisher(Image, '/processed_image', 10)
        self.get_logger().info("YOLO Node Started. Waiting for images...")

    def image_callback(self, msg: Image):
        try: 
            # Convert ROS Image to OpenCV
            raw_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding="mono8")
            raw_image=cv.resize(raw_image,[128,128])
            raw_image = raw_image[self.y_min:self.y_max, self.x_min:self.x_max]
            _, raw_image = cv.threshold(raw_image, 60, 255, cv.THRESH_TOZERO)
            # Run Inference (Stream=True is faster for video)
            
            
            # Debugging: Check if anything was detected
            # if len(results[0].boxes) == 0:
            #     self.get_logger().warn("No objects detected in this frame.")
            
            # else: 
            #     road_masks = np.zeros((640, 640), dtype=np.uint8)

            #     for mask in results[0].masks.data: 
            #         mask= mask if mask is not None else []
            #         road_masks = np.maximum(mask.cpu().numpy().astype(np.uint8), road_masks) 


            #     dist_trans= cv.distanceTransform(road_masks.astype(np.uint8), cv.DIST_L2,5)
            #     cv.normalize(dist_trans,dist_trans,0,1.0,cv.NORM_MINMAX)

            #     car_mask = np.zeros_like(dist_trans)
            #     h,w = car_mask.shape 
            #     cv.rectangle(car_mask, (int(w/2)-60, h-50), (int(w/2)+60, h), (1), -1)
            #     target_size = (64, 64) 

            #     small_road_mask = cv.resize(dist_trans, target_size, interpolation=cv.INTER_AREA)

            #     # Resize the car mask (or just generate it at 64x64 directly)
            #     small_car_mask = cv.resize(car_mask, target_size, interpolation=cv.INTER_NEAREST) 
            #     stack_img= np.stack([small_road_mask, small_car_mask], axis=0)
            #     state_img = torch.from_numpy(stack_img).float()
            #     self.get_logger().info(f'State Image Shape: {state_img.shape}')
            #     stack_img=stack_img.transpose(1,2,0) 
            #     message= cv_bridge.CvBridge()

            #     mesg= message.cv_to_imgmsg(stack_img, encoding="32FC2")
            #     self.publisher_.publish(mesg)   
            #     view_data = state_img.detach().cpu().numpy().transpose(1, 2, 0) # [H, W, 2]

            #     # 2. Create a 'Zero' channel for Blue
            #     blue_channel = np.zeros_like(view_data[:, :, 0])

            #     # 3. Merge into a BGR image
            #     # Format: [Blue, Green, Red]
            #     # We put Distance Transform in Green and Car Mask in Red
            #     vis_image = cv.merge([blue_channel, view_data[:, :, 0], view_data[:, :, 1]])

            #     # 4. Show it
            #     cv.imshow("Road Segmentation", vis_image)
            #     cv.waitKey(1)
            # # Get the annotated image
        

            # # Display the image
            try:
                
                message = self.bridge.cv2_to_imgmsg(raw_image,encoding="mono8")
                self.publisher_.publish(message)
            except: 
                self.get_logger().info("Message not published ")
            
            big_view = cv.resize(raw_image, (512, 256), interpolation=cv.INTER_NEAREST)

            cv.imshow("Road d", big_view)  
        
        # This is critical: waitKey(1) allows the GUI to refresh
        
            cv.waitKey(1)

        except Exception as e:
            self.get_logger().error(f'Error: {e}')

def main(): 
    rclpy.init()
    node = ImageProcessingNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        cv.destroyAllWindows()
        node.destroy_node()
        rclpy.shutdown()