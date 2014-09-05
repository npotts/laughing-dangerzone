#!/bin/bash
for i in {0..255} ; do
    printf "\x1b[38;5;${i}mcolour${i} "
    if [ 0 == $(($i % 8)) ]; then
      printf "\n"
    fi
done
printf "\n"
