#!/bin/bash
set -e
sudo systemctl restart odoo-server.service
echo "Odoo16 service restarted"
