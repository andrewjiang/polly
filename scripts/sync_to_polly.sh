#!/bin/bash
# Script to sync files to the Polly Raspberry Pi

# Ensure the target directory exists
ssh -i ~/.ssh/polly_key andrewjiang@polly.local "mkdir -p ~/Polly"

# Sync the files
rsync -avz --progress -e "ssh -i ~/.ssh/polly_key" \
    --exclude "__pycache__" \
    --exclude "*.pyc" \
    --exclude ".git" \
    --exclude ".env" \
    --exclude "venv" \
    ./ andrewjiang@polly.local:~/Polly/

echo "Sync completed!" 