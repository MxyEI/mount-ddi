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
