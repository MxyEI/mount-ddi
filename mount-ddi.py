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
  python mount-ddi.py            # 自动匹配 iOS 版本、联网取对应 DDI 并挂载
  python mount-ddi.py --umount   # 卸载
  python mount-ddi.py --list     # 看已挂载镜像
"""
import importlib.util
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


def main(argv):
    if not ensure_dep():
        return 1

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

    print("\n[*] 自动挂载 Developer Disk Image(按设备 iOS 版本联网取对应 DDI)…")
    r = _pmd("mounter", "auto-mount", capture=True)
    combined = (r.stdout or "") + (r.stderr or "")
    print(combined.strip())
    low = combined.lower()

    # 已挂载视为成功。注意:pymobiledevice3 把「设备没连」当作已处理的错误,
    # 只打一条 ERROR 日志、退出码仍是 0,所以不能只看 returncode——
    # 输出里出现 error / not connected / traceback 一律判失败,避免误报成功。
    already = "already mounted" in low or "developerdiskimage already" in low
    errored = any(k in low for k in ("error", "not connected", "traceback", "failed", "no device"))
    if already or (r.returncode == 0 and not errored):
        print("\n[✓] DDI 已就位!现在点开 WDA(WebDriverAgentRunner)即可裸启动跑通。")
        print("    重启设备后 DDI 会掉,重连 USB 再跑一次本脚本。")
        return 0

    print("\n[!] 挂载失败。排查:")
    if "not connected" in low or "no device" in low:
        print("    - 电脑没识别到设备(usbmux 列表为空):")
        print("      · Windows 需装 iTunes 或「Apple 设备」App(提供 Apple Mobile Device Service)")
        print("      · 解锁设备并在弹窗点「信任此电脑」;换原装数据线 / 换 USB 口")
    print("    - 设备没信任此电脑 → 解锁后弹窗点信任,或跑 `pymobiledevice3 lockdown pair`")
    print("    - 没联网 → auto-mount 要从网上取对应 iOS 版本的 DDI")
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
