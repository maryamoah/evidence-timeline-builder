import json
import argparse
from pathlib import Path
from datetime import datetime


def parse_time(ts: str) -> datetime:
    """
    Parse ISO 8601 timestamps safely.
    """
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return datetime.min


def build_timeline(manifest_path: Path):
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    events = []
    for item in manifest:
        events.append(
            {
                "time": parse_time(item.get("collected_at", "")),
                "file": item.get("file"),
                "size": item.get("size"),
                "hash": item.get("sha256"),
            }
        )

    events.sort(key=lambda x: x["time"])
    return events


def write_outputs(events, out_prefix: str):
    # Markdown timeline
    md_lines = ["# Evidence Timeline", ""]
    for e in events:
        ts = e["time"].isoformat()
        md_lines.append(f"- **{ts}** — `{e['file']}` ({e['size']} bytes)")

    Path(f"{out_prefix}.md").write_text("\n".join(md_lines), encoding="utf-8")

    # CSV timeline
    csv_lines = ["timestamp,file,size,sha256"]
    for e in events:
        csv_lines.append(f"{e['time'].isoformat()},{e['file']},{e['size']},{e['hash']}")

    Path(f"{out_prefix}.csv").write_text("\n".join(csv_lines), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(
        description="Build a timeline from an evidence manifest.json file."
    )
    ap.add_argument("manifest", help="Path to manifest.json")
    ap.add_argument(
        "-o",
        "--output",
        default="timeline",
        help="Output filename prefix (default: timeline)",
    )
    args = ap.parse_args()

    events = build_timeline(Path(args.manifest))
    write_outputs(events, args.output)

    print(f"[+] Timeline written to {args.output}.md and {args.output}.csv")


if __name__ == "__main__":
    main()
