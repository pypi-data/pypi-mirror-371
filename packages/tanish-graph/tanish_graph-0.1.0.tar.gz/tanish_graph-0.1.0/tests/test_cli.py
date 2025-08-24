import subprocess

def test_cli_line_graph():
    result = subprocess.run(
        ["python", "-m", "holograph.cli", "--type", "line", "14", "21", "43"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "1" in result.stdout
