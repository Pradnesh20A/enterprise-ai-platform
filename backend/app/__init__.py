"""Enterprise AI Document Intelligence Platform."""

import os

# Set OMP_NUM_THREADS to 1 to prevent segmentation faults with FAISS/OpenMP on macOS
# and to prevent PyTorch from fighting over CPU threads in Uvicorn workers.
os.environ["OMP_NUM_THREADS"] = "1"
