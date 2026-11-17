"""Execute the notebook in place so the .ipynb carries all outputs and figures."""
from pathlib import Path
import sys

import nbformat
from jupyter_client.kernelspec import KernelSpecManager
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parent.parent
NB_PATH = ROOT / "Restaurant_Data_Visualization.ipynb"

specs = KernelSpecManager().find_kernel_specs()
if "python3" not in specs:
    from ipykernel.kernelspec import install
    install(user=True, replace=True)
    print("Installed python3 kernelspec")

nb = nbformat.read(NB_PATH, as_version=4)
client = NotebookClient(
    nb,
    timeout=900,
    kernel_name="python3",
    allow_errors=False,
    resources={"metadata": {"path": str(ROOT)}},
)
print(f"Executing {NB_PATH.name} ...")
client.execute()
nbformat.write(nb, NB_PATH)

code_cells = [c for c in nb.cells if c.cell_type == "code"]
errors = [
    (i, out) for i, c in enumerate(code_cells)
    for out in c.get("outputs", []) if out.get("output_type") == "error"
]
print(f"Executed {len(code_cells)} code cells. Errors: {len(errors)}")
print("Saved:", NB_PATH)
sys.exit(1 if errors else 0)
