#!/bin/bash

# Get the parent directory of the script
parent_directory=$(dirname "$(dirname "$0")")

# Cron job entries
cron_entries=(
    "0 */12 * * * rm $parent_directory/caches/requests_cache.sqlite"
    "0 */12 * * * rm $parent_directory/caches/proxy_requests_cache.sqlite"
    "0 */3 * * * rm -rf /tmp/*"
)

# Check if cron job entries already exist
existing_cron=$(crontab -l 2>/dev/null)

for entry in "${cron_entries[@]}"; do
    if ! grep -qF "$entry" <<< "$existing_cron"; then
        (crontab -l; echo "$entry") | crontab -
        echo "Added cron job: $entry"
    else
        echo "Cron job already exists: $entry"
    fi
done

echo "Cron job update complete."
