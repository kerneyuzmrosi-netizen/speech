# 基于深度神经网络的数字命令语音识别（使用 AISHELL 数据库）

本项目使用 **AISHELL-1** 中文语音数据库，完成一个面向“数字命令”场景的语音识别实验流程。

## 1. 数据库选择

- 语料：AISHELL-1
- 采样率：16kHz
- 目标：在 AISHELL 语料基础上构建/筛选数字命令相关数据，训练并评估识别模型

## 2. 技术路线（DNN-HMM）

1. 数据准备：
   - 下载 AISHELL-1 并完成目录整理
   - 按训练/验证/测试划分样本
   - 提取包含数字命令关键词的数据子集（可选）
2. 特征工程：
   - 提取 FBANK 或 MFCC 特征
   - CMVN 归一化
3. 声学建模：
   - 以 HMM 作为时序建模框架
   - 采用 DNN 估计状态后验概率（DNN-HMM）
4. 解码与评估：
   - 搭建解码图（含语言模型）
   - 使用 CER/WER 进行评估，重点统计数字命令识别准确率

## 3. 已实现脚本

新增 `scripts/prepare_aishell_digits.py`，用于生成训练清单（manifest）：

- `aishell_full.jsonl`：完整语料清单
- `aishell_digit_commands.jsonl`：按关键词过滤后的数字命令子集（可选）

### 用法示例

```bash
python scripts/prepare_aishell_digits.py \
  --aishell-root /path/to/data_aishell \
  --output-dir data/manifests \
  --build-digit-subset
```

自定义关键词（逗号分隔）：

```bash
python scripts/prepare_aishell_digits.py \
  --aishell-root /path/to/data_aishell \
  --output-dir data/manifests \
  --build-digit-subset \
  --keywords "零,一,二,三,四,五,六,七,八,九,十,拨号,呼叫,打开,关闭"
```

## 4. 开发建议

- 语言：Python
- 工具链：PyTorch + Kaldi（或等价流程）
- 结果输出：
  - 训练日志
  - 测试集识别结果
  - 错误样例分析

## 5. 预期成果

- 完成基于 AISHELL 的数字命令语音识别实验
- 给出模型结构、训练流程与实验结果
- 输出论文材料与可复现实验脚本
