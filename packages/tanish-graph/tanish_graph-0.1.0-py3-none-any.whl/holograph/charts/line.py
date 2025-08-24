def draw_line(values, height=10, theme="mono", file=None):
    max_val = max(values)
    scale = height / max_val if max_val else 1

    # graph lines
    lines = []
    for v in values:
        level = int(v * scale)
        line = " " * (height - level) + "*" 
        lines.append(line)

    output = "\n".join(lines)

    # ✅ Add values at the bottom
    output += "\n" + " ".join(str(int(v)) for v in values) + "\n"

    if file:
        file.write(output)
    else:
        print(output)
    return output
