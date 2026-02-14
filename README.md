# N_m3u8DL-RE-GUI

基于 [N_m3u8DL-RE](https://github.com/nilaoda/N_m3u8DL-RE) 的图形用户界面工具。

## 项目简介

N_m3u8DL-RE-GUI 是一个为 [N_m3u8DL-RE](https://github.com/nilaoda/N_m3u8DL-RE) 提供图形用户界面的工具，使用户能够更方便地使用 N_m3u8DL-RE 下载 m3u8 格式的视频流。该工具采用 MVC 架构设计，提供了直观易用的界面，支持多任务下载管理。

## 功能特性

- **图形化界面**：提供友好的 GUI 界面，无需命令行操作
- **多任务管理**：支持同时管理多个下载任务
- **实时日志**：实时显示下载过程日志
- **配置保存**：自动保存用户配置，方便下次使用
- **临时文件清理**：自动清理下载产生的临时文件
- **任务状态监控**：实时监控任务下载状态
- **自动跳转**：添加任务后自动跳转到任务管理界面

## 依赖要求

- Python 3.7+
- Tkinter（Python 标准库）
- [N_m3u8DL-RE](https://github.com/nilaoda/N_m3u8DL-RE) 可执行文件

## 安装使用

1. 确保已安装 Python 3.7+
2. 下载 [N_m3u8DL-RE](https://github.com/nilaoda/N_m3u8DL-RE) 的可执行文件，并放置在项目根目录
3. 运行主程序：
```bash
python main.py
```

## 主要功能

### 任务配置
- 输入 URL 或文件路径
- 设置保存目录和文件名
- 配置临时目录
- 调整下载线程数、重试次数等参数

### 任务管理
- 添加、删除、清空任务
- 开始/停止指定任务
- 查看任务状态和日志
- 实时监控下载进度

### 高级设置
- 请求头设置
- 解密设置
- 混流设置
- 轨道选择

## 项目结构

```
N_m3u8DL-RE-GUI/
├── controllers/          # 控制器层
│   └── main_controller.py
├── models/               # 模型层
│   ├── config_manager.py
│   ├── task_builder.py
│   └── task_manager.py
├── views/                # 视图层
│   ├── advanced_settings_view.py
│   └── main_view.py
├── main.py               # 主程序入口
├── m3u8dl_config.json    # 配置文件
└── N_m3u8DL-RE.exe       # N_m3u8DL-RE 可执行文件
```

## 原始项目

本项目基于 [nilaoda](https://github.com/nilaoda) 开发的 [N_m3u8DL-RE](https://github.com/nilaoda/N_m3u8DL-RE) 工具。

## 许可证

请参阅原始项目 [N_m3u8DL-RE](https://github.com/nilaoda/N_m3u8DL-RE) 的许可证信息。