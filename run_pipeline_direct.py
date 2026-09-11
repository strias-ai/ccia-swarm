import sys
import os
sys.path.append("/home/k1/ccia_workspace/modules")
from art_63 import TriSwarmOrchestrator

if __name__ == "__main__":
    orch = TriSwarmOrchestrator()
    orch.run_full_pipeline()
