# 知乎book爬虫

## 代码逻辑
### Step1、爬数据
* 爬取封面
* 爬取简介
* 爬取目录
* 爬取章节
> 数据保存到临时文件夹中，以便下次重新生成。

### Step2、生成epub
* 添加封面
* 添加简介
* 添加章节
* 添加章节图片
* 添加导航
* 输出文件

## 使用说明
### 安装依赖包
```bash
pip install -r requirements.txt
```
### 运行脚本
```bash
python3 main.py
```
### 扫码

## TODO
### 参数化