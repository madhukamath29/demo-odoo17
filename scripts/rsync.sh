#!/bin/bash
set -e

# Sync files from the source directory to the destination
rsync -vrah /temp/enterprise_addon/ /opt/odoo17/odoo17/

# Optionally remove the source directory if no longer needed
rm -rf /temp/enterprise_addon

echo "Code Deployed to /opt/odoo17/odoo17/"




