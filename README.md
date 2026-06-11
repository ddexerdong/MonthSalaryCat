# MonthSalaryCat（月薪喵 OLED 动画）

这是一个 STM32CubeIDE 工程，用于在 128x64 I2C OLED 屏幕上播放黑白月薪喵动画。

## 硬件

- 工程由 STM32CubeMX / STM32CubeIDE 生成
- OLED：GME12864-49，或同类 128x64 SSD1306/SSD1315 I2C 屏幕
- 接线：
  - GND -> GND
  - VCC -> 3.3V
  - SCL -> I2C1_SCL
  - SDA -> I2C1_SDA
- OLED I2C 地址：`0x3C`
- STM32 HAL 中使用的地址写法：`0x3C << 1`

## 工程结构

- `Core/Inc/oled_i2c.h`、`Core/Src/oled_i2c.c`：基于 HAL I2C 的 OLED 驱动
- `Core/Inc/yuexinmiao_oled_frames.h`：生成后的 128x64 OLED 动画帧数据
- `tools/make_yuexinmiao_oled_frames.py`：OLED 帧数据生成脚本
- `assets/yuexinmiao_original.gif`：当前生成脚本使用的素材
- `build/oled_preview/`：电脑端预览 GIF、contact sheet 和逐帧 PNG
- `STM32CubeIDE/`：STM32CubeIDE 工程文件和链接脚本

## 编译和下载

在 STM32CubeIDE 中导入或打开 `STM32CubeIDE` 文件夹，然后执行：

1. 右键项目 Refresh
2. Project -> Clean
3. Build
4. Download / Debug 下载到开发板

## OLED 帧格式

`yuexinmiao_oled_frames.h` 中的帧数据格式为 SSD1306/SSD1315 page order：

- 分辨率：128x64
- 共 8 个 page
- 每个 page 128 字节
- 每帧 1024 字节
- 每个字节表示纵向 8 个像素
- 黑底白线显示

## 重新生成帧数据

```sh
python3 tools/make_yuexinmiao_oled_frames.py
```

脚本会重新生成：

- `Core/Inc/yuexinmiao_oled_frames.h`
- `build/oled_preview/preview.gif`
- `build/oled_preview/contact_sheet.png`
- `build/oled_preview/frame_00.png` 等逐帧预览

当前仓库里的素材是已经预处理过的 128x64 预览 GIF，不是最高质量的原始动画源文件。

## 许可证

本项目中的自写代码使用 MIT License。`Drivers/` 目录中的 ST CMSIS/HAL 文件保留 ST 原始许可证。
