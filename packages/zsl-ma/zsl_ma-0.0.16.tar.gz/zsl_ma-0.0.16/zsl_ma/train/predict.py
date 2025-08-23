import argparse
import os

import numpy as np
import torch
from torch.utils.data import DataLoader
from torchvision import transforms

from zsl_ma.dataset_utils.em_dataset import AttributeImageDataset
from zsl_ma.models.projection import ProjectionNet
from zsl_ma.tools import get_device, calculate_metric


def predict(configs):
    device = get_device()
    print(f"Using {device.type} device training.")
    transform = transforms.Compose([transforms.Resize((64, 64)),
                                    transforms.ToTensor(),
                                    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])])
    test_dataset = AttributeImageDataset(configs.data_root, 'val', configs.att_dir, transform=transform)
    test_loader = DataLoader(test_dataset, batch_size=configs.batch_size, shuffle=False)
    att_np = np.array(test_dataset.attr_dict)  # 合并为单一numpy数组
    att_matrix = torch.tensor(att_np).to(device)  # 从单一numpy数组创建张量，效率更高


    model = ProjectionNet(configs.cnn)
    state_dict = torch.load(os.path.join(configs.model_dir, 'best.pth'))
    model.load_state_dict(state_dict)
    model = model.to(device)
    model.eval()
    all_predictions = []
    all_labels = []
    with torch.no_grad():
        for images, label in test_loader:
            images = images.to(device)
            outputs = model(images)

            distances = torch.cdist(outputs, att_matrix, p=2)
            _, predicted = torch.min(distances, dim=1)
            all_predictions.extend(predicted.cpu().numpy())
            all_labels.extend(label.cpu().numpy())
    res = calculate_metric(all_labels, all_predictions, classes=test_dataset.classes)
    print(res)

def parse_args(args=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--batch_size', type=int, default=150)
    parser.add_argument('--cnn', type=str,
                        default=r'D:\Code\deep-learning-code\classification\yms_class\run\output1\models\best_model.pth')
    parser.add_argument('--att_dir', type=str, default=r'D:\Code\2-ZSL\1-output\特征解耦结果\best-3\class_mean_features\fault_combined')
    parser.add_argument('--data_root', type=str, default=r'D:\Code\2-ZSL\Zero-Shot-Learning\data\split\不可见类')
    parser.add_argument('--model_dir', type=str, default=r'D:\Code\2-ZSL\Zero-Shot-Learning\MA-ZSL\zsl_ma\train\output\exp-1\checkpoints')
    return parser.parse_args(args if args else [])

if __name__ == '__main__':
    args = parse_args()
    predict(args)