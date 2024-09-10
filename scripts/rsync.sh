#!/bin/bash
set -e
rsync -vrah /temp/enterprise_addon /opt/odoo17/odoo17/
rm -rf "/temp/enterprise_addon"
echo "Code Deployed to /opt/odoo17/odoo17/"

