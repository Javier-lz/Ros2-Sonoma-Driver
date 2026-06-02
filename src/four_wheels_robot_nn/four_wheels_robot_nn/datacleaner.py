import pandas as pd
import os
from pathlib import Path
from config import *
def clean_dataset_by_index(csv_path, image_folder):
    # 1. Load CSV with NO header (header=None)
    # This assigns integer names (0, 1, 2, 3, 4) to the columns
    df = pd.read_csv(csv_path, header=None)
    
    # 2. Map the image column index
    # You mentioned it is the 4th column starting at 0 (Index 4)
    IMG_COL_INDEX = 4 
    
    # 3. Get the physical files from the disk
    actual_files = set(os.listdir(image_folder))
    
    # 4. PERFORM THE INNER JOIN
    # Filter where the value in column 4 is present in our file set
    initial_count = len(df)
    df_clean = df[df[IMG_COL_INDEX].isin(actual_files)].copy()
    
    # 5. Result Reporting
    lost_data = initial_count - len(df_clean)
    df_clean=df_clean[df_clean[speed_column]>0.05]
    print(f"Total Rows: {initial_count}")
    print(f"Valid Rows: {len(df_clean)}")
    print(f"Corrupted/Missing Rows Removed: {lost_data}")
    df_steer = df_clean[df_clean[steer_column].abs()>0.2]
    print(len(df_steer)) 
    print(len(df_clean))
    df_straight=df_clean[df_clean[steer_column].abs()<=0.2] 
    df_straight_scaled=df_straight.sample(len(df_steer),random_state=42) 

    
    df_clean =pd.concat([df_straight_scaled,df_steer])
    
    # 6. Save back without adding a new header
    # We use header=False to keep the original "No Header" format
    save_path = csv_path.with_stem(f"{csv_path.stem}_cleaned")
    df_clean.to_csv(save_path, index=False, header=False)
    
    return df_clean

def main_logic_cleaner():
    data = Path.cwd() / "src/four_wheels_robot_nn/four_wheels_robot_nn/data/training_dat/data.csv"
    img = Path.cwd() / "src/four_wheels_robot_nn/four_wheels_robot_nn/data/training_dat/images"
    clean_dataset_by_index(data,img)
