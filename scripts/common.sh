# Shared by the numbered scripts. Finds the kit folder, your clone folder and your settings.
KIT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"; ME="$KIT/my-clone"; PY="$KIT/.venv/bin/python"
die() { echo; echo "STOP: $*"; echo; exit 1; }
[ -f "$ME/clone.yaml" ] || die "my-clone/clone.yaml is missing. Run: bash scripts/1_setup.sh"
cfg() { "$PY" -c "import yaml,sys;print(yaml.safe_load(open('$ME/clone.yaml')).get(sys.argv[1],''))" "$1"; }
[ -f "$KIT/.env" ] && { set -a; . "$KIT/.env"; set +a; }
pod() { [ -n "$POD_IP" ] && [ -n "$POD_PORT" ] || die "POD_IP and POD_PORT are empty in .env. See docs/03-train-on-runpod.md, step 5."
        ssh -o StrictHostKeyChecking=no -o ServerAliveInterval=30 -o ConnectTimeout=20 -p "$POD_PORT" root@"$POD_IP" "$@"; }
