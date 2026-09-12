"""Demo helper: `python demo.py break` plants a one-line bug in shop/pricing.py, `python demo.py reset` reverts it."""
import subprocess, sys
P = "sample_project/shop/pricing.py"
BUG = ("Decimal(str(pct)) / Decimal(100)", "Decimal(str(pct)) / Decimal(1000)")
if sys.argv[1:] == ["break"]:
    s = open(P).read().replace(*BUG); open(P, "w").write(s); print("planted: discount divides by 1000 instead of 100")
elif sys.argv[1:] == ["reset"]:
    subprocess.call(["git", "checkout", "--", P]); print("reset")
else:
    print(__doc__)
