import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset, random_split
from torchvision import transforms
from pathlib import Path
import pandas as pd
from PIL import Image

# --- AGENT 1: THE DATASET (FIXED COLUMN MAPPING) ---
class RobotDataset(Dataset):
    def __init__(self, csv_path, img_dir, transform=None):
        # Requisite: No header in your data, so we set header=None
        self.df = pd.read_csv(csv_path, header=None)
        
        # Clean up: Ensure columns 1 (Speed) and 3 (Steer) are floats
        self.df[1] = pd.to_numeric(self.df[1], errors='coerce')
        self.df[3] = pd.to_numeric(self.df[3], errors='coerce')
        self.df = self.df.dropna(subset=[1, 3, 4]) # Drop rows with missing values
        
        self.img_dir = Path(img_dir)
        self.transform = transform

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        # According to your head:
        # Index 4 is the image name
        img_name = self.df.iloc[idx, 4]
        img_path = self.img_dir / img_name
        
        image = Image.open(img_path).convert('L')
        
        # Speed is index 1, Steering is index 3
        speed = self.df.iloc[idx, 1]
        steering = self.df.iloc[idx, 3]
        
        labels = torch.tensor([speed, steering], dtype=torch.float32)
        
        if self.transform:
            image = self.transform(image)
            
        return image, labels

# --- AGENT 2: THE TRAINER ---
class Trainer:
    def __init__(self):
        self.base_path = Path("src/four_wheels_robot_nn/four_wheels_robot_nn/data/training_dat")
        self.path_data = self.base_path / "data.csv"
        self.path_images = self.base_path / "images"
        self.model_save_path = self.base_path / "robot_model.pth"

        self.transform = transforms.Compose([
            transforms.Resize((64, 128)),
            transforms.ToTensor(),
        ])

        # Network with 15/30 depths as requested
        self.conv_layers = nn.Sequential(
            nn.Conv2d(1, 15, kernel_size=3, padding=1), 
            nn.ReLU(),
            nn.MaxPool2d(2, 2),                         
            
            nn.Conv2d(15, 30, kernel_size=3, padding=1), 
            nn.ReLU(),
            nn.MaxPool2d(2, 2),                         
            
            nn.Flatten()
        )

        with torch.no_grad():
            dummy = torch.zeros(1, 1, 64, 128)
            n_features = self.conv_layers(dummy).numel()

        self.network = nn.Sequential(
            self.conv_layers,
            nn.Linear(n_features, 512),
            nn.ReLU(),
            nn.Linear(512, 2)
        )

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.network.to(self.device)

    def train(self, epochs=25):
        full_dataset = RobotDataset(self.path_data, self.path_images, self.transform)
        train_size = int(0.8 * len(full_dataset))
        val_size = len(full_dataset) - train_size
        train_ds, val_ds = random_split(full_dataset, [train_size, val_size])

        train_loader = DataLoader(train_ds, batch_size=32, shuffle=True)
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
    Trainer().train()