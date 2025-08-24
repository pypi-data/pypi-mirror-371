# ABetter
## 一、简介

ABetter 是一个在 Jupyter Notebook 中计算 A/B-Testing 效果的简单易用的 Python 工具包，其基于**样本统计结果**而非样本明细，因此无需导入样本，很适合用于大规模样本实验。

主要功能：

1. 自适应选择检验方法；
2. 输出检验表：显著性, 置信区间，MDE，Effect Size，增量效果；
3. 绘制示意图。

## 二、安装

源代码托管在 GitHub，地址: [https://github.com/SqRoots/ABetter](https://github.com/SqRoots/ABetter)。

您可以使用 pip 命令安装 ABetter。

```bash
# PyPI
pip install abetter
```

## 三、使用

### 3.1 计算AB实验效果

检验均值型指标：

```python
import abetter as ab

# 定义均值型指标样本（其中样本量n、样本均值mean、样本标准差std，是3个必要参数，其他为可选参数）
s1 = ab.SampleMean(n=1000000, mean=0.5000, std=0.2000, field_name='订单量', group_name='实验组', group_ratio=0.1, report_title="AB实验结果")
s2 = ab.SampleMean(n=2000000, mean=0.5005, std=0.2010, field_name='订单量', group_name='空白组', group_ratio=0.2)

# 检验
ss = s1 - s2
ss   # Pandas数据框存储于 ss.data_all
```

<img src="./img/image-20250621105540539.png" alt="image-20250621105540539" style="zoom:50%;" />

检验比率型指标：

```python
import abetter as ab

# 定义比率型指标样本（其中样本量n、阳性样本量k，是2个必要参数，其他为可选参数）
s1 = ab.SampleProp(n=10000, k=60, field_name='交易人数', group_name='实验组', group_ratio=0.1, report_title="AB实验结果")
s2 = ab.SampleProp(n=20000, k=50, field_name='交易人数', group_name='空白组', group_ratio=0.2)

# 检验
ss = s1 - s2
ss   # Pandas数据框存储于 ss.data_all
```

<img src="./img/image-20250621105640703.png" alt="image-20250621105640703" style="zoom:50%;" />

### 3.2 绘图

绘制两个样本均值的分布：

```python
import abetter as ab

# 定义均值型指标样本（前3个参数依次是：样本量n、样本均值mean、样本标准差std）
s1 = ab.SampleMean(1000, 0.50, 0.20)
s2 = ab.SampleMean(200, 0.55, 0.21)

# 绘图
fig, ax = ab.plot_two_mean(s1, s2)
fig
```

<img src="./img/image-20250621110055582.png" alt="image-20250621110055582" style="zoom:50%;" />

绘制两个样本均值之差的分布：

```python
import abetter as ab

# 定义均值型指标样本（前3个参数依次是：样本量n、样本均值mean、样本标准差std）
s1 = ab.SampleMean(1000, 0.50, 0.20)
s2 = ab.SampleMean(200, 0.55, 0.21)

# 绘图
fig, ax = ab.plot_diff_mean(s1 - s2)
fig
```

<img src="./img/image-20250621110204152.png" alt="image-20250621110204152" style="zoom:50%;" />

### 3.3 计算并绘制MDE曲线

计算并绘制**均值型样本**的MDE曲线：

```python
import abetter as ab

# 两组样本比例，例如一组样本量占比 20%，另一组样本量占比 80% 时
n_ratio=(20,80)
# 最小的那组样本量范围（对于本例，是指20的那一组样本量取数范围）
n_min_range=(10000,20000)
# 计算并绘制均值型样本的MDE曲线：
f, a, mde = ab.plot_mde_mean_sample(
    std1=1, std2=1,           # 两组样本的样本标准差
    n_ratio=n_ratio,          # 样本量比例
    n_min_range=n_min_range,  # 最小那一组样本量的取值范围
    test='t',                 # 检验方法：仅支持 z 和 t 两种
    equal_var=True            # 方差是否相等：仅对 t 检验有效
)
f
```

<img src="./img/image-20250824145308932.png" alt="image-20250824145308932" style="zoom:50%;" />

计算并绘制**比率型样本**的MDE曲线

```python
import abetter as ab

# 两组样本比例，例如一组样本量占比 20%，另一组样本量占比 80% 时
n_ratio=(20,80)
# 最小的那组样本量范围（对于本例，是指20的那一组样本量取数范围）
n_min_range=(10000,20000)
# 绘图并计算MDE
f, a, mde = ab.plot_mde_prop_sample(
    prop=0.2,                 # 阳性样本占比（根据经验估计），并认为原假设成立（H0: prop1 == prop2）
    n_ratio=n_ratio,          # 样本量比例
    n_min_range=n_min_range   # 最小那一组样本量的取值范围
)
f
```

<img src="./img/image-20250824145915547.png" alt="image-20250824145915547" style="zoom:50%;" />

计算并绘制**比率型样本**的MDE曲线（可能遇到的问题）

由于本工具使用Z检验计算比率型样本的MDE，当阳性样本占比太小或太大时，要求样本量足够大（**每一组的阳性样本和阴性样本都不能低于10个**），否则比率并不服从正态分布，MDE曲线会呈现锯齿状，结果不可信！这时需要使用其他检验方法（例如 Fisher 精确检验），或者提高 n_min_range 的取值范围。

下面是一个阳性样本占比和样本量都过小的例子，将 n_min_range 调整为(10000,50000)之后MDE曲线将不在有锯齿。

```python
import abetter as ab

n_ratio=(20,80)
n_min_range=(100,500)                # 对于prop=0.01，几百个样本太少了，比率不服从正态分布
f, a, mde = ab.plot_mde_prop_sample(
    prop=0.01,                       # 太小了
    n_ratio=n_ratio,
    n_min_range=n_min_range
)
f
```

<img src="./img/image-20250824150547847.png" alt="image-20250824150547847" style="zoom:50%;" />

## todo

- [x] 功能：计算最小样本量
- [ ] 功能：调研小样本比率检验如何科学的计算置信区间、MDE。
- [ ] 绘图：统计功效
- [ ] 输出：补充`__repr__`和`__str__`
- [ ] 文档：参考文献与相关公式
