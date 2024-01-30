from torch.utils.data import DataLoader
from utils.dataloader import ChestXRayDataset
from torchvision import transforms

transform = transforms.Compose([
    transforms.Resize((224, 224)),  # Resize the image to 224x224 pixels
    transforms.ToTensor(),          # Convert the image to a PyTorch tensor
    # Add any other transformations here.
    # For example, for data augmentation:
    # transforms.RandomHorizontalFlip(),
    # transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

# Assuming you have defined transforms
dataset = ChestXRayDataset(annotations_file='path/to/annotations.csv', img_dir='path/to/images', transform=transform)

dataloader = DataLoader(dataset, batch_size=64, shuffle=True)
