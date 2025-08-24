import argparse
import sys
import json
import csv
from io import StringIO
from .charts import draw_bar, draw_line


def parse_values(args):
    """Parse values from CLI args (JSON, CSV, stdin, or direct values)."""
    if args.json:
        return json.loads(args.json)

    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            values = []
            col = args.column
            for row in reader:
                if col and col in row:
                    values.append(float(row[col]))
                else:
                    for v in row.values():
                        try:
                            values.append(float(v))
                            break
                        except ValueError:
                            continue
            return values

    if args.values == ["-"]:  # read from stdin
        data = sys.stdin.read().strip()
        return [float(x) for x in data.split()]

    return [float(v) for v in args.values]


def render_graph(args, values):
    """Render graph as ASCII string."""
    buffer = StringIO()
    if args.type == "bar":
        output = draw_bar(values, height=10, theme=args.theme)
    else:
        output = draw_line(values, height=10, theme=args.theme)
    buffer.write(output)
    return buffer.getvalue()


def main():
    parser = argparse.ArgumentParser(description="Holograph: Graphs in terminal")
    parser.add_argument("--type", choices=["bar", "line"], default="bar", help="Type of graph")
    parser.add_argument("--theme", choices=["mono", "bright", "hud"], default="mono", help="Theme")
    parser.add_argument("--file", help="CSV file to read values from")
    parser.add_argument("--column", help="Column name in CSV")
    parser.add_argument("--json", help="JSON array as input")
    parser.add_argument("--out", help="Output file (e.g. graph.txt or graph.png)")
    parser.add_argument("values", nargs="*", help="Values for graph or '-' for stdin")

    args = parser.parse_args()
    values = parse_values(args)
    output = render_graph(args, values)

    if args.out:
        if args.out.endswith(".txt"):
            with open(args.out, "w", encoding="utf-8") as f:
                f.write(output)
            print(f"[✔] Graph exported to {args.out}")

        elif args.out.endswith(".png"):
            try:
                from PIL import Image, ImageDraw, ImageFont

                lines = output.splitlines()
                font = ImageFont.load_default()
                width = max(font.getbbox(line)[2] for line in lines)
                height = len(lines) * 15  # 15px per line
                img = Image.new("RGB", (width + 20, height + 20), "black")
                draw = ImageDraw.Draw(img)

                for i, line in enumerate(lines):
                    draw.text((10, i * 15), line, font=font, fill="lime")

                img.save(args.out)
                print(f"[✔] Graph exported as image: {args.out}")
            except ImportError:
                sys.exit("[Error] Pillow is required for PNG export. Install with `pip install pillow`.")

        else:
            sys.exit("[Error] Output file must be .txt or .png")
    else:
        # ✅ Directly print to stdout for CLI usage and tests
        print(output)


if __name__ == "__main__":
    main()
