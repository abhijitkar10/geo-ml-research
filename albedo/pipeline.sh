#!/usr/bin/env bash
# Whole study, end to end, safe to start any number of times (cron runs it at boot and every 20 min):
#   1. fetch ERA5 surface fields (reuses the queued CDS request; resubmits if it expired or failed)
#   2. model_a -> model_b -> report -> explain (LLM digest), each skipped once logs/<step>.ok exists
# flock keeps a second copy from running. logs/pipeline.done appears when every step has been tried.
cd ~/geo-ml-research || exit 1
exec 9> logs/pipeline.lock
flock -n 9 || exit 0
log() { echo "$(date '+%F %T') $*" >> logs/pipeline.log; }
# homelab shares this box: stay in the background. One BLAS thread per process: numpy's default (all cores)
# fought LightGBM and made the ridge CV ~30x slower (measured 2026-11-08).
PY="env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=2 nice -n 15 ionice -c3 .venv/bin/python"
SINGLE=albedo/data/era5/single_2003-2025.nc
ERA5_REQUEST=e412616b-40f2-47eb-9359-9cd93cd9005f

[ "$(ls albedo/data/merra2/*.sub.nc 2>/dev/null | wc -l)" -ge 276 ] || { log "merra2 incomplete, resuming"; $PY albedo/download.py merra2 >> logs/merra2.log 2>&1; }
[ -f albedo/data/era5/plev_2003-2025.nc ] || { log "plev missing, downloading"; $PY albedo/download.py era5 plev >> logs/era5_plev.log 2>&1; }
if [ ! -f $SINGLE ]; then
  log "waiting for ERA5 request $ERA5_REQUEST"
  $PY albedo/resume_era5.py $ERA5_REQUEST $SINGLE >> logs/era5_single.log 2>&1 \
    || { log "request unusable, resubmitting"; $PY albedo/download.py era5 single >> logs/era5_single.log 2>&1; }
fi
[ -f $SINGLE ] || { log "no ERA5 surface file yet, will retry"; exit 0; }

for step in model_a model_b shipping report explain; do
  [ -f logs/$step.ok ] && continue
  log "start $step"
  [ $step = model_a ] && touch logs/model_a.started
  $PY albedo/$step.py > logs/$step.log 2>&1
  code=$?
  echo "EXIT $code" >> logs/$step.log
  log "$step exit $code"
  if [ $code -eq 0 ]; then touch logs/$step.ok; else echo $code >> logs/$step.failures; fi
  # A step that failed 3 times is given up on so later steps still run; logs/<step>.log has why.
  [ $code -ne 0 ] && [ "$(wc -l < logs/$step.failures)" -lt 3 ] && exit 1
done
# When a dataset completes (or logs/rerun.request is touched after a code change), rerun every model once.
# (model_a.started is touched when the data is loaded, so "newer" means the models never saw it.)
new=""
for m in albedo/data/ssf/COMPLETE albedo/data/ssf_aqua/COMPLETE albedo/data/fbct/COMPLETE albedo/data/fbct_n20/COMPLETE logs/rerun.request; do
  [ $m -nt logs/model_a.started ] && new="$new $m"
done
if [ -n "$new" ]; then
  log "new data or request ($new): rerunning every model"
  rm -f logs/model_a.ok logs/model_b.ok logs/shipping.ok logs/report.ok logs/explain.ok logs/*.failures logs/pipeline.done; exit 0
fi
for step in model_a model_b shipping report explain; do echo "$step $([ -f logs/$step.ok ] && echo ok || echo failed)"; done > logs/pipeline.done
log "pipeline done"
