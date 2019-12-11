#!/bin/bash

SCRIPTS_DIR="~/Code/swarmbots/scripts"
ssh rlab_s1 "$SCRIPTS_DIR/local_script.sh"
ssh rlab_s2 "$SCRIPTS_DIR/local_script.sh"
ssh rlab_s3 "$SCRIPTS_DIR/local_script.sh"