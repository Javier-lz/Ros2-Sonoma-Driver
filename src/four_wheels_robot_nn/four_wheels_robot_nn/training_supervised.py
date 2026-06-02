import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset, random_split,Subset
from torchvision import transforms
from pathlib import Path
import pandas as pd
import numpy as np
from PIL import Image
from config import * 
import cv2 as cv 
import matplotlib.pyplot as plt 
from datacleaner import main_logic_cleaner
EPOCHS = 30
# --- AGENT 1: THE DATASET (FIXED COLUMN MAPPING) ---
class RobotDataset(Dataset):
    def __init__(self, csv_path, img_dir, transform=None,augment=False):
        # Requisite: No header in your data, so we set header=None
        self.df = pd.read_csv(csv_path, header=None)
        
        # Clean up: Ensure columns 1 (Speed) and 3 (Steer) are floats
        self.df[speed_column] = pd.to_numeric(self.df[1], errors='coerce')
        self.df[steer_column] = pd.to_numeric(self.df[3], errors='coerce')
        self.df = self.df.dropna(subset=[1, 3, 4]) # Drop rows with missing values
        
        self.img_dir = Path(img_dir)
        self.transform = transform
        self.augment=augment
    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        # According to your head:
        # Index 4 is the image name
        img_name = self.df.iloc[idx, 4]
        img_path = self.img_dir / img_name
        
        image = cv.imread(img_path) 
        image = image.astype(np.float32)
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
       

        # Speed is index 1, Steering is index 3
        speed = self.df.iloc[idx, speed_column]
        steering = self.df.iloc[idx, steer_column]
        
        
       
       

        if self.augment :
            image = torch.flip(image, dims=[2]) # Flip Width dimension
            steering = steering * -1.0
        labels = torch.tensor([speed, steering], dtype=torch.float32) 
        return image, labels

# --- AGENT 2: THE TRAINER ---
class Trainer:
    def __init__(self,data_path,base_path):
        self.base_path = Path("src/four_wheels_robot_nn/four_wheels_robot_nn/data/training_dat")
        self.path_data = self.base_path / f"{data_path}.csv"
        self.path_images = self.base_path / "images"
        self.model_save_path = self.base_path / "robot_model.pth"
        
        self.transform = transforms.Compose([
            transforms.Resize((y_max-y_min, x_max-x_min)),
            transforms.ToTensor(),
        ])

        # Network with 15/30 depths as requested
        self.conv_layers = nn.Sequential(
            nn.Conv2d(conv_attr_1[0],conv_attr_1[1],kernel_size=conv_attr_1[2]["kernel_size"],padding=conv_attr_1[3]["padding"]), 
            nn.ReLU(),
            nn.MaxPool2d(2, 2),                         
            
            nn.Conv2d(conv_attr_2[0],conv_attr_2[1],kernel_size=conv_attr_2[2]["kernel_size"],padding=conv_attr_2[3]["padding"]), 
            nn.ReLU(),
            nn.MaxPool2d(2, 2),                         
            
            nn.Flatten()
        )

        with torch.no_grad():
            dummy = torch.zeros(1,3, y_max-y_min, x_max-x_min)
            n_features = self.conv_layers(dummy).numel()

        self.network = nn.Sequential(
            self.conv_layers,
            nn.Linear(n_features, number_of_neurons_1),
            nn.ReLU(),
            nn.Linear(number_of_neurons_1, number_of_neurons_2),
            nn.ReLU(),
            nn.Linear(number_of_neurons_2,number_of_outputs)
        )

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.network.to(self.device)

    def train(self, epochs=25):
        clean_dataset = RobotDataset(self.path_data, self.path_images, self.transform, augment=False)
        augmented_dataset = RobotDataset(self.path_data, self.path_images, self.transform, augment=True)
        
        # 2. Split indices for train/validation split (80/20)
        total_samples = len(clean_dataset)
        train_size = int(0.8 * total_samples)
        val_size = total_samples - train_size
        
        train_indices, val_indices = random_split(range(total_samples), [train_size, val_size])
        
        # 3. Create subsets from their respective source domains
        train_ds_clean = Subset(clean_dataset, train_indices)
        train_ds_augmented = Subset(augmented_dataset, train_indices)
        
        # 4. CRITICAL FIX: Concatenate the subsets together to duplicate the training size!
        # This takes your 80% dataset and appends the 80% flipped dataset to it. Total = 160%
        train_ds_combined = torch.utils.data.ConcatDataset([train_ds_clean, train_ds_augmented])
        
        # 5. Validation stays strictly clean and un-augmented
        val_ds = Subset(clean_dataset, val_indices)
        train_loader = DataLoader(train_ds_combined, batch_size=32, shuffle=True)
        val_loader = DataLoader(val_ds, batch_size=32, shuffle=False)

        criterion = nn.MSELoss()
        optimizer = optim.Adam(self.network.parameters(), lr=0.001)

        for epoch in range(epochs):
            self.network.train()
            t_loss = 0.0
            
            for imgs, lbls in train_loader:
                
                imgs, lbls = imgs.to(self.device), lbls.to(self.device)
                optimizer.zero_grad()
                loss = criterion(self.network(imgs), lbls)
                loss.backward()
                optimizer.step()
                t_loss += loss.item()

            print(f"Epoch {epoch+1} | Loss: {t_loss/len(train_loader):.6f}")

        torch.save(self.network.state_dict(), self.model_save_path)
        print("Model Saved Successfully.")

if __name__ == "__main__":
    main_logic_cleaner()
    Trainer("data_cleaned","").train(EPOCHS)