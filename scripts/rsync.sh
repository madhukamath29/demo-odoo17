#!/bin/bash
set -e
rsync -vrah /tmp/codedeploy1/ /opt/odoo17/odoo17/
rm -rf "/tmp/codedeploy1"
echo "Code Deployed to /opt/odoo17/odoo17/"

