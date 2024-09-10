#!/bin/bash
set -e

# Sync files from the source directory to the destination
rsync -vrah /temp/test/ /opt/odoo17/odoo17/

# Optionally remove the source directory if no longer needed
#rm -rf /temp/test 

echo "Code Deployed to /opt/odoo17/odoo17/"




