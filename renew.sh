#!/usr/bin/env bash
# One-command session renewal: log in, upload the new session to GitHub,
# and confirm the next cloud run succeeds.
set -euo pipefail
cd "$(dirname "$0")"

if [ ! -d .venv ]; then
    echo "No .venv found — run: python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && playwright install chromium"
    exit 1
fi
source .venv/bin/activate

echo "Opening a browser window to log in..."
python login.py https://michiganross.12twenty.com/events

if [ ! -f storage_state.json ]; then
    echo "storage_state.json was not created — login did not complete. Aborting."
    exit 1
fi

echo "Uploading session to GitHub..."
python3 -c "import base64;print(base64.b64encode(open('storage_state.json','rb').read()).decode())" | gh secret set ROSS_STORAGE_STATE

echo "Triggering a cloud run to confirm it works..."
gh workflow run poll.yml
sleep 8
run_id=$(gh run list --workflow poll.yml --limit 1 --json databaseId -q '.[0].databaseId')
gh run watch "$run_id" --exit-status >/dev/null 2>&1 || true

if gh run view "$run_id" --log 2>&1 | grep -q "session expired"; then
    echo "Run still reports 'session expired' — something went wrong. Check the workflow logs:"
    echo "  gh run view $run_id --log"
    exit 1
fi

echo "Renewed and confirmed working (run: $(gh run view "$run_id" --json url -q .url))."
