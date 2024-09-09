#!/bin/bash
set -e
rsync -vrah /tmp/codedeploy/ /opt/odoo17/odoo17/
#rm -rf "/tmp/codedeploy"
echo "Code Deployed to /opt/odoo17/odoo17/"

