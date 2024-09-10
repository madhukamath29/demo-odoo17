#!/bin/bash
set -e

# Use rsync to copy the files
rsync -vrah /temp/enterprise_addon/ /opt/odoo17/odoo17/

# Remove the temporary directory
rm -rf /temp/enterprise_addon

echo "Code Deployed to /opt/odoo17/odoo17/"

