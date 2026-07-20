#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一键给 USB 连接的 iOS 设备挂载 Developer Disk Image(DDI)。跨平台:Windows / macOS / Linux。

为什么需要它:
  裸启动 WDA 需要 testmanagerd 的 .control 服务,而它只在 DDI 挂载后才存在。
  Dopamine(rootless)禁掉了裸 mount 语法、/Developer 又在密封卷上,无法在设备侧固化;
  所以用电脑经 USB 走 Apple 授权的 image-mounter 挂(这条不受设备侧 mount 限制)。
  ⚠️ 重启后 DDI 会掉,重连 USB 再跑一次本脚本即可。

依赖:pymobiledevice3(纯 Python,自动 pip 安装)。设备需先"信任此电脑"。

用法:
  python mount-ddi.py                       # 自动匹配 iOS 版本、联网取对应 DDI 并挂载
  python mount-ddi.py --offline             # 离线挂:用本地 DDI(免联网)
  python mount-ddi.py --image X.dmg --sig X.dmg.signature   # 离线挂,显式指定文件
  python mount-ddi.py --umount              # 卸载
  python mount-ddi.py --list                # 看已挂载镜像

离线 DDI 从哪来:
  · 本地放一份 DeveloperDiskImage(iOS<17 是 dmg + .signature 两个文件),按版本放到
    脚本旁的 ddi/<iOS版本>/ 目录,例如:
        ddi/15.2/DeveloperDiskImage.dmg
        ddi/15.2/DeveloperDiskImage.dmg.signature
    --offline 会按设备 ProductVersion(先精确 15.2,再退回 15.x)自动匹配。
  · 镜像可从公开的 DeveloperDiskImage 仓库下载(如 github 上的 iOS DDI 汇总仓库),
    或从装了对应 Xcode 的机器 /Applications/Xcode.app/.../DeviceSupport/<版本>/ 拷。
"""
import importlib.util
import json
import os
import subprocess
import sys

# 打包成 exe(PyInstaller)后,靠这个哨兵参数让 exe 把自己当作 pymobiledevice3 CLI 来跑。
_PMD_FLAG = "--__run_pymobiledevice3__"
_FROZEN = getattr(sys, "frozen", False)


def _has(mod):
    return importlib.util.find_spec(mod) is not None


def _pmd(*args, capture=False):
    """调 pymobiledevice3 子命令。"""
    if _FROZEN:
        # exe 里没有 `python -m`,改成重新调用自身、走内置的 pymobiledevice3 分发器。
        cmd = [sys.executable, _PMD_FLAG, *args]
    else:
        cmd = [sys.executable, "-m", "pymobiledevice3", *args]
    print("  $ pymobiledevice3", *args)
    if capture:
        return subprocess.run(cmd, capture_output=True, text=True)
    return subprocess.run(cmd)


def ensure_dep():
    if _FROZEN or _has("pymobiledevice3"):
        return True  # exe 已内置 pymobiledevice3,无需 pip
    print("[*] 未装 pymobiledevice3,自动安装中(需联网)…")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-U", "pymobiledevice3"])
        return True
    except Exception as e:
        print("[!] 自动安装失败。请手动执行:  pip install -U pymobiledevice3")
        print("   ", e)
        return False


def _here():
    """脚本(或 exe)所在目录。"""
    if _FROZEN:
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def _device_version():
    """取第一台 USB 设备的 iOS 版本(ProductVersion),取不到返回 None。"""
    r = _pmd("usbmux", "list", capture=True)
    try:
        data = json.loads(r.stdout or "[]")
        if data:
            return data[0].get("ProductVersion")
    except Exception:
        pass
    return None


def _find_local_ddi(version, ddi_dir):
    """在 ddi_dir 下按版本找 DeveloperDiskImage.dmg + .signature。先精确、再退回 major.minor。"""
    base = ddi_dir or os.path.join(_here(), "ddi")
    tries = []
    if version:
        tries.append(version)                                   # 15.2.1
        tries.append(".".join(version.split(".")[:2]))          # 15.2
    seen, cands = set(), []
    for v in tries:
        if v and v not in seen:
            seen.add(v)
            cands.append(v)
    for v in cands:
        d = os.path.join(base, v)
        img = os.path.join(d, "DeveloperDiskImage.dmg")
        sig = img + ".signature"
        if os.path.isfile(img) and os.path.isfile(sig):
            return img, sig
    return None, None


def _mount_flag_form():
    """探测本机 pymobiledevice3 的 `mounter mount` 参数形式(各版本不一)。"""
    h = _pmd("mounter", "mount", "--help", capture=True)
    text = (h.stdout or "") + (h.stderr or "")
    img_flag = next((f for f in ("--image", "-x", "-i") if f in text), None)
    sig_flag = next((f for f in ("--signature", "-s") if f in text), None)
    return img_flag, sig_flag


def mount_offline(image, sig):
    """用本地 DDI 文件挂载(免联网)。跨版本:优先带 flag,退回位置参数。"""
    if not (os.path.isfile(image) and os.path.isfile(sig)):
        print("[!] 找不到镜像或签名文件:")
        print("    image:", image)
        print("    sig  :", sig)
        return 1
    print("\n[*] 离线挂载 Developer Disk Image(本地文件、免联网):")
    print("    image:", image)
    print("    sig  :", sig, "\n")
    img_flag, sig_flag = _mount_flag_form()
    if img_flag and sig_flag:
        r = _pmd("mounter", "mount", img_flag, image, sig_flag, sig)
    else:
        # 老/新版本可能收位置参数:mounter mount <image> <signature>
        r = _pmd("mounter", "mount", image, sig)

    # 复查是否真挂上(退出码不可全信)。
    q = _pmd("mounter", "list", capture=True)
    if q.returncode != 0:
        q = _pmd("mounter", "query", capture=True)
    if "developer" in ((q.stdout or "") + (q.stderr or "")).lower():
        print("\n[✓] DDI 已就位(离线)!点开 WDA 即可裸启动。重启后重挂一次即可。")
        return 0
    print("\n[!] 离线挂载失败。排查:")
    print("    - 镜像/签名与设备 iOS 版本不匹配(必须严格对应)")
    print("    - 设备没解锁 / 没信任此电脑(先 `pymobiledevice3 lockdown pair`)")
    print("    - 镜像文件损坏或下载不完整,重新下载")
    return r.returncode or 1


def _arg_value(argv, name):
    """取 --name VALUE 形式的值,没有返回 None。"""
    if name in argv:
        i = argv.index(name)
        if i + 1 < len(argv):
            return argv[i + 1]
    return None


def main(argv):
    if not ensure_dep():
        return 1

    # 显式指定文件即走离线;否则 --offline 触发自动找本地 DDI。
    image = _arg_value(argv, "--image")
    sig = _arg_value(argv, "--sig") or _arg_value(argv, "--signature")
    ddi_dir = _arg_value(argv, "--ddi-dir")
    if image or sig or "--offline" in argv:
        if not (image and sig):
            ver = _device_version()
            print("[*] 设备 iOS 版本:", ver or "(未取到)")
            found_img, found_sig = _find_local_ddi(ver, ddi_dir)
            image = image or found_img
            sig = sig or found_sig
        if not (image and sig):
            base = ddi_dir or os.path.join(_here(), "ddi")
            print("[!] 没找到本地 DDI。请把镜像放到:")
            print("      %s/<iOS版本>/DeveloperDiskImage.dmg" % base)
            print("      %s/<iOS版本>/DeveloperDiskImage.dmg.signature" % base)
            print("    或用 --image X.dmg --sig X.dmg.signature 显式指定。")
            return 1
        return mount_offline(image, sig)

    if "--list" in argv:
        # 不同版本子命令名可能是 list 或 query;两个都试。
        r = _pmd("mounter", "list", capture=True)
        if r.returncode != 0:
            r = _pmd("mounter", "query", capture=True)
        print(((r.stdout or "") + (r.stderr or "")).strip())
        return r.returncode
    if "--umount" in argv or "--unmount" in argv:
        return _pmd("mounter", "umount").returncode

    # 设备检测仅提示、不拦(输出格式各版本不一);真正判定交给 auto-mount。
    print("[*] 连接的设备(需已解锁 + 信任此电脑):")
    _pmd("usbmux", "list")

    # 先查一次是否已挂载:已挂就别再跑 auto-mount(它对已挂设备会报错或干等)。
    q = _pmd("mounter", "list", capture=True)
    if q.returncode != 0:
        q = _pmd("mounter", "query", capture=True)
    qlow = ((q.stdout or "") + (q.stderr or "")).lower()
    if "developer" in qlow or "com.apple.developer" in qlow:
        print("\n[✓] 检测到 DDI 已挂载,无需重复挂。点开 WDA 即可裸启动。")
        return 0

    print("\n[*] 自动挂载 Developer Disk Image(按设备 iOS 版本联网取对应 DDI)…")
    print("    ⏳ iOS<17 首次要联网下载 DeveloperDiskImage,网络慢时几分钟很正常;下方是实时日志:\n")
    # 关键:实时流式(不 capture),下载进度可见,避免「看着卡住」的错觉。
    r = _pmd("mounter", "auto-mount")

    if r.returncode == 0:
        # auto-mount 退出码 0 不一定真挂上(设备没连它也可能返回 0),复查一次。
        q2 = _pmd("mounter", "list", capture=True)
        if q2.returncode != 0:
            q2 = _pmd("mounter", "query", capture=True)
        if "developer" in ((q2.stdout or "") + (q2.stderr or "")).lower():
            print("\n[✓] DDI 已就位!现在点开 WDA(WebDriverAgentRunner)即可裸启动跑通。")
            print("    重启设备后 DDI 会掉,重连 USB 再跑一次本脚本。")
            return 0
    low = ""

    print("\n[!] 挂载失败。排查:")
    if "not connected" in low or "no device" in low:
        print("    - 电脑没识别到设备(usbmux 列表为空):")
        print("      · Windows 需装 iTunes 或「Apple 设备」App(提供 Apple Mobile Device Service)")
        print("      · 解锁设备并在弹窗点「信任此电脑」;换原装数据线 / 换 USB 口")
    print("    - 设备没信任此电脑 → 解锁后弹窗点信任,或跑 `pymobiledevice3 lockdown pair`")
    print("    - 没联网 / 下载太慢 → 改用离线挂:python mount-ddi.py --offline")
    print("      (先把 DDI 放到 ddi/<iOS版本>/,详见脚本顶部说明)")
    print("    - iOS 17+ 需开发者模式(设置>隐私与安全>开发者模式)")
    return r.returncode or 1


def _run_as_pymobiledevice3():
    """冻结态下,把自身当作 `python -m pymobiledevice3` 执行。"""
    import multiprocessing

    multiprocessing.freeze_support()
    from pymobiledevice3.__main__ import main as pmd_main

    sys.argv = ["pymobiledevice3", *sys.argv[2:]]  # 去掉 exe 路径和哨兵参数
    pmd_main()


if __name__ == "__main__":
    if _FROZEN and len(sys.argv) > 1 and sys.argv[1] == _PMD_FLAG:
        _run_as_pymobiledevice3()
        sys.exit(0)
    sys.exit(main(sys.argv[1:]))
