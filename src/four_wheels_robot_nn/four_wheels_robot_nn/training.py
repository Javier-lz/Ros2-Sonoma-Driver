import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from nav_msgs.msg import Odometry
from cv_bridge import CvBridge
import cv2
import torch
import torch.nn as nn

# --- 1. THE BRAIN (PyTorch Model) ---
class PriusDriverNet(nn.Module):
    def __init__(self):
        super(PriusDriverNet, self).__init__()
        
        # Image Branch (CNN) - Expects 64x64 2 channel input 
        self.image_branch = nn.Sequential( 
            nn.Conv2d(2, 16, kernel_size=3, stride=2), 
            nn.ReLU(),
            nn.Conv2d(16, 32, kernel_size=3, stride=2),
            nn.ReLU(),
            nn.Flatten(),
        ) 
        
        # Telemetry Branch (MLP) 
        # Inputs: [Linear Velocity X, Angular Velocity Z]
        self.telemetry_branch = nn.Sequential(
            nn.Linear(2, 16),
            nn.ReLU(),
        )

       
        # Inside __init__
        
        dummy_input = torch.zeros(1, 2, 64, 64)
        n_flattened = self.image_branch(dummy_input).shape[1]
        # Now use n_flattened inside your Linear layer!
        self.decision_gate = nn.Sequential(
            nn.Linear(n_flattened + 16, 64),
            nn.ReLU(),
            nn.Linear(64, 2) # Outputs: [Throttle/Brake, Steering Angle]
        )
        self.buffer = RolloutBuffer()

    def forward(self, img, telemetry):
        img_features = self.image_branch(img)
        car_features = self.telemetry_branch(telemetry)
        combined = torch.cat((img_features, car_features), dim=1)
        return self.decision_gate(combined)


# --- 2. THE INTERFACE (ROS 2 Node) ---
class TrainingNode(Node):   
    def __init__(self):
        super().__init__('training_node')
        self.get_logger().info("Training Node Started with Velocity Inputs.")
        
        self.model = PriusDriverNet()
        self.bridge = CvBridge()
        self.latest_telemetry = None # Will store [vel_x, ang_z]

        # Subscribers
        self.odom_sub = self.create_subscription(
            Odometry, 
            '/model/prius_hybrid/odometry', 
            self.odometry_callback, 
            10)
            
        self.img_sub = self.create_subscription(
            Image,
            '/processed_image', 
            self.image_callback,
            10)

    def odometry_callback(self, msg: Odometry):
        # Extract Linear Velocity X and Angular Velocity Z
        vel_x = msg.twist.twist.linear.x
        ang_z = msg.twist.twist.angular.z
        
        # Store as a tensor for the model
        self.latest_telemetry = torch.tensor([[vel_x, ang_z]], dtype=torch.float32)

    def image_callback(self, msg: Image):
        if self.latest_telemetry is None:
            return

        # 1. Convert and Resize Image
        cv_img = self.bridge.imgmsg_to_cv2(msg, "32FC2")
        cv_img = cv2.resize(cv_img, (64, 64)) 
        
        # 2. Preprocess for PyTorch (B, C, H, W)

        state_img = torch.from_numpy(cv_img).permute(2, 0, 1).float().unsqueeze(0)
        mu, sigma = self.model.actor(state_img, self.latest_telemetry)
        value = self.model.critic(state_img, self.latest_telemetry)
        
        dist = torch.distributions.Normal(mu, torch.exp(sigma))
        action = dist.sample()
        log_prob = dist.log_prob(action).sum(dim=-1)
        
        if len(self.buffer.states_img) >= 2048:
            self.update_epochs += 1
            self.update_model() 
            if self.update_epochs ==10: 
                self.update_epochs=0
                self.buffer.clear()
            

        
        else: 
            self.propagation(state_img, self.latest_telemetry, action, log_prob, reward=0.0, done=False, value=value)
            



    def ppo_loss(self,old_probs, new_probs, advantages, critic_values, returns, epsilon=0.2):
        # 1. Policy Loss (The Actor)
        # How much did the probability of the 'good' action change?
        ratio = new_probs / old_probs
        surr1 = ratio * advantages
        surr2 = torch.clamp(ratio, 1.0 - epsilon, 1.0 + epsilon) * advantages
        actor_loss = -torch.min(surr1, surr2).mean()

        # 2. Value Loss (The Critic)
        # Does the Critic correctly guess how much reward we are getting?
        critic_loss = nn.MSELoss()(critic_values, returns)

        # Total Loss = Actor + Critic
        return actor_loss + 0.5 * critic_loss

    def propagation(self, state_img, state_tel, action, log_prob, reward, done, value):
        self.buffer.states_img.append(state_img)
        self.buffer.states_tel.append(state_tel)
        self.buffer.actions.append(action)
        self.buffer.log_probs.append(log_prob)
        self.buffer.rewards.append(reward)
        self.buffer.dones.append(done)
        self.buffer.values.append(value)





class RolloutBuffer:
    def __init__(self):
        # Observations
        self.states_img = []  # The 2-channel masks
        self.states_tel = []  # The [velocity, steering] tensors
        
        # Decisions
        self.actions = []     # The steering/throttle commands sampled
        self.log_probs = []   # The "confidence" of those actions
        
        # Feedback
        self.rewards = []     
        self.dones = []       
        self.values = []      
    
    def clear(self):

        self.states_img.clear()
        self.states_tel.clear()
        self.actions.clear()
        self.log_probs.clear()
        self.rewards.clear()
        self.values.clear()
        self.dones.clear()







def main(args=None):
    rclpy.init(args=args)
    node = TrainingNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()