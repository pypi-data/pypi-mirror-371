# BoolHybridArray：高效的布尔混合数组库

一个专为布尔值优化的数组类，能够根据数据特征自动在密集存储和稀疏存储模式间切换，兼顾性能和内存效率。

## 安装方法

使用pip安装：
pip install bool-hybrid-array
## 核心特性

- **智能存储模式**：数据量小的位置使用密集存储numpy.ndarray数组，
- 数据量大的位置为稀疏存储array.array稀疏数组
- 非稀疏模式：数据大部分为非0（True）索引
- 稀疏模式：数据大部分为0（False）索引
- BoolHybridArr函数会自动切换
- **内存高效**：稀疏数据场景下比普通列表节省50%-80%内存
- **操作便捷**：支持类似列表的索引、切片和赋值操作
- **快速统计**：内置高效的计数和布尔判断方法

## 快速开始

### 基本用法
# 导入类
from bool_hybrid_array import BoolHybridArr

# 创建实例
arr = BoolHybridArr([True, False, True, False, True])

# 访问元素
print(arr[0])  # 输出: True
print(arr[1:4])  # 输出: [False, True, False]

# 联系方式
- 若遇到 Bug 或有功能建议，可发送邮件至：1289270215@qq.com
# 修改元素
arr[2] = False
print(arr)  # 输出: BoolHybridArr([True, False, False, False, True])
### 存储优化
# 创建包含大量布尔值的数组（大部分为False）
big_arr = BoolHybridArr([i % 100 == 0 for i in range(10000)])

# 查看存储模式（此时应为稀疏模式）
print(repr(big_arr))  # 输出: BoolHybridArray(size=10000, mode=sparse, true_count=100)

# 自动优化存储
big_arr.optimize()
### 统计功能
# 统计True的数量
print(arr.count(True))  # 输出: 2

# 检查是否至少有一个True
print(any(arr))  # 输出: True

# 检查是否全为True
print(all(arr))  # 输出: False
## 性能优势

在包含100万个布尔值且只有10%为True的场景下：
或在包含100万个布尔值且只有10%为False的场景下
- 普通Python列表：约占用1MB内存
- BoolHybridArray：约占用100KB内存（节省90%）
- 随机访问速度基本保持一致
## 版本历史

- 0.1.0：初始版本，支持基本功能和自动存储优化

## 许可证

本项目采用MIT许可证，详情参见LICENSE文件。