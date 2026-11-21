# SeaDrone-Select / 海空小目标检测

> SAHI 切片推理相对整图推理，在 SeaDronesSee 上的小目标检测增益、最优参数区间与代价。
> 固定 YOLOv8n 权重，只改「怎么把图喂给模型」，不改网络结构。

## 这是什么

- **研究问题**：切片推理相对整图推理，APs 与 Recall 是否提升？提升多少？代价几倍？
- **不在范围内**：不改网络结构、不做仿真环境、不做多模态与机载部署、不追求 SOTA

## 环境要求

| 项 | 要求 |
|---|---|
| 系统 | Windows 10/11 64 位（Linux 亦可，命令自行替换） |
| Python | 3.11（conda 环境名 `seadrone`） |
| GPU | NVIDIA，≥8 GB 显存（yolov8n 够用） |
| 磁盘 | ≥50 GB 可用 |
| 数据 | SeaDronesSee v2（YOLO 格式），约 12.7 GB |

## 安装（照着敲，每步都有通过标准）

完整版见 [RUNBOOK.md](RUNBOOK.md)，这里是速览：

```bash
conda create -n seadrone python=3.11 -y
conda activate seadrone
# 按 PyTorch 官网生成命令装 CUDA 版（不要 pip install torch）
pip install ultralytics
pip install "sahi[ultralytics]"
pip freeze > requirements.txt
```

## 数据

```bash
python scripts/download_data.py --out D:\data\SeaDronesSee
```

数据落盘后**只读**：路径写进配置，任何人不得在数据目录内改名或覆盖。

## 一条命令验证环境可用

```bash
python -c "import torch;print(torch.__version__, torch.cuda.is_available())"
```

期望输出 `2.x.x True`。三个值（torch 版本 / cuda 是否可用 / yolo 版本）对不上就是环境没装好。

## 目录结构

```
README.md            # 本文件：陌生人复现的唯一入口
RUNBOOK.md           # 8 步安装流程 + 通过标准 + 常见报错
requirements.txt     # 版本锁定（装好当天就要有）
configs/             # data.yaml、训练与推理配置
scripts/             # 因子统计、评测、SAHI 封装、可视化
results/             # 按实验 ID 分目录（E0/E-1/E1..E4/E6/E7）
report/              # 图表、报告、历史版本
data/                # 只有路径说明，不放数据
```

## 复现一次实验

```bash
# 1) 训练（60 epoch, seed=0）
yolo detect train data=configs/data.yaml model=yolov8n.pt imgsz=640 epochs=60 batch=16 seed=0 optimizer=SGD lr0=0.01

# 2) 验证
yolo detect val model=runs/detect/train/weights/best.pt data=configs/data.yaml imgsz=640

# 3) 记录到实验记录表：一行必须带结论
```

## 数据来源与许可

- 数据集：SeaDronesSee v2，经 HuggingFace 公开镜像获取（以实际下载为准）
- **镜像可下载 ≠ 可任意使用**：许可条款见数据集主页，报告与仓库须注明来源与使用方式
- 本仓库的**代码**采用 [MIT 许可](LICENSE)；数据集不在此许可范围内，仍遵循其原始条款
- 引用本仓库时请注明：项目名 + 仓库地址 + 访问日期

## 仓库纪律

1. 数据与权重不进仓库（见 `.gitignore`）
2. 单文件 >50 MB 走网盘，仓库存路径说明
3. 任何提交前先 pull，避免覆盖队友的记录表
