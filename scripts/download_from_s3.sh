#!/bin/bash
echo "Downloading artifacts from S3..."
aws s3 cp s3://final-code-merged-bucket/deployment/ /temp/final-code --recursive