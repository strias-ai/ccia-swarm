# -*- coding: utf-8 -*-
"""
CCIA INFERENCE VRAM PROFILER v1.0
Mide tokens por segundo y velocidad de inferencia en la APU Radeon 780M.
"""
import time

class VRAMProfiler:
    def __init__(self):
        self.start_time = None

    def start(self):
        self.start_time = time.time()

    def stop(self, token_count: int = 100) -> dict:
        if not self.start_time:
            return {"tps": 0.0, "elapsed": 0.0}
        elapsed = time.time() - self.start_time
        tps = token_count / elapsed if elapsed > 0 else 0.0
        return {"tps": round(tps, 2), "elapsed": round(elapsed, 2)}

if __name__ == "__main__":
    p = VRAMProfiler()
    p.start()
    time.sleep(0.1)
    res = p.stop(15)
    print(f"📊 Profiler Inferencia: {res['tps']} tok/s en {res['elapsed']}s")
