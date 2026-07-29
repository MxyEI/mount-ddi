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

### 打包成独立 exe(目标机免装 Python)

在**一台装了 Python 3 的 Windows** 上双击 `build-windows.bat`,即可把整套工具(含
`pymobiledevice3`)打成单文件 `dist\mount-ddi.exe`。把这个 exe 拷到任意 Windows 机器双击运行,
**无需安装 Python**。

- 打包过程:自动建打包用虚拟环境 `.build-venv` → 装 `pyinstaller` + `pymobiledevice3` → 按
  `mount-ddi.spec` 输出 `dist\mount-ddi.exe`。需联网。
- exe 也支持参数:`mount-ddi.exe --list` / `mount-ddi.exe --umount`。
- 首次安装依赖会自动探测清华、阿里云、腾讯云、中科大镜像，按响应速度依次尝试可用国内源，
  全部失败后才回退 PyPI 官方源；
  后续打包直接复用 `.build-venv`，不会每次强制升级、重复下载。
- 需要更新依赖时运行 `build-windows.bat --upgrade-deps`。也可在运行前设置
  `MOUNT_DDI_PYPI_INDEX`，手动指定企业内网或其他 PyPI 镜像。

## 前置

1. USB 连接设备、**解锁屏幕**、弹窗点**「信任此电脑」**(没配对过先跑 `pymobiledevice3 lockdown pair`)。
2. iOS 17+ 还需在 **设置 > 隐私与安全 > 开发者模式** 打开。
3. 联网(脚本按设备 iOS 版本探测可用下载源并缓存对应 DDI)。

## 命令

```bash
python mount-ddi.py            # 挂载(自动匹配版本,联网取 DDI)
python mount-ddi.py --download-only --version 15.3.1  # 只下载并缓存,暂不挂载
python mount-ddi.py --offline  # 离线挂:用本地 DDI,免联网(网络慢/无网时用)
python mount-ddi.py --list     # 看已挂载镜像
python mount-ddi.py --umount   # 卸载
```

## 离线挂载(免联网)

联网 `auto-mount` 慢或没网时,把 DDI 放本地按版本挂。iOS<17 是 `dmg` + `.signature` 两个文件,
放到脚本旁 `ddi/<iOS版本>/`:

```
ddi/15.2/DeveloperDiskImage.dmg
ddi/15.2/DeveloperDiskImage.dmg.signature
```

然后 `python mount-ddi.py --offline`(按设备 ProductVersion 自动匹配:如先精确 `15.3.1`,再退回 `15.3`)。
也可显式指定:`python mount-ddi.py --image X.dmg --sig X.dmg.signature`。

镜像来源:公开的 DeveloperDiskImage 汇总仓库,或装了对应 Xcode 的机器
`.../iPhoneOS.platform/DeviceSupport/<版本>/DeveloperDiskImage.dmg`。

## 自动下载与国内网络

iOS 17 以下默认不再隐藏在 `pymobiledevice3 auto-mount` 中下载。脚本会并发探测以下入口，
按探测响应速度选择下载源；下载中实时打印链接、引用/保存目录、百分比、大小和速度，失败后
自动切换下一个源：

- 国内加速：`ghfast.top`、`gh-proxy.com`、`ghproxy.net`
- 直连回退：`raw.githubusercontent.com`

文件取自 `pymobiledevice3` 使用的
[`doronz88/DeveloperDiskImage`](https://github.com/doronz88/DeveloperDiskImage) 仓库。
例如 iOS `15.3.1` 会自动匹配 `15.3`，缓存到 `ddi/15.3/`，以后运行直接复用。

只下载指定版本、不连接设备：

```bash
python mount-ddi.py --download-only --version 15.3.1
```

也可用 `--ddi-dir <目录>` 修改下载及引用目录。

## 挂上之后

点开 **WebDriverAgentRunner** 图标 → WDA 裸启动 → testmanagerd 授权 → 截图/元素树/tap 全通,
HTTP server 监听 `:8100`。控制端 `iproxy 8100:8100` 或同 WiFi 直连。

## 说明

- 只依赖 `pymobiledevice3`(pip),不需要装 Xcode/libimobiledevice,Windows 也能用。
- DDI 来自 pymobiledevice3 使用的 DeveloperDiskImage 仓库，并由本脚本多源下载及缓存。
- 这是"免固化、靠电脑挂一次"的方案 —— 相对设备侧固化更简单可靠;代价是每次重启要重挂。
