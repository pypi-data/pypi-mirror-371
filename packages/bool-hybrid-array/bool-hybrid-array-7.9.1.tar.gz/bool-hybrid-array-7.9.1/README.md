# BoolHybridArray：高效的布尔混合数组库

一个专为布尔值优化的数组类，能够根据数据特征自动在密集存储和稀疏存储模式间切换，兼顾性能和内存效率。

7.9.0的介绍有bug，这里修复一下

## 安装方法

使用pip安装：
pip install bool-hybrid-array

## 核心特性

* **智能存储模式**：数据量小的位置使用密集存储numpy.ndarray数组，
* 数据量大的位置为稀疏存储array.array稀疏数组
* 非稀疏模式：数据大部分为非0（True）索引
* 稀疏模式：数据大部分为0（False）索引
* BoolHybridArr函数会自动切换
* **内存高效**：稀疏数据场景下比普通列表节省50%-80%内存
* **操作便捷**：支持类似列表的索引、切片和赋值操作
* **快速统计**：内置高效的计数和布尔判断方法

## 快速开始

### 基本用法

# 导入类

from bool\_hybrid\_array import BoolHybridArr,**TruesArray,FalseArray**

# 创建实例

arr = BoolHybridArr(\[True, False, True, False, True])

**arr2 = TruesArray(3)#7.9.0新增**

**arr3 = FalseArray(3)#7.9.0新增**

# 访问元素

print(arr\[0])  # 输出: True；
print(arr\[1:4])  # 输出:  BoolHybridArr(\[False, True, False])；

print(arr2)  # 输出:  BoolHybridArr(True, True, True])；

print(arr3)  # 输出:  BoolHybridArr(\[False, False, False])；

# 联系方式

* 若遇到 Bug 或有功能建议，可发送邮件至：1289270215@qq.com
* 微信联系：18250730129

# 修改元素

arr\[2] = False
print(arr)  # 输出: BoolHybridArr(\[True, False, False, False, True])

### 存储优化

# 创建包含大量布尔值的数组（大部分为False）

big\_arr = BoolHybridArr(\[i % 100 == 0 for i in range(10000)])

# 查看存储模式（此时应为稀疏模式）

print(repr(big\_arr))  # 输出: BoolHybridArray(split\_index=100,size=10000,is\_sparse=True,small\_len=100,large\_len=)不好意思large\_len我不知道

# 自动优化存储

big\_arr.optimize()

### 统计功能

# 统计True的数量

print(arr.count(True))  # 输出: 2

# 检查是否至少有一个True

print(any(arr))  # 输出: True

# 检查是否全为True

print(all(arr))  # 输出: False
# 复制数组（7.9.1新增）

arr_copy = arr.copy()
arr_copy[0] = False
print(arr[0])      # 输出: True（原数组不变）
print(arr_copy[0]) # 输出: False（拷贝数组已修改）

## 性能优势

在包含100万个布尔值且只有10%为True的场景下
或在包含100万个布尔值且只有10%为False的场景下：

* ###### 普通Python列表：约占用1MB内存
* BoolHybridArray：约占用100KB内存（节省90%）
* 随机访问速度基本保持一致

## 版本历史

* **7.8.13**：PyPI上的初始版本，支持基本功能和自动存储优化
* **7.9.0**：添加TruesArray和FalsesArray
* **7.9.1**：修复介绍的bug，增加copy功能

##**彩蛋：**
- Q：为什么要“密集+稀疏？”
- A：因为在做线性筛的时候遇到了个问题：密集数组太占内存，稀疏数组跑起来卡，所以就做了这个
- Q：为什么要“密集numpy.ndarray，稀疏array.array”？
- A：因为他本来只做线性筛，只修改数组，不insert、pop、remove;稀疏区长度变化平凡，要numpy.ndarray的“**修改就创建新实例**”的话那炸了，所以用array.array,密集区长度不变；所以可以用更高效的numpy.ndarray
- Q：为什么要有TruesArray/FalsesArray？直接用BoolHybridArr(\[True]\*n)/BoolHybridArr(\[False]\*n)不行吗？
- A：因为BoolHybridArr(\[True]\*n)在计算\[True]\*n时如果n太大，那么列表的内存会溢出
- Q：**BoolHybridArr**和**BoolHybridArray**有什么区别？
- A：BoolHybridArray是本库中**唯一一个类**，所有函数都是围绕他进行的，但需要split\_index,size,is\_sparse；
BoolHybridArr是一个**函数**，用于把一个可迭代对象转为BoolHybridArray类

## 许可证
本项目采用**MIT许可证**，详情参见**LICENSE文件**。

