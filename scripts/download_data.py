#!/usr/bin/env python
"""SeaDronesSee 下载器（支持断点续传 + 落盘核验）。

用法：
    python scripts/download_data.py --out D:/data/SeaDronesSee
    python scripts/download_data.py --out D:/data/SeaDronesSee --repo dronefreak/SeaDronesSee

设计要点：
  * 走 huggingface_hub 的 snapshot_download，它天然支持断点续传（重跑即可接着下）
  * 下完立即统计文件数/体积并写 manifest.csv —— 这是 P2 数据核验表的第一列证据
  * 网络断了就重跑同一条命令，不要删目录重下
"""

import argparse
import csv
import os
import sys
from pathlib import Path


def human(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} PB"


def download(repo: str, out: Path) -> None:
    try:
        from huggingface_hub import snapshot_download
    except ImportError:
        print("[!] 缺少依赖，先执行：pip install huggingface_hub", file=sys.stderr)
        sys.exit(2)

    out.mkdir(parents=True, exist_ok=True)
    print(f"[1/3] 仓库 : {repo}")
    print(f"[2/3] 目标 : {out}")
    print("      已下载的部分会自动跳过；中断后重跑本命令即可续传。\n")

    snapshot_download(
        repo_id=repo,
        repo_type="dataset",
        local_dir=str(out),
        max_workers=4,
        resume_download=True,
    )


def verify(out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    files = [p for p in out.rglob("*") if p.is_file()]
    total = sum(p.stat().st_size for p in files)
    print(f"\n[3/3] 落盘核验")
    print(f"      文件数 : {len(files)}")
    print(f"      总体积 : {human(total)}")

    exts = {}
    for p in files:
        exts[p.suffix.lower()] = exts.get(p.suffix.lower(), 0) + 1
    top = sorted(exts.items(), key=lambda kv: -kv[1])[:6]
    print("      类型   : " + ", ".join(f"{k or '(无后缀)'}×{v}" for k, v in top))

    manifest = out / "manifest.csv"
    with open(manifest, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["relpath", "size_bytes"])
        for p in files:
            w.writerow([str(p.relative_to(out)), p.stat().st_size])
    print(f"      manifest: {manifest}")

    for need in ("data", "images", "labels"):
        hit = [p for p in out.rglob("*") if p.is_dir() and p.name.lower() == need]
        print(f"      目录 {need:<7}: {'找到 %d 处' % len(hit) if hit else '未找到 ← 需人工确认'}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, help="落盘目录，如 D:/data/SeaDronesSee")
    ap.add_argument("--repo", default="dronefreak/SeaDronesSee", help="HuggingFace 数据集仓库")
    ap.add_argument("--verify-only", action="store_true", help="只核验，不下载")
    args = ap.parse_args()

    out = Path(args.out).expanduser().resolve()
    if not args.verify_only:
        download(args.repo, out)
    verify(out)
    print("\n下一步：把文件数与体积记进 P2 核验表；数据目录此后只读。")


if __name__ == "__main__":
    main()
