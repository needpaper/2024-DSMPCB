import os
import re
import random
import numpy as np
import pandas as pd
import torch
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
import joblib
from model import LSTM_MultiheadAttention

# 提取设计特征
def extract_features_from_filename(filename):
    pattern = r'tem(\d+)_d(\d+)result_radius(\d+)_angle(\d+).csv'
    match = re.match(pattern, filename)
    if match:
        return [int(match.group(1)), int(match.group(2)), int(match.group(3)), int(match.group(4))]
    else:
        return None

# 主程序
if __name__ == "__main__":
    # 配置路径
    data_dir = "H:\\pythonProject\\NNbasedSurrogateModel20241127\\dataexp1-CTLT\\alldata"
    saved_model_path = "trained_models/model_epoch_500.pt"
    scaler_dir = "H:\\pythonProject\\NNbasedSurrogateModel20241127\\dataexp1-CTLT\\scalers"  # 保存标准化器的路径
    save_plot_dir = "plots"
    max_length = 21  # 固定插值长度

    # 自定义绘图参数
    font_size = 14  # 字体大小
    legend_labels = ["Original", "Predicted"]  # 图例内容
    xlabel = "Angle(rad)"  # x 轴标签
    ylabel = "Moment(Nm)"  # y 轴标签

    # 检查模型路径
    if not os.path.exists(saved_model_path):
        print(f"Model not found: {saved_model_path}")
        exit()

    # 检查标准化器路径
    scaler_x_path = os.path.join(scaler_dir, 'scaler_x.pkl')
    scaler_y_path = os.path.join(scaler_dir, 'scaler_y.pkl')
    if not os.path.exists(scaler_x_path) or not os.path.exists(scaler_y_path):
        print(f"Scalers not found in {scaler_dir}. Please ensure they are saved during training.")
        exit()

    # 加载标准化器
    scaler_x = joblib.load(scaler_x_path)
    scaler_y = joblib.load(scaler_y_path)
    print("Scalers loaded successfully.")

    # 加载模型
    model = LSTM_MultiheadAttention(input_size=4, hidden_size=64, output_size=22, num_heads=4)
    model.load_state_dict(torch.load(saved_model_path))
    model.eval()

    # 随机选择文件进行预测
    all_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    if not all_files:
        print("No CSV files found in the directory.")
        exit()

    if not os.path.exists(save_plot_dir):
        os.makedirs(save_plot_dir)

    for i in range(100):  # 循环预测 100 次
        random_file = random.choice(all_files)
        random_file_path = os.path.join(data_dir, random_file)

        # 提取设计特征
        features = extract_features_from_filename(random_file)
        if features is None:
            print(f"File name does not match the pattern: {random_file}")
            continue

        print(f"Iteration {i + 1}: Selected File: {random_file}")
        print(f"Extracted Design Features: {features}")

        # 加载数据
        data = pd.read_csv(random_file_path)
        x_original = data.iloc[:, 0].values  # 第一列为 x
        y_original = data.iloc[:, 1].values / 1000  # 第二列为 y，并进行单位转换

        # 插值 y 数据到 max_length
        x_new = np.linspace(0, 1, max_length)
        y_interpolated = np.interp(x_new, np.linspace(0, 1, len(y_original)), y_original)

        # 归一化特征
        features_normalized = scaler_x.transform([features])

        # 模型预测
        input_tensor = torch.tensor(features_normalized, dtype=torch.float32).unsqueeze(0)  # 添加 batch 维度
        with torch.no_grad():
            y_predicted_normalized = model(input_tensor).numpy().flatten()

        # 反归一化预测结果
        y_predicted = scaler_y.inverse_transform(y_predicted_normalized.reshape(1, -1)).flatten()

        # 提取预测的最大位移和插值曲线
        max_displacement_pred = y_predicted[-1]
        y_interpolated_pred = y_predicted[:-1]

        # 生成预测曲线的 x 坐标
        x_predicted = np.linspace(0, max_displacement_pred, max_length)

        # 绘制对比曲线
        plt.figure(figsize=(10, 6))
        plt.plot(x_original, y_original, label=legend_labels[0], color="blue", linewidth=2)
        plt.plot(x_predicted, y_interpolated_pred, label=legend_labels[1], linestyle="--", color="orange", linewidth=2)
        plt.title(f"Iteration {i + 1}: Comparison of Original and Predicted Curves", fontname="Times New Roman", fontsize=font_size)
        plt.xlabel(xlabel, fontname="Times New Roman", fontsize=font_size)
        plt.ylabel(ylabel, fontname="Times New Roman", fontsize=font_size)
        plt.legend(fontsize=font_size, loc="best", frameon=False)
        plt.xticks(fontsize=font_size, fontname="Times New Roman")
        plt.yticks(fontsize=font_size, fontname="Times New Roman")
        plt.tight_layout()

        # 保存绘图
        plot_save_path = os.path.join(save_plot_dir, f"comparison_{i + 1}_{random_file.replace('.csv', '.png')}")
        plt.savefig(plot_save_path, dpi=300, bbox_inches="tight")
        plt.close()

        print(f"Comparison plot saved to: {plot_save_path}")

