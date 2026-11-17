"""Assemble the notebook from the three cell modules."""
from pathlib import Path

import nbformat as nbf

from nb_cells_part1 import CELLS as PART1
from nb_cells_part2 import CELLS as PART2
from nb_cells_part3 import CELLS as PART3

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "Restaurant_Data_Visualization.ipynb"

cells = []
for kind, text in PART1 + PART2 + PART3:
    if kind == "md":
        cells.append(nbf.v4.new_markdown_cell(text))
    else:
        cells.append(nbf.v4.new_code_cell(text))

nb = nbf.v4.new_notebook(cells=cells)
nb.metadata = {
    "kernelspec": {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3",
    },
    "language_info": {
        "name": "python",
        "version": "3.11",
        "mimetype": "text/x-python",
        "file_extension": ".py",
    },
    "colab": {
        "provenance": [],
        "toc_visible": True,
        "name": "Restaurant_Data_Visualization.ipynb",
    },
}

nbf.validate(nb)
nbf.write(nb, OUT)
print(f"Wrote {OUT}")
print(f"Cells: {len(cells)}  (markdown: {sum(c[0] == 'md' for c in PART1 + PART2 + PART3)}, "
      f"code: {sum(c[0] == 'code' for c in PART1 + PART2 + PART3)})")
