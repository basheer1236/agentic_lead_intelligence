import os
import glob
import subprocess
import sys

def main():
    test_files = sorted(glob.glob("tests/test_*.py"))
    print(f"Running {len(test_files)} test scripts...")
    passed = 0
    failed = 0
    failures = []

    for f in test_files:
        env = os.environ.copy()
        env["PYTHONPATH"] = "."
        res = subprocess.run([sys.executable, f], capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
        if res.returncode == 0:
            passed += 1
            print(f"[PASS] {f}", flush=True)
        else:
            failed += 1
            print(f"[FAIL] {f}", flush=True)
            failures.append((f, res.stderr or res.stdout))

    print("\n" + "=" * 50)
    print(f"TEST RUNNER SUMMARY: {passed} PASSED, {failed} FAILED out of {len(test_files)} files")
    print("=" * 50)

    if failures:
        for f, err in failures:
            print(f"\n--- FAILURE IN {f} ---")
            print(err)

if __name__ == "__main__":
    main()
