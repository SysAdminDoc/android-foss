#!/usr/bin/env python3
import hashlib
import shutil
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
VERSION = "0.0.16"
DIST = ROOT / "dist"
ARCHIVE = DIST / f"android-foss-v{VERSION}.zip"
CHECKSUM = DIST / f"android-foss-v{VERSION}.zip.sha256"
TOP_LEVEL_FILES = (
    "index.html",
    "manifest.webmanifest",
    "sw.js",
    "README.md",
    "LICENSE",
    "catalog.json",
    "catalog-trust.json",
    "catalog-popularity.json",
)


def release_files():
    files = [ROOT / name for name in TOP_LEVEL_FILES]
    files.extend(path for path in (ROOT / "assets").rglob("*") if path.is_file())
    missing = [path for path in files if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"Release input is missing: {missing[0].relative_to(ROOT)}")
    return sorted(files, key=lambda path: path.relative_to(ROOT).as_posix())


def write_archive(files):
    with zipfile.ZipFile(ARCHIVE, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in files:
            relative = path.relative_to(ROOT).as_posix()
            info = zipfile.ZipInfo(relative, date_time=(2026, 9, 12, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes(), compresslevel=9)


def main():
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()
    files = release_files()
    write_archive(files)
    digest = hashlib.sha256(ARCHIVE.read_bytes()).hexdigest().upper()
    CHECKSUM.write_text(f"{digest}  {ARCHIVE.name}\n", encoding="ascii")
    print(f"built {ARCHIVE.name}: {ARCHIVE.stat().st_size} bytes")
    print(f"SHA256 {digest}")


if __name__ == "__main__":
    main()
