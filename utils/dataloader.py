# dataloader.py

from torch.utils.data import Dataset
import pandas as pd
import os
from torchvision.io import read_image

class ChestXRayDataset(Dataset):
    def __init__(self, annotations_file, img_dir, transform=None):
        # Initialization code here
        self.img_labels = pd.read_csv(annotations_file)
        self.img_dir = img_dir
        self.transform = transform

    def __len__(self):
        # Return the size of dataset

    def __getitem__(self, idx):
        # Logic to load and return a single data point
        # such as an image and its label
