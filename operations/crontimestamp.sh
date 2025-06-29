#!/bin/bash
while IFS= read -r x; do
  echo -n "$(date +'%Y-%m-%d %H:%M:%S') "
  echo "$x"
done