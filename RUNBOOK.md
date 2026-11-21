# RUNBOOK：从零到「环境可用」（8 步）

> 每一行都写清了**通过标准**。全部 8 步通过，才算环境可用（对应 P1 环境验收单）。
> 同一错误最多重试 1 次；第二次失败就保存完整报错、升级，不要反复重装。

---

## 0. 前置

- Windows 10/11 64 位，**纯英文、无空格**的安装路径（如 `D:\miniconda3`）
- 已装 NVIDIA 驱动（`nvidia-smi` 有输出）
- 已装 Git for Windows（`git --version` 有输出）

---

## 1. 安装 Miniconda

下载 Windows 64 位安装包，安装时勾选 "Add to PATH"（不勾也能用，走 Anaconda Prompt）。

**通过标准**：新开一个终端，输入 `conda --version` 有版本输出。

---

## 2. 创建环境

```bash
conda create -n seadrone python=3.11 -y
conda activate seadrone
```

**通过标准**：`conda env list` 里出现 `seadrone`；命令行前缀变成 `(seadrone)`。

---

## 3. 安装 PyTorch（CUDA 版）

打开 https://pytorch.org/get-started/locally/，选 Windows / Conda 或 Pip / CUDA 12.x，复制它生成的命令执行。

> ⚠️ **不要 `pip install torch`** —— 那会装成 CPU 版，`cuda.is_available()` 永远是 False。

**通过标准**：安装过程无报错。

---

## 4. 验证 GPU

```bash
python -c "import torch;print(torch.__version__, torch.cuda.is_available())"
```

**通过标准**：第二个值是 **True**。

---

## 5. 安装 ultralytics

```bash
pip install ultralytics
yolo version
```

**通过标准**：`yolo version` 有输出。

---

## 6. 安装 SAHI（必须带扩展）

```bash
pip install "sahi[ultralytics]"
python -c "import sahi; print(sahi.__version__)"
```

**通过标准**：`import sahi` 无报错。

> 只装 `sahi` 不装 `sahi[ultralytics]`，推理时会报「找不到检测器」。

---

## 7. 跑通一张图

```bash
yolo detect predict model=yolov8n.pt source=<任意一张图> save=True
```

**通过标准**：生成带框图，框的位置**肉眼正确**。

> 这一步同时验证了三件事：路径对不对、权重能不能下、绘图有没有问题。

---

## 8. 克隆仓库并锁定版本

```bash
git clone <仓库地址> seadrone
cd seadrone
pip freeze > requirements.txt
```

**通过标准**：仓库能 clone；`requirements.txt` 已生成并提交；README 里那条示例命令能跑通。

---

## 常见报错速查（覆盖 80% 的坑）

| 现象 | 原因 | 处理 |
|---|---|---|
| `cuda.is_available()` 为 False | 装成 CPU 版 / CUDA 版本不匹配 | 重装对应 CUDA 版本；先确认驱动版本 |
| `import sahi` 正常但推理报错 | 缺 ultralytics 扩展 | `pip install "sahi[ultralytics]"` |
| 路径报错、文件找不到 | 中文 / 空格 / 相对路径 | 全部改英文绝对路径，写进配置 |
| 框整体偏移 | 坐标未归一化或未还原 | 检查转换脚本的宽高与中心点计算 |
| 图片颜色异常 | OpenCV 是 BGR，PIL 是 RGB | 转换通道顺序 |
| 训练中断 | 网络 / 断电 | 开 `resume`，日志落盘 |

---

## 卡住了怎么办（三级升级）

| 级别 | 先找谁 | 时限 | 适用 |
|---|---|---|---|
| S0 自查 | 本文件、报错搜索 | 立刻 | 90% 的问题在这一级 |
| S1 团队 | 群里提问 + 学长 | 24 h | 数据集格式、指标口径、连续两天无进展 |
| S2 技术负责人 | 微信直发（附完整报错 + 已尝试操作） | 48 h | SAHI / 训练 / 评测脚本相关 |
