"""Fetch an already-submitted CDS request by ID (survives a reboot without re-queueing).
    .venv/bin/python albedo/resume_era5.py <request_id> <dest.nc>"""
import re, sys, time
from pathlib import Path
from ecmwf.datastores import Client
rid, dst = sys.argv[1], Path(sys.argv[2])
t = (Path.home() / ".cdsapirc").read_text()
c = Client(url=re.search(r"url:\s*(\S+)", t).group(1), key=re.search(r"key:\s*(\S+)", t).group(1))
r = c.get_remote(rid)
while r.status in ("accepted", "running"):
    print(time.strftime("%T"), r.status, flush=True); time.sleep(120)
print("final status", r.status, flush=True)
r.download(str(dst.with_suffix(".tmp"))); dst.with_suffix(".tmp").rename(dst); print("ok", dst)
