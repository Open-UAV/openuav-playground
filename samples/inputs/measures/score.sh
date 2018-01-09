#!/usr/bin/env bash
cat /simulation/outputs/measure.csv | awk -F',' '{sum+=$2; ++n} END { print sum/n }' > /simulation/outputs/score.out
cat /simulation/outputs/score.out