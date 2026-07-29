#!/usr/bin/env python3
"""List responsive PyPI indexes in preferred order for the Windows build."""
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed


MIRRORS = (
    ("清华大学", "https://pypi.tuna.tsinghua.edu.cn/simple", True),
    ("阿里云", "https://mirrors.aliyun.com/pypi/simple", True),
    ("腾讯云", "https://mirrors.cloud.tencent.com/pypi/simple", True),
    ("中国科学技术大学", "https://mirrors.ustc.edu.cn/pypi/simple", True),
    ("PyPI 官方", "https://pypi.org/simple", False),
)


def probe(item, timeout=6):
    name, index_url, domestic = item
    request = urllib.request.Request(
        index_url + "/pymobiledevice3/", headers={"User-Agent": "mount-ddi-build/1.0"}
    )
    started = time.monotonic()
    with urllib.request.urlopen(request, timeout=timeout) as response:
        response.read(1)
    return name, index_url, domestic, time.monotonic() - started


def main():
    available = []
    with ThreadPoolExecutor(max_workers=len(MIRRORS)) as executor:
        futures = {executor.submit(probe, item): item for item in MIRRORS}
        for future in as_completed(futures):
            name = futures[future][0]
            try:
                result = future.result()
                available.append(result)
                print("    [OK] %s: %.2f 秒" % (result[0], result[3]), file=sys.stderr)
            except Exception as error:
                reason = str(error).replace("\n", " ")[:80]
                print("    [--] %s: %s" % (name, reason), file=sys.stderr)

    if not available:
        return 1
    domestic = sorted((item for item in available if item[2]), key=lambda item: item[3])
    official = sorted((item for item in available if not item[2]), key=lambda item: item[3])
    for item in domestic + official:
        print(item[1])
    return 0


if __name__ == "__main__":
    sys.exit(main())
