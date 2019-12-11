#!/bin/bash

SCRIPTS_DIR="/home/pi/Code/swarmbots/scripts"
ssh -i ~/.ssh/scriptkey swarmer1 "$SCRIPTS_DIR/local_script.sh" &
S1_PID=$!
ssh -i ~/.ssh/scriptkey swarmer2 "$SCRIPTS_DIR/local_script.sh" &
S2_PID=$!
ssh -i ~/.ssh/scriptkey swarmer3 "$SCRIPTS_DIR/local_script.sh" &
S3_PID=$!

echo $S1_PID >> kill.txt
echo $S2_PID >> kill.txt
echo $S3_PID >> kill.txt

