import sys

import pandas as pd
import torch
from PIL import Image
from tqdm import tqdm

from zsl_ma.tools.distributed_utils import MetricLogger, SmoothedValue, warmup_lr_scheduler
from zsl_ma.tools.tool import generate_image_dataframe


def train_one_epoch(model, train_loader, optimizer, device, criterion, epoch, warmup=True):
    metric_logger = MetricLogger(delimiter="  ")
    metric_logger.add_meter('lr', SmoothedValue(window_size=1, fmt='{value:.6f}'))
    header = f'Train Epoch:[{epoch}]'

    lr_scheduler = None
    if epoch == 0 and warmup is True:  # 当训练第一轮（epoch=0）时，启用warmup训练方式，可理解为热身训练
        warmup_factor = 1.0 / 1000
        warmup_iters = min(1000, len(train_loader) - 1)

        lr_scheduler = warmup_lr_scheduler(optimizer, warmup_iters, warmup_factor)

    train_loss = torch.zeros(1).to(device)
    model.train()

    # train_iterator = tqdm(train_loader, file=sys.stdout, colour='blue', desc=f'the {epoch + 1} epoch is training....')
    for step, (images, indices, label) in enumerate(metric_logger.log_every(train_loader, 50, header)):
        images = images.to(device)

        optimizer.zero_grad()
        predictions, features = model(images)
        loss = torch.zeros(1).to(device)
        for output, feature, index in zip(predictions, features,indices):
            loss += criterion(output, index.to(device))
            ortho_loss = model.orthogonal_regularization(feature.to(device), index.to(device))
            loss = loss + ortho_loss

        loss.backward()
        optimizer.step()

        if lr_scheduler is not None:
            lr_scheduler.step()

        train_loss = (train_loss * step + loss.detach()) / (step + 1)
        # train_iterator.set_postfix(loss=loss.item(), mean_loss=train_loss.item())
        metric_logger.update(loss=train_loss)
        now_lr = optimizer.param_groups[0]["lr"]
        metric_logger.update(lr=now_lr)

    return train_loss.item()


@torch.no_grad()
def val_one_epoch(model, val_loader, device, criterion, epoch):
    metric_logger = MetricLogger(delimiter="  ")
    header = 'Validation Epoch: [{}]'.format(epoch)

    val_loss = torch.zeros(1).to(device)
    model.eval()
    all_predictions = []
    all_labels = []

    # factor_preds = {
    #     'condition': {'pred': [], 'true': []},
    #     'fault_type': {'pred': [], 'true': []},
    #     'severity': {'pred': [], 'true': []}
    # }
    # test_iterator = tqdm(val_loader, file=sys.stdout, colour='blue', desc=f'the {epoch + 1} epoch is val....')
    for step, (images, indices, label) in enumerate(metric_logger.log_every(val_loader, 50, header)):
        images, label = images.to(device), label.to(device)
        # outputs = model(images)
        predictions, features = model(images)
        loss = torch.zeros(1).to(device)

        predicted_indices = []

        # 计算损失并获取每个因子的预测索引
        for output, feature, index in zip(predictions, features, indices):
            loss += criterion(output, index.to(device))
            _, predicted = torch.max(output, 1)
            predicted_indices.append(predicted)  # 保存预测的因子索引
            ortho_loss = model.orthogonal_regularization(feature.to(device), index.to(device))
            loss = loss + ortho_loss

        # 堆叠预测的三因子索引 [batch_size, 3]
        # ortho_loss = model.orthogonal_regularization(features)
        # loss = loss + ortho_loss
        predicted_indices = torch.stack(predicted_indices, dim=1).cpu().numpy()
        # 转换为最终预测的label
        pred_labels = val_loader.dataset.maper.get_labels_from_indices_batch(predicted_indices)

        all_predictions.extend(pred_labels)

        val_loss = (val_loss * step + loss.detach()) / (step + 1)

        # test_iterator.set_postfix(loss=loss.item(), mean_loss=val_loss.item())

        all_labels.extend(label.cpu().numpy())
        metric_logger.update(loss=val_loss)



        # # 解析真实三因子索引 (来自原始indices)
        # true_indices = torch.stack(indices, dim=1).cpu().numpy()  # [batch_size, 3]
        #
        # # 分别记录三因子的预测和真实值
        # for i in range(len(predicted_indices)):
        #     # 预测的三因子索引
        #     cond_pred, fault_pred, sev_pred = predicted_indices[i]
        #     # 真实的三因子索引
        #     cond_true, fault_true, sev_true = true_indices[i]
        #
        #     factor_preds['condition']['pred'].append(cond_pred)
        #     factor_preds['condition']['true'].append(cond_true)
        #     factor_preds['fault_type']['pred'].append(fault_pred)
        #     factor_preds['fault_type']['true'].append(fault_true)
        #     factor_preds['severity']['pred'].append(sev_pred)
        #     factor_preds['severity']['true'].append(sev_true)


    return val_loss, all_predictions, all_labels

# def train_one_epoch(model, train_loader, optimizer, device, criterion, epoch):
#     train_loss = torch.zeros(1).to(device)
#     cls_loss_total = torch.zeros(1).to(device)
#     ortho_loss_total = torch.zeros(1).to(device)
#     intra_loss_total = torch.zeros(1).to(device)
#
#     model.train()
#
#     train_iterator = tqdm(train_loader, file=sys.stdout, colour='blue', desc=f'the {epoch + 1} epoch is training....')
#     for step, (images, indices, labels) in enumerate(train_iterator):
#         images = images.to(device)
#         indices = [idx.to(device) for idx in indices]  # 每个属性的标签列表
#         # 创建属性标签张量 [batch_size, num_attributes]
#         attribute_labels = torch.stack(indices, dim=1)
#
#         optimizer.zero_grad()
#         predictions, features = model(images)
#
#         # 计算分类损失
#         cls_loss = torch.zeros(1).to(device)
#         for i, pred in enumerate(predictions):
#             cls_loss += criterion(pred, indices[i])
#
#         # 计算正交正则损失 (属性间解耦)
#         ortho_loss = model.orthogonal_regularization(features)
#
#         # 计算同类相关性损失 (属性内聚集)
#         intra_loss = model.intra_attribute_correlation(features, attribute_labels)
#
#         # 总损失 = 分类损失 + 正交损失 + 同类相关损失
#         total_loss = cls_loss + ortho_loss + intra_loss
#
#         # 反向传播
#         total_loss.backward()
#         optimizer.step()
#
#         # 更新损失统计
#         train_loss = (train_loss * step + total_loss.detach()) / (step + 1)
#         cls_loss_total = (cls_loss_total * step + cls_loss.detach()) / (step + 1)
#         ortho_loss_total = (ortho_loss_total * step + ortho_loss.detach()) / (step + 1)
#         intra_loss_total = (intra_loss_total * step + intra_loss.detach()) / (step + 1)
#
#         # 更新进度条
#         train_iterator.set_postfix(
#             total_loss=total_loss.item(),
#             cls_loss=cls_loss.item(),
#             ortho_loss=ortho_loss.item(),
#             intra_loss=intra_loss.item(),
#             mean_loss=train_loss.item()
#         )
#
#     return train_loss.item()
#
# @torch.no_grad()
# def val_one_epoch(model, val_loader, device, criterion, epoch):
#     val_loss = torch.zeros(1).to(device)
#     cls_loss_total = torch.zeros(1).to(device)
#     ortho_loss_total = torch.zeros(1).to(device)
#     intra_loss_total = torch.zeros(1).to(device)
#
#     model.eval()
#     all_predictions = []
#     all_labels = []
#     # 属性内相似度统计
#     intra_sim_metrics = {
#         'condition': [],
#         'fault_type': [],
#         'severity': []
#     }
#
#     test_iterator = tqdm(val_loader, file=sys.stdout, colour='blue', desc=f'the {epoch + 1} epoch is val....')
#     for step, (images, indices, labels) in enumerate(test_iterator):
#         images = images.to(device)
#         indices = [idx.to(device) for idx in indices]
#         # 创建属性标签张量 [batch_size, num_attributes]
#         attribute_labels = torch.stack(indices, dim=1)
#
#         predictions, features = model(images)
#
#         # 计算分类损失
#         cls_loss = torch.zeros(1).to(device)
#         for i, pred in enumerate(predictions):
#             cls_loss += criterion(pred, indices[i])
#
#         # 计算正交正则损失
#         ortho_loss = model.orthogonal_regularization(features)
#
#         # 计算同类相关性损失
#         intra_loss = model.intra_attribute_correlation(features, attribute_labels)
#
#         # 总损失
#         total_loss = cls_loss + ortho_loss + intra_loss
#
#         # 更新损失统计
#         val_loss = (val_loss * step + total_loss.detach()) / (step + 1)
#         cls_loss_total = (cls_loss_total * step + cls_loss.detach()) / (step + 1)
#         ortho_loss_total = (ortho_loss_total * step + ortho_loss.detach()) / (step + 1)
#         intra_loss_total = (intra_loss_total * step + intra_loss.detach()) / (step + 1)
#
#         # 获取预测结果
#         predicted_indices = []
#         for output in predictions:
#             _, predicted = torch.max(output, 1)
#             predicted_indices.append(predicted)
#
#         # 堆叠预测的三因子索引 [batch_size, 3]
#         predicted_indices = torch.stack(predicted_indices, dim=1).cpu().numpy()
#         # 转换为最终预测的label
#         pred_labels = val_loader.dataset.maper.get_labels_from_indices_batch(predicted_indices)
#         all_predictions.extend(pred_labels)
#         all_labels.extend(labels)
#
#         # 计算每个属性内的相似度
#         for attr_idx, attr_name in enumerate(['condition', 'fault_type', 'severity']):
#             feat = features[attr_idx]
#             attr_labels = attribute_labels[:, attr_idx]
#             unique_labels = torch.unique(attr_labels)
#
#             for label in unique_labels:
#                 # 提取同类样本特征
#                 class_mask = (attr_labels == label)
#                 class_feat = feat[class_mask]
#
#                 if class_feat.size(0) < 2:
#                     continue
#
#                 # 计算类内特征均值
#                 class_mean = class_feat.mean(dim=0, keepdim=True)
#
#                 # 计算类内特征与均值的余弦相似度
#                 norm_feat = F.normalize(class_feat, p=2, dim=1)
#                 norm_mean = F.normalize(class_mean, p=2, dim=1)
#
#                 intra_sim = torch.sum(norm_feat * norm_mean, dim=1)
#                 intra_sim_metrics[attr_name].extend(intra_sim.cpu().numpy().tolist())
#
#         # 更新进度条
#         test_iterator.set_postfix(
#             loss=total_loss.item(),
#             mean_loss=val_loss.item()
#         )
#
#     # 打印属性内相似度统计
#     print("\n属性内特征相似度统计:")
#     for attr_name, sim_list in intra_sim_metrics.items():
#         if sim_list:
#             avg_sim = sum(sim_list) / len(sim_list)
#             print(f"  {attr_name}: 平均相似度 = {avg_sim:.4f}")
#         else:
#             print(f"  {attr_name}: 无有效样本计算相似度")
#
#     return val_loss, all_predictions, all_labels


def merge_to_192d(features):
    """
    将3个64维张量拼接为192维向量。
    参数：features - 长度为3的列表，每个元素是64维张量（支持(64,)或(1,64)形状）。
    返回：192维张量（形状: (192,)）。
    """
    # 1. 统一处理每个张量的形状（挤压为1D）
    processed = []
    for tensor in features:
        # 挤压多余维度（如(1,64) → (64,)）
        squeezed = tensor.squeeze()
        processed.append(squeezed)

    # 2. 沿特征维度拼接（3个64维 → 192维）
    merged = torch.cat(processed, dim=0)
    return merged


@torch.no_grad()
def predict(model, data_dir, device, transform, image_subdir):
    """
    模型预测函数，返回DataFrame格式的预测结果（n行×m列）

    参数:
    - n: 取top-n预测结果
    - idx_to_labels: 类别索引到名称的映射字典
    - classes: 所有类别名称列表
    """
    model.eval()
    df_data, maper = generate_image_dataframe(data_dir, image_subdir)
    condition_features = []
    fault_type_features = []
    severity_features = []
    df_pred = pd.DataFrame()
    att = []
    for inx, row in tqdm(df_data.iterrows()):
        img_path = row['图片路径']
        img_pil = Image.open(img_path).convert('RGB')
        input_img = transform(img_pil).to(device)  # 预处理
        input_img = input_img.unsqueeze(0)
        pred_logits,features = model(input_img)  # 执行前向预测，得到所有类别的 logit 预测分数
        predicted_indices = []

        for pred_logit in pred_logits:
            pred_softmax = torch.softmax(pred_logit, dim=1)
            _, predicted = torch.max(pred_softmax, 1)
            predicted_indices.append(predicted.cpu())  # 保存预测的因子索引

        condition_features.append(features[0].squeeze().detach().cpu().numpy())
        fault_type_features.append(features[1].squeeze().detach().cpu().numpy())
        severity_features.append(features[2].squeeze().detach().cpu().numpy())
        att.append(merge_to_192d(features).squeeze().detach().cpu().numpy())

        # 转换为最终预测的label
        predicted_indices = torch.stack(predicted_indices, dim=1).numpy()
        pred_label = maper.get_labels_from_indices_batch(predicted_indices)
        pred_dict = {
            '类别预测ID': pred_label[0] if len(pred_label) == 1 else pred_label,
            '工况预测ID': predicted_indices[0, 0] if len(predicted_indices) == 1 else predicted_indices[:, 0],
            '故障类型预测ID': predicted_indices[0, 1] if len(predicted_indices) == 1 else predicted_indices[:, 1],
            '故障程度预测ID': predicted_indices[0, 2] if len(predicted_indices) == 1 else predicted_indices[:, 2]
        }
        df_pred = pd.concat([df_pred, pd.DataFrame([pred_dict])], ignore_index=True)

    df = pd.concat([df_data, df_pred], axis=1)

    return df, condition_features, fault_type_features, severity_features, att


def train_cae_one_epoch(model, train_loader, val_loader, device, optimizer, criterion, epoch):
    result = {'train_loss': 0., 'val_loss': 0., 'epoch': 0}
    train_loss = torch.zeros(1).to(device)
    model.train()
    train_iterator = tqdm(train_loader, file=sys.stdout, colour='yellow')
    for step, (images, label) in enumerate(train_iterator):
        images = images.to(device)

        optimizer.zero_grad()

        outputs = model(images)

        loss = criterion(outputs, images)

        loss.backward()
        optimizer.step()

        train_loss = (train_loss * step + loss.detach()) / (step + 1)
        train_iterator.set_postfix(loss=loss.item(), mean_loss=train_loss.item())

    print(f'the epoch {epoch + 1} train loss is {train_loss.item():.6f}')
    val_loss = torch.zeros(1).to(device)
    model.eval()
    val_iterator = tqdm(val_loader, file=sys.stdout, colour='MAGENTA')
    with torch.no_grad():
        for step, (images, label) in enumerate(val_iterator):
            images = images.to(device)

            outputs = model(images)
            loss = criterion(outputs, images)
            val_loss = (val_loss * step + loss.detach()) / (step + 1)

            val_iterator.set_postfix(loss=loss.item(), mean_loss=val_loss.item())
    print(f'the epoch {epoch + 1} val loss is {val_loss.item():.6f}')
    result['train_loss'] = train_loss.item()
    result['val_loss'] = val_loss.item()
    result['epoch'] = epoch + 1
    return result


@torch.no_grad()
def extract_features_from_csv(model, csv_path, device, transform):
    """
    根据CSV文件中的图片路径提取对应图片的特征（不处理异常，出错直接终止）

    参数:
    - model: 训练好的模型（输出格式为 (预测logits, 特征列表)）
    - csv_path: 包含图片路径的CSV文件路径（需有"图片路径"列）
    - device: 运行设备（如torch.device('cuda')）
    - transform: 图片预处理变换
    """
    model.eval()
    condition_features = []
    fault_type_features = []
    severity_features = []

    # 读取CSV文件
    df = pd.read_csv(csv_path)
    if "图片路径" not in df.columns:
        raise ValueError("CSV文件必须包含'图片路径'列")

    # 遍历图片路径提取特征（无异常处理）
    for idx, row in tqdm(df.iterrows(), total=len(df), desc="提取特征"):
        img_path = row["图片路径"]

        # 加载图片并预处理（无异常捕获，出错直接报错）
        img_pil = Image.open(img_path).convert("RGB")
        input_img = transform(img_pil).to(device)
        input_img = input_img.unsqueeze(0)

        # 前向传播获取特征
        pred_logits, features = model(input_img)

        # 提取并保存特征
        condition_features.append(features[0].squeeze().detach().cpu().numpy())
        fault_type_features.append(features[1].squeeze().detach().cpu().numpy())
        severity_features.append(features[2].squeeze().detach().cpu().numpy())

    return condition_features, fault_type_features, severity_features
