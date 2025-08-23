import os
import re
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from torch.utils.data import Dataset

from zsl_ma.dataset_utils.dataset import FactorLabelMapper


class AttributeImageDataset(Dataset):
    def __init__(self, root_dir, mode, attr_dir, transform=None):
        self.img_dir = Path(root_dir) / mode
        self.transform = transform
        self.images = [f for f in os.listdir(self.img_dir) if f.endswith(('.bmp', '.jpg', '.png'))]
        self.maper = FactorLabelMapper(root_dir)

        self.attr_dir = attr_dir
        self.classes = self.maper.classes

        self.attr_dict =[]
        for cls_name in self.classes:
            npy_path = os.path.join(self.attr_dir, f"{cls_name}.npy")
            self.attr_dict.append(np.load(npy_path, allow_pickle=True))


    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        image_path = os.path.join(self.img_dir, self.images[idx])

        image = Image.open(image_path).convert('RGB')

        if self.transform:
            image = self.transform(image)

        base_filename = os.path.splitext(self.images[idx])[0]
        class_name = base_filename.split('_')[0]
        label = self.maper.get_label_from_class(class_name)

        # 获取对应的语义属性向量
        # attr_vector = self.attr_dict[class_name]

        return image, label # torch.tensor(attr_vector, dtype=torch.float32)

if __name__ == '__main__':
    data = AttributeImageDataset(r'D:\Code\2-ZSL\Zero-Shot-Learning\data\split\单文件夹格式', 'train',
                                 r'D:\Code\2-ZSL\1-output\特征解耦结果\best-3\class_mean_features\fault_combined')
    print(len(data))