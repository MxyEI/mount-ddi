# 一键挂载 DDI(电脑侧,跨平台)

裸启动 WDA 需要 testmanagerd 的 `.control`,而它只在 **Developer Disk Image(DDI)** 挂载后才有。
**Dopamine(rootless)禁裸 mount、`/Developer` 又在密封卷上,设备侧无法固化**,所以用电脑经 USB
走 Apple 授权的 image-mounter 挂(这条不受设备侧限制)。⚠️ **重启后 DDI 会掉,重跑一次即可。**

## 用法

**Windows**:双击 `mount-ddi.bat`(需先装 [Python 3](https://www.python.org/downloads/),安装时勾 *Add to PATH*)。

**macOS / Linux**:
```bash
./mount-ddi.sh
```

首次会自动 `pip install pymobiledevice3`(纯 Python、跨平台的 iOS 设备工具)。

## 前置

1. USB 连接设备、**解锁屏幕**、弹窗点**「信任此电脑」**(没配对过先跑 `pymobiledevice3 lockdown pair`)。
2. iOS 17+ 还需在 **设置 > 隐私与安全 > 开发者模式** 打开。
3. 联网(auto-mount 按设备 iOS 版本从网上取对应 DDI)。

## 命令

```bash
python mount-ddi.py            # 挂载(自动匹配版本)
python mount-ddi.py --list     # 看已挂载镜像
python mount-ddi.py --umount   # 卸载
```

## 挂上之后

点开 **WebDriverAgentRunner** 图标 → WDA 裸启动 → testmanagerd 授权 → 截图/元素树/tap 全通,
HTTP server 监听 `:8100`。控制端 `iproxy 8100:8100` 或同 WiFi 直连。

## 说明

- 只依赖 `pymobiledevice3`(pip),不需要装 Xcode/libimobiledevice,Windows 也能用。
- DDI 由 pymobiledevice3 联网获取(它维护了各 iOS 版本的 DeveloperDiskImage 仓库)。
- 这是"免固化、靠电脑挂一次"的方案 —— 相对设备侧固化更简单可靠;代价是每次重启要重挂。
