"""Remove the inherited paper rectangle from prepared sponsor artwork (maintenance only)."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAMES = ("partner-column-one", "partner-column-two", "media-logos")
PAPER = b"q /C1 cs .975 .975 .975 scn 0 1080 m 1920 1080 l 1920 0 l 0 0 l h f* Q"
NOTE = "Source full-slide paper rectangle removed; transparent artwork inherits the slide background. Logo vectors, embedded images and transforms are preserved."


def normalize(root=ROOT):
    import pymupdf as fitz

    manifest_path = root / "library/parts/bitpolito/manifest.json"
    manifest = json.loads(manifest_path.read_text())
    hashes = {}
    for name in NAMES:
        part = manifest["parts"][name]
        target = root / part["file"]
        with fitz.open(target) as document:
            matches = []
            for xref in range(1, document.xref_length()):
                if document.xref_is_stream(xref):
                    stream = document.xref_stream(xref)
                    if PAPER in stream:
                        matches.append((xref, stream))
            if not matches and part.get("background_cleanup") == NOTE:
                hashes[part["file"]] = hashlib.sha256(target.read_bytes()).hexdigest()
                continue
            if len(matches) != 1 or matches[0][1].count(PAPER) != 1:
                raise ValueError(f"Unexpected source paper rectangle in {target}")
            xref, stream = matches[0]
            document.update_stream(xref, stream.replace(PAPER, b"", 1))
            temporary = target.with_suffix(".normalized.pdf")
            document.save(temporary, garbage=4, deflate=True)
        temporary.replace(target)
        part.update(sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
                    bytes=target.stat().st_size, background_cleanup=NOTE)
        hashes[part["file"]] = part["sha256"]
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    # Refresh only the resources actually changed by this maintenance operation.
    for relative, section, key in (("templates/index.json", "templates", "prepared_resources"),
                                   ("library/index.json", "slides", "resources")):
        path = root / relative
        data = json.loads(path.read_text())
        entries = data[section]
        for entry in entries.values() if isinstance(entries, dict) else entries:
            resources = entry.get(key, {})
            for filename in resources.keys() & hashes.keys():
                resources[filename] = hashes[filename]
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    print(f"Normalized {len(hashes)} sponsor artwork groups; no logo rasterization.")


if __name__ == "__main__":
    normalize()
