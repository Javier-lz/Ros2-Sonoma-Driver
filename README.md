# Ros2-Sonoma-Driver
Autonomous vehicle (prius_hybrid) using gazebo for simulation and ros2 for communication. 


## Description: 

This project is my first work with ros2 and gazebo, where I have learned a lot about package creation and communication with the different tools offered by the ros2 middleware, mainly topics though, as well as bridging with gazebo to make simulations sort of physically accurate.

The project has also taught me quite a bit about visual processing because it has led me to try and read on multiple computer vision techniques like image thresholding, different works on lane detection and even use different standard models like Yolo to make the project work. I was not able to use these techniques properly because of implementations and lack of insight when I came across them so I ended up doing the following process. 


### Development Process: 

#### Image preprocessing

Firstly I used the standard Sonoma raceway with the prius_hybrid model with implemented sensors. This allowed me to work on the ros_gz_bridge in order to create topics for ros2 and being able to use the information from the sensors. I used mainly /cmd_vel and the front camera from the car. Afterwards, I used openCv in python for some basic image downscaling and region of interest cropping which is later published to a topic called /processed_image. 

#### Data gathering 

Since what I used for this project is a convonlutional neural network with supervised learning, I needed to gather the driving data. In order to do this I used a PS4 controller to publish to the cmd_vel topic which allowed me to precisely control the car. I had tried using the keyboard and, even though it worked, my lack of skills while driving made the process of gathering data extremely innefficient and with a high risk of inyecting incorrect input, therefore I spent some time looking how to use the controller. 

Afterwards, I created the data_gathering node which was responsible for gathering all the necessary data, /processed_image , linear forward velocity and steering angle and save it to a csv file together with an image folder with a unique identifier. Moreover, the images were further processed to use HSV format because it is better to generalize visual data and more robust to lighting and terrain differences. 



#### Data preprocessing 

I made a python script that is run on the data where I filter first of all the data that could have been with uploads failures on the image generation, which means, that I deleted the instances of data where there wre no corresponding images. 
Afterwards, I used pandas to balance the data since a lot of the records were taken from straight driving, the initial models did not turn correctly. Furthermore, after more data gathering I found out that the initial gathering moments where the car was stopped were getting way too much importance because one model chose to keep still and never accelerate, this turned into filtering the data by having a minimum speed of 0.05 m/s, enough speed for a raceway although something with which I would need to be more careful if this was a city driving model. 


### CNN Supervised Learning 

This project allowed me to learn and use convonlutional neural networks to develop a good understanding of how the models recognize features. This project consists of a basic convolutional neural network with 3 layers, that are then connected to a fully connected layer with another 3 layers (counting the output layer). 

The cnn was made using PyTorch and the training was made by comparing the whole model's output given only the images and then optimizing each weight with Adam's built in optimizer. 

#### Testing: 
In order to asses the model's performance I left the car on different tracks with different environments to test whether the steering and velocity control generalized to different (noticeable) roads. It did have some difficulties on some tight curves which it reached way too fast (but just like professional drivers).

### Future developments. 

There are a lot of things I would like to implement in this or similar projects like implementing the acceleration as an output instead of velocity and also I would like to implement reinforcement learning together with image segmentation for the car to learn to not go outside the road. 


