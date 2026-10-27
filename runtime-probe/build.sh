#!/usr/bin/env bash
# Build RamusBridge for one loader.
#
#   ./runtime-probe/build.sh BepInEx6    /path/to/BepInEx
#   ./runtime-probe/build.sh MelonLoader /path/to/MelonLoader
#   ./runtime-probe/build.sh BepInEx5    /path/to/<game>_Data/Managed
set -euo pipefail

LOADER="${1:-BepInEx6}"
DIR="${2:-}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

case "$LOADER" in
  BepInEx6)    PROP="BepInExRoot" ;;
  MelonLoader) PROP="MelonDir" ;;
  BepInEx5)    PROP="UnityManagedDir" ;;
  *) echo "unknown loader: $LOADER (BepInEx6 | BepInEx5 | MelonLoader)" >&2; exit 2 ;;
esac

if [ -z "$DIR" ]; then
  echo "usage: build.sh $LOADER <path>" >&2
  exit 2
fi

exec dotnet build "$HERE/RamusBridge.csproj" -c Release -p:Loader="$LOADER" -p:"$PROP=$DIR"
