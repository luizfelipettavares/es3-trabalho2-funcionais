#!/usr/bin/env bash
# Roda cada suíte 3 vezes em sequência e grava JUnit XML + HTML + log em resultados/<suite>/.
# Requer os sistemas no ar (ver README). Uso: HEADLESS=1 bash ferramentas/rodar_3x.sh [suite...]
set -u
RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
SUITES=("${@:-pacote-A/exemplo pacote-A/desafio pacote-B/exemplo pacote-B/desafio projeto-anterior}")
for r in 1 2 3; do
  for s in ${SUITES[@]}; do
    out="$RAIZ/resultados/${s//\//-}"; mkdir -p "$out"; cd "$RAIZ/$s"
    [ "$s" = pacote-A/exemplo ] && curl -s -X POST http://localhost:5000/api/admin/reset > /dev/null
    arq=""; [ "$s" = pacote-B/exemplo ] && arq=test_login.py
    python3 -m pytest $arq -v -p no:cacheprovider --junitxml="$out/execucao_r$r.xml" \
      --html="$out/execucao_r$r.html" --self-contained-html > "$out/execucao_r$r.log" 2>&1
    echo "$s r$r: $(tail -1 "$out/execucao_r$r.log")"
  done
done
