#!/usr/bin/env bash
# Lokaler Datenabgleich (für Rechner, die bundeshaushalt.de erreichen; GitHub-Server werden dort abgewiesen).
# Rechnet die Daten neu und öffnet bei Änderungen einen Pull Request zur Prüfung. Braucht git, python3 und gh.
#
#   bash pipeline/aktualisieren.sh
set -euo pipefail
cd "$(dirname "$0")/.."
PY=$(command -v python3 || command -v python)

if [ -n "$(git status --porcelain -- data)" ]; then
  echo "data/ hat ungespeicherte Änderungen, bitte erst committen oder verwerfen." >&2
  exit 1
fi
git fetch -q origin main
git switch -q main
git merge -q --ff-only origin/main

rm -f pipeline/bericht.md
"$PY" pipeline/haushalt.py
"$PY" pipeline/median.py

if git diff --quiet -- data; then
  echo "Keine Änderungen an den Daten."
  exit 0
fi

heute=$(date -u +%Y-%m-%d)
branch="daten/$heute"
git switch -q -c "$branch"
git add data
git commit -q -m "Daten aktualisiert ($heute)"
git push -q --force -u origin "$branch"
{
  echo "Abgleich mit den amtlichen Quellen (lokal ausgeführt). Bitte vor dem Zusammenführen prüfen:"
  echo
  echo "- Sind die geänderten Werte plausibel (neues Haushaltsjahr, neue Haushaltsrechnung, Revision)?"
  echo "- Stimmen Texte auf der Seite noch, die Jahre nennen (z. B. „2015–2026“)?"
  echo
  cat pipeline/bericht.md
} > pipeline/.pr.md
if gh pr view "$branch" >/dev/null 2>&1; then
  gh pr edit "$branch" --body-file pipeline/.pr.md
else
  gh pr create --base main --head "$branch" --title "Daten aktualisiert ($heute)" --body-file pipeline/.pr.md
fi
rm -f pipeline/.pr.md
git switch -q main
