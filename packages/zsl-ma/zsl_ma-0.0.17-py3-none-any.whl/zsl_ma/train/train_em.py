import argparse
import os
import sys

import numpy as np
import torch
from torch.utils.data import DataLoader
from torchvision import transforms
from tqdm import tqdm

from zsl_ma.dataset_utils.em_dataset import AttributeImageDataset
from zsl_ma.models.projection import ProjectionNet, LSELoss
from zsl_ma.tools.tool import get_device, create_next_numbered_folder, make_save_dirs, calculate_metric


def main(configs):
    device = get_device()
    print(f"Using {device.type} device training.")
    save_dir = create_next_numbered_folder(configs.save_dir,configs.prefix)
    img_dir, model_dir = make_save_dirs(save_dir)
    transform = transforms.Compose([transforms.Resize((64, 64)),
                                    transforms.ToTensor(),
                                    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])])

    train_dataset = AttributeImageDataset(configs.data_root, 'train', configs.att_dir, transform=transform)
    val_dataset = AttributeImageDataset(configs.data_root, 'val', configs.att_dir, transform=transform)
    train_loader = DataLoader(train_dataset, batch_size=configs.batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=configs.batch_size, shuffle=False)

    model = ProjectionNet(configs.cnn).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=configs.lr)
    att_np = np.array(train_dataset.attr_dict)  # 合并为单一numpy数组
    att_matrix = torch.tensor(att_np).to(device)  # 从单一numpy数组创建张量，效率更高
    criterion = LSELoss(att_matrix)
    best = -1


    for epoch in range(configs.epochs):
        model.train()
        train_loss = torch.zeros(1).to(device)
        train_iterator = tqdm(train_loader, file=sys.stdout, colour='yellow')
        for step, (images, label) in enumerate(train_iterator):
            images, label = images.to(device), label.to(device)
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, label)
            loss.backward()
            optimizer.step()
            train_loss = (train_loss * step + loss.detach()) / (step + 1)
            train_iterator.set_postfix(loss=loss.item(), mean_loss=train_loss.item())

        print(f'the epoch {epoch + 1} train loss is {train_loss.item():.6f}')
        model.eval()
        val_loss = torch.zeros(1).to(device)
        val_iterator = tqdm(val_loader, file=sys.stdout, colour='MAGENTA')
        all_predictions = []
        all_labels = []
        with torch.no_grad():
            for step, (images, label) in enumerate(val_iterator):
                images = images.to(device)
                outputs = model(images)
                loss = criterion(outputs, label)
                val_loss = (val_loss * step + loss.detach()) / (step + 1)

                distances = torch.cdist(outputs, att_matrix, p=2)
                _, predicted = torch.min(distances, dim=1)
                all_predictions.extend(predicted.cpu().numpy())
                all_labels.extend(label.cpu().numpy())
                val_iterator.set_postfix(loss=loss.item(), mean_loss=val_loss.item())
        print(f'the epoch {epoch + 1} val loss is {val_loss.item():.6f}')
        res = calculate_metric(all_labels, all_predictions, classes=train_dataset.classes)
        print(res)
        if best < res['f1-score']:
            best = res['f1-score']
            torch.save(model.state_dict(), os.path.join(model_dir, 'best.pth'))


def parse_args(args=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lr', type=float, default=0.001, help='learning rate')
    parser.add_argument('--epochs', type=int, default=150, help='number of epochs')
    parser.add_argument('--batch_size', type=int, default=150)
    parser.add_argument('--cnn', type=str, default=r'D:\Code\deep-learning-code\classification\yms_class\run\output1\models\best_model.pth')
    parser.add_argument('--save_dir', type=str, default=r'output')
    parser.add_argument('--att_dir', type=str, default=r'D:\Code\2-ZSL\1-output\特征解耦结果\best-3\class_mean_features\fault_combined')
    parser.add_argument('--data_root', type=str, default=r'D:\Code\2-ZSL\Zero-Shot-Learning\data\split\单文件夹格式')
    parser.add_argument('--prefix', type=str, default='exp')
    return parser.parse_args(args if args else [])

if __name__ == '__main__':
    args = parse_args()
    main(args)
