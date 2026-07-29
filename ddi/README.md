# 离线 DDI 存放处

把对应 iOS 版本的 DeveloperDiskImage 放这里,`mount-ddi.py --offline` 会按设备
ProductVersion 自动匹配(先精确、再退回 major.minor)。

iOS < 17(dmg + signature 两个文件):

    ddi/15.2/DeveloperDiskImage.dmg
    ddi/15.2/DeveloperDiskImage.dmg.signature

镜像来源:
  - 公开的 DeveloperDiskImage 汇总仓库(GitHub 搜 "DeveloperDiskImage")
  - 装了对应 Xcode 的机器:
    /Applications/Xcode.app/Contents/Developer/Platforms/iPhoneOS.platform/DeviceSupport/<版本>/DeveloperDiskImage.dmg

也可让脚本自动探测国内加速/直连网络并下载到本目录。例如 iOS 15.3.1 自动引用 15.3:

    python mount-ddi.py --download-only --version 15.3.1

终端会打印选中的下载链接、实时进度和最终引用目录。

iOS 15.3.1 使用 15.3 的 DDI，没有单独的 15.3.1 镜像。已有直链也可继续手动下载:

  - https://ghfast.top/https://raw.githubusercontent.com/doronz88/DeveloperDiskImage/main/DeveloperDiskImages/15.3/DeveloperDiskImage.dmg
  - https://ghfast.top/https://raw.githubusercontent.com/doronz88/DeveloperDiskImage/main/DeveloperDiskImages/15.3/DeveloperDiskImage.dmg.signature
  - https://raw.githubusercontent.com/Mythologyli/DeveloperDiskImage/main/15.3/DeveloperDiskImage.dmg
  - https://raw.githubusercontent.com/Mythologyli/DeveloperDiskImage/main/15.3/DeveloperDiskImage.dmg.signature
  - https://raw.githubusercontent.com/filsv/iOSDeviceSupport/master/15.3.zip

手动下载的两个文件可放到 `ddi/15.3/`，然后运行 `python mount-ddi.py --offline`。
