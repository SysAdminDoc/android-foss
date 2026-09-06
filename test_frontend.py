import json
import struct
import unittest
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parent
VERSION = "0.0.14"


class AssetParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.scripts = []
        self.stylesheets = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == "script" and values.get("src"):
            self.scripts.append(values["src"])
        if tag == "link" and values.get("rel") == "stylesheet":
            self.stylesheets.append(values.get("href"))


def png_size(path):
    with path.open("rb") as image:
        header = image.read(24)
    if header[:8] != b"\x89PNG\r\n\x1a\n":
        raise AssertionError(f"{path} is not a PNG")
    return struct.unpack(">II", header[16:24])


class FrontendTests(unittest.TestCase):
    def test_catalog_coverage_matches_marketing_copy(self):
        catalog = json.loads((ROOT / "catalog.json").read_text(encoding="utf-8"))
        entries = catalog["entries"]
        self.assertEqual(776, len(entries))
        self.assertEqual(85, len({entry["category"] for entry in entries}))
        self.assertEqual(838, sum(len(entry["storeLinks"]) for entry in entries))
        self.assertEqual(5, sum(entry["category"] == "Calendar" for entry in entries))

    def test_frontend_uses_local_runtime_assets(self):
        parser = AssetParser()
        parser.feed((ROOT / "index.html").read_text(encoding="utf-8"))
        self.assertEqual(["assets/app.js"], parser.scripts)
        self.assertEqual(["assets/styles.css"], parser.stylesheets)
        for relative_path in parser.scripts + parser.stylesheets:
            self.assertTrue((ROOT / relative_path).is_file(), relative_path)

    def test_manifest_and_icons_are_installable(self):
        manifest = json.loads((ROOT / "manifest.webmanifest").read_text(encoding="utf-8"))
        self.assertEqual("Android FOSS", manifest["name"])
        self.assertEqual("standalone", manifest["display"])
        icon_sizes = {icon["sizes"]: ROOT / icon["src"] for icon in manifest["icons"]}
        self.assertEqual((192, 192), png_size(icon_sizes["192x192"]))
        self.assertEqual((512, 512), png_size(icon_sizes["512x512"]))
        self.assertEqual((1024, 1024), png_size(ROOT / "assets/brand/android-foss-mark.png"))

    def test_version_strings_match(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        index = (ROOT / "index.html").read_text(encoding="utf-8")
        script = (ROOT / "assets/app.js").read_text(encoding="utf-8")
        service_worker = (ROOT / "sw.js").read_text(encoding="utf-8")
        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        self.assertIn(f"version-{VERSION}-", readme)
        self.assertIn(f"Android FOSS v{VERSION}", index)
        self.assertIn(f"APP_VERSION = '{VERSION}'", script)
        self.assertIn(f"android-foss-v{VERSION}", service_worker)
        self.assertIn(f"Android FOSS v{VERSION}", changelog)

    def test_public_copy_uses_plain_punctuation(self):
        for name in ("README.md", "CHANGELOG.md", "index.html"):
            text = (ROOT / name).read_text(encoding="utf-8")
            self.assertNotRegex(text, "[—–]", name)
            self.assertNotIn(" - ", text, name)


if __name__ == "__main__":
    unittest.main()
