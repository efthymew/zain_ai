import ubjson
import os
import slippi
import shutil

import torch
from torch.utils.data import Dataset, DataLoader
import numpy as np

from slippi.id import CSSCharacter
from slippi.event import Frame


# [stage, character, ports, curr frame, damage,
#  marth dmg, marth stock, marth jumps left, marth shield size, marth positionx, marth positiony, cstickx, csticky, joyx, joyy, marth buttons bits, marthl float, marthr float,
#  p2 dmg, p2 stocks, p2 jumps left, p2 shield size, p2x, p2y]
# 
# [marth inputs]

class FrameDataset(Dataset):
    def __init__(self, frame_list, zain_port):
        for i in range(len(frame_list) - 1):
            sequences.append(frame_list[i])
            next_frame = frame_list[i + 1]
            target = [next_frame.player1_x, next_frame.player1_y, next_frame.player1_health, next_frame.player1_velocity]
            targets.append(target)
    
    def __len__(self):
        return len(self.sequences)
    
    def __getitem__(self, idx):
        sequence = self.sequences[idx]
        target = self.targets[idx]
        
        # Convert list of Frame objects to a numpy array
        sequence_data = np.array([[
            frame.actions, frame.player1_x, frame.player1_y, frame.player2_x, frame.player2_y,
            frame.player1_health, frame.player2_health, frame.player1_velocity, frame.player2_velocity
        ] for frame in sequence], dtype=np.float32)
        
        # Convert to tensor
        sequence_tensor = torch.tensor(sequence_data, dtype=torch.float32)
        
        # Extract the inputs of player1 for the next frame
        target_tensor = torch.tensor(target, dtype=torch.float32)
        
        return sequence_tensor, target_tensor
    
origin = "zain_games"



for root, dirs, files in os.walk(origin):
    for file in files:
        file_path = os.path.join(root, file)
        with open(file_path, "rb") as f:
            try:
                game = slippi.Game(f)
            except:
                continue

            print("hi")
