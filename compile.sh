#!/bin/bash
for i in *.tex; do
  if [ "$i" != 'template.tex' ]; then
    latexmk -pdf "$i";
  fi
done