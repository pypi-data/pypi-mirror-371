# 📊 Holograph

ASCII/Unicode terminal graphs for Python and the command line.  
Easily generate **bar charts** and **line charts** right inside your terminal.

---

## 🔧 Installation

Install from source (development mode):

```bash
git clone https://github.com/yourusername/holograph
cd holograph
pip install -e .
⚡ Quickstart (Python)
from holograph.charts import draw_bar, draw_line

# Bar chart
print(draw_bar([3, 6, 9], height=5))

# Line chart
print(draw_line([1, 4, 2, 5], height=5))

Output (bar):

█
█ █
█ █ █


Output (line):

       *
    *
 *
 💻 CLI Usage

Run directly from the terminal:

# Bar chart
python -m holograph.cli --type bar 3 6 9

# Line chart
python -m holograph.cli --type line 1 2 3 4

# JSON input
python -m holograph.cli --json "[5, 10, 15]"

# CSV input (choose column)
python -m holograph.cli --file data.csv --column value