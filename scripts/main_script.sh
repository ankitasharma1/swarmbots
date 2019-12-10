#!/bin/bash

SCRIPTS_DIR="~/Code/swarmbots/scripts"
ssh rlab_s1 "$SCRIPTS_DIR/local_script_s1.sh"
ssh rlab_s2 "$SCRIPTS_DIR/local_script_s2.sh"
ssh rlab_s3 "$SCRIPTS_DIR/local_script_s3.sh"