#!/bin/bash
# Pulls results + logs from the Dell every 30 min (launchd: com.abhijit.albedo-sync). LAN first, Tailscale second.
for h in dell-lan dell; do
  rsync -a -e "ssh -o ConnectTimeout=10 -o BatchMode=yes" "$h:geo-ml-research/albedo/results/" "$HOME/geo-ml-research/albedo/results/" \
    && rsync -a -e "ssh -o ConnectTimeout=10 -o BatchMode=yes" "$h:geo-ml-research/logs/" "$HOME/geo-ml-research/logs/" \
    && { date > "$HOME/geo-ml-research/logs/last_sync"; exit 0; }
done
exit 1
