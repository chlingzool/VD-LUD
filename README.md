# LUD用户文档

## LUD中文文档 (入门级)

### 介绍
**LUD**(*Liny-Universal-Driver*) 是*linyOESOS*伪系统的**通用磁盘文件驱动程序(文件系统)**

#### LUD驱动程序的目标
* 实现一个通用的虚拟磁盘文件驱动程序，它提供统一的接口，使得用户和开发者们可以方便地开发基于LUD的各种文件系统！
* 提供一个完整的、功能丰富的、易于使用的、跨平台的文件系统，它可以满足各种应用的需求！

#### LUD驱动程序的特点
* 完全开源，遵循 *Apache 2.0* 许可证
* 可以将多个文件系统合并成一个虚拟磁盘，并提供统一的接口访问
* 向下兼容，EPT/TESS/FPP无损转移成LUD文件系统的虚拟磁盘文件 (仅在LUD-LS中提供)
* 集成度高，使用方便，易于扩展，可用于各种应用场景 (LUD-LS中提供伪系统文件系统模板)

#### LUD驱动程序的架构
LUD驱动程序由以下几个部分组成：

* **LUD核心** (Main.py/LUD.py/lud.py) - 实现了LUD驱动程序的**所有**功能
* **存储文件** (Others) - 一般为3个或1个 **.ovd**(*Original-Virtual-Disk*) 原始虚拟磁盘文件 **/** **.lud**(*Liny-Universal-Driver*) LUD驱动虚拟磁盘文件

### LUD驱动程序的使用

新手操作：

#### 系统要求
LUD驱动程序的运行环境要求：
* 操作系统：Any
* Python版本：3.11+
* 硬件要求：Any

#### 安装
1. 下载python3.11及以上版本，并安装到系统中
2. 下载LUD驱动程序，解压到任意目录
3. 在安装目录下运行命令：`python lud.py` (或在命令行中运行 `python3 lud.py`)

### 说明

入门级文档，仅包含LUD驱动程序的基本介绍，更详细的使用方法请参考LUD驱动程序的官方开发者文档

#### 接口

接口：(已经实现的访问接口)
```
add_f(name'', path'root', value'') - 添加文件
add_ph(name'', path'root') - 添加路径节点
add_pt(name'', clusters(start, end)) - 添加分区
del_f(name'', IsKillAllValue?) - 删除文件
del_ph(name'') - 删除路径节点
del_pt(name'') - 释放分区
rename_f(old_name'', new_name'') - 重命名文件
rename_ph(old_name'', new_name'') - 重命名路径节点
change_pt(name'', mode'', *Other) - 修改分区属性
move_f(name'', new_path'') - 移动文件
move_ph(name'', new_path'') - 移动路径节点
change_f(name'', mode'', *Other) - 修改文件属性
change_ph(name'', mode'', *Other) - 修改路径节点属性
read_f(name'') - 读取文件内容
list_things(path'') - 列出目录下的文件和路径节点
find_things(name'', path'root') - 查找文件或路径节点
find_aTypeThings(name'', path'root', type'') - 查找指定类型的文件或路径节点
```
属性：
```
=Main - 主属性
==name - 磁盘名称
==label - 磁盘标识符
==main - 磁盘本体
==cluster - 磁盘簇标识
==index - 磁盘索引 (逻辑地址)
==part - 磁盘分区
==tool - 磁盘工具
==root - 磁盘根目录
==dev - 开发者
```

#### 专有名词

* **LUD** - Liny-Universal-Driver，通用磁盘文件驱动程序
* **PATH** - 路径节点，可以看作是文件系统中的文件夹，可以包含文件或其他路径节点
* **c** and **t** - 分别表示簇号和位置号，用于标识磁盘中的位置
* **FILE/file** - 一般 FILE指文件，file指文件系统中的任何类型文件
* **PATH/path** - 一般 PATH指路径节点，path指文件系统中的任何类型路径

# LUD开发者文档

## LUD中文文档 (高级)

### 开发者选项

可以通过设置任何一个选项来开启开发者选项，且
***我们不承担任何责任***

#### 使用说明

任何因开发者选项而导致的功能失效，文件损坏，数据丢失等问题，LUD将不承担任何责任

#### 选项参数

1. **oof** (OnlyOneFile) - 打开后，LUD驱动程序将只允许一个文件存在，即使有多个存储文件 (这会导致原文件无法访问)  
`'oof' : True | False (默认值False)`
2. **elf** (ErrorLogInFile) - 打开后，LUD驱动程序将记录错误信息到文件中  
`'elf' : True | False (默认值False)`  

### 开发者接口

用于调试和开发的接口，仅供开发者使用，不建议普通用户使用，可能会导致文件损坏或数据丢失，请谨慎使用（除非你知道你在做什么）  
LUD不保证开发者接口的稳定性和可用性，请不要依赖开发者接口来实现自己的功能，我们可能会随时修改或删除开发者接口，也不保证开发者接口的兼容性

#### 接口

```
- 方法
link_lexer - LINK文件词法分析器
Error - 错误信息
to_bytes / re_text - 字节转换
file_parent - 文件父目录生成器(p_path)
free_space - 磁盘空间空位查找
type_check - 类型检查器
_cheack - 磁盘自检
_format - 磁盘格式化
save / stroage - 存储文件读写
- 参数
dev.open - DEV状态
```
