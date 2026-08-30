# -*- coding: utf-8 -*-
"""
CCIA HTTP LOAD BENCHMARK TESTER v1.0
Simula peticiones concurrentes a endpoints locales para medir latencia P50/P95 y RPS (Opción 7).
"""
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor

def run_quick_benchmark(target_url: str = "http://127.0.0.1:8000/health", total_requests: int = 50, concurrency: int = 5) -> dict:
    latencies = []
    failures = 0

    def _worker():
        nonlocal failures
        t0 = time.time()
        try:
            req = urllib.request.Request(target_url, headers={"User-Agent": "CCIA-Benchmark/1.0"})
            with urllib.request.urlopen(req, timeout=2) as resp:
                if resp.status == 200:
                    latencies.append((time.time() - t0) * 1000)
                else:
                    failures += 1
        except Exception:
            failures += 1

    t_start = time.time()
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(_worker) for _ in range(total_requests)]
        for f in futures:
            f.result()
    t_total = time.time() - t_start

    if latencies:
        latencies.sort()
        p50 = latencies[int(len(latencies) * 0.5)]
        p95 = latencies[int(len(latencies) * 0.95)]
        rps = total_requests / t_total if t_total > 0 else 0.0
    else:
        p50 = p95 = rps = 0.0

    return {
        "total": total_requests,
        "success": len(latencies),
        "failures": failures,
        "rps": round(rps, 1),
        "p50_ms": round(p50, 2),
        "p95_ms": round(p95, 2)
    }

if __name__ == "__main__":
    res = run_quick_benchmark()
    print(f"⚡ Test Carga HTTP: {res['rps']} RPS | P50: {res['p50_ms']}ms | P95: {res['p95_ms']}ms")
