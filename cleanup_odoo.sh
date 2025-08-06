#!/bin/bash

echo "🚫 Removing frontend-heavy and mail-related modules..."

# List of modules to remove
MODULES=(
  web
  web_editor
  portal
  mail
  web_tour
  web_unsplash
  html_editor
  auth_signup
  iap
  iap_mail
  snailmail
  partner_autocomplete
  sms
  google_gmail
  phone_validation
  base_install_request
)

# Paths to search in
PATHS=(
  "./addons"
  "./odoo/addons"
)

# Loop and remove
for path in "${PATHS[@]}"; do
  for module in "${MODULES[@]}"; do
    fullpath="${path}/${module}"
    if [ -d "$fullpath" ]; then
      rm -rf "$fullpath"
      echo "🗑️ Removed: $fullpath"
    else
      echo "✅ Skipped (not found): $fullpath"
    fi
  done
done

echo "🎉 Cleanup complete!"
