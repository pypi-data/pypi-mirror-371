def draw_bar(values, height=10, theme="mono", file=None):
    max_val = max(values)
    scale = height / max_val if max_val else 1

    # graph rows (top to bottom)
    rows = []
    for h in range(height, 0, -1):
        row = ""
        for v in values:
            row += "|" if int(v * scale) >= h else " "
            row += " "
        rows.append(row)

    output = "\n".join(rows)

    # ✅ Add values at the bottom
    output += "\n" + " ".join(str(int(v)) for v in values) + "\n"

    if file:
        file.write(output)
    else:
        print(output)
    return output
