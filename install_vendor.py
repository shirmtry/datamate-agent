"""
install_vendor.py — Tải wheel thuần Python từ PyPI và giải nén vào ./vendor
(dùng khi pip bị chặn ghi thư mục Temp).

  python install_vendor.py peft accelerate openpyxl et-xmlfile
"""
import io
import json
import sys
import urllib.request
import zipfile
from pathlib import Path

BASE = Path(__file__).resolve().parent
VENDOR = BASE / "vendor"


def pick_wheel(meta, py_tag="py3"):
    urls = meta["urls"]
    wheels = [u for u in urls if u["filename"].endswith(".whl")]
    pure = [u for u in wheels if "py3-none-any" in u["filename"]]
    if pure:
        return pure[0]
    cp = [u for u in wheels if "cp3" in u["filename"] and "win_amd64" in u["filename"]]
    return (pure or cp or wheels or [None])[0]


def install(name):
    VENDOR.mkdir(exist_ok=True)
    with urllib.request.urlopen(
            urllib.request.Request(f"https://pypi.org/pypi/{name}/json",
                                   headers={"User-Agent": "curl/8"}), timeout=60) as r:
        meta = json.load(r)
    wheel = pick_wheel(meta)
    if not wheel:
        print(f"  ✗ {name}: không có wheel")
        return False
    print(f"  → {name} {meta['info']['version']} ({wheel['filename']}, "
          f"{wheel['size']/1024:.0f} KB)")
    with urllib.request.urlopen(
            urllib.request.Request(wheel["url"], headers={"User-Agent": "curl/8"}), timeout=180) as r:
        data = r.read()
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        z.extractall(VENDOR)
    return True


if __name__ == "__main__":
    for pkg in sys.argv[1:]:
        try:
            install(pkg)
        except Exception as e:
            print(f"  ✗ {pkg}: {e}")
    sys.path.insert(0, str(VENDOR))
    for pkg in sys.argv[1:]:
        mod = pkg.replace("-", "_")
        try:
            m = __import__(mod)
            print(f"  ✅ import {mod} {getattr(m, '__version__', '?')}")
        except Exception as e:
            print(f"  ⚠️ import {mod}: {type(e).__name__}: {e}")
