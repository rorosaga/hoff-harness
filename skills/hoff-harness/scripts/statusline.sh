#!/bin/sh
# Claude Code status line: how many screen clips wait for the next message.
# Prints nothing when none wait. Pure shell, because the status line runs often.
d="$HOME/Library/Caches/hoff-harness"
n=0
if [ -e "$d/preview" ] && [ -n "$(find "$d/preview" -mmin -1 2>/dev/null)" ]; then
  n=$(cat "$d/preview")  # `hoff-harness preview`: a pretend count, nothing attaches
elif [ -e "$d/marks/pending" ]; then
  for m in $(find "$d/marks" -mindepth 2 -maxdepth 2 -name mark.json -mmin -15 2>/dev/null); do
    [ -e "$(dirname "$m")/used" ] || n=$((n + 1))
  done
fi
[ "$n" -gt 0 ] 2>/dev/null || exit 0
s=s; [ "$n" = 1 ] && s=
keys=$(cat "$d/keys-hint" 2>/dev/null || echo "⌃⌥ add · ⌃⌥ esc clear")  # written by the overlay from config.json
printf '📎 %s screen clip%s ready · %s\n' "$n" "$s" "$keys"
