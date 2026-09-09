#!/usr/bin/env bash
# Haengt alle Skills dieses Repos nach ~/.claude/skills/ — als Symlink, damit
# Aenderungen im Repo sofort wirken. Ersetzt vorhandene Links gleichen Namens.
set -euo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ZIEL="$HOME/.claude/skills"
mkdir -p "$ZIEL"

for pfad in "$REPO"/plugins/*/skills/*/; do
  name="$(basename "$pfad")"
  if [ -e "$ZIEL/$name" ] && [ ! -L "$ZIEL/$name" ]; then
    echo "  uebersprungen: $name — dort liegt ein echter Ordner, kein Link"
    continue
  fi
  rm -f "$ZIEL/$name"
  ln -s "${pfad%/}" "$ZIEL/$name"
  echo "  verknuepft: $name"
done
echo
echo "Fertig. Claude Code neu starten, damit die Skills gelesen werden."
