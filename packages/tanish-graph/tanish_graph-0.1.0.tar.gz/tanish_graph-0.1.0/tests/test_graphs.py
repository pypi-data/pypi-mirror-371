import pytest
from holograph.charts import draw_line, draw_bar  # ✅ ab sahi chalega

def test_line_graph_scaling():
    values = [2, 4, 6, 8]
    result = draw_line(values, height=5)
    assert isinstance(result, str)
    assert len(result) > 0

def test_bar_graph_alignment():
    values = [1, 2, 3]
    result = draw_bar(values, height=5)
    assert "|" in result  # bar edge marker
