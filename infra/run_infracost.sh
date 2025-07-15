#!/bin/bash
set -euo pipefail

# Cleanup previous runs
rm -f tfplan.binary tfplan.json infracost-output.json infracost-report.html

# Initialize and plan with Terraform
terraform init -input=false -upgrade
terraform validate
terraform plan -out=tfplan.binary -input=false
terraform show -json tfplan.binary > tfplan.json

# Try to generate usage file (new Infracost versions use 'infracost generate usage-file')
if command -v infracost &> /dev/null; then
  if infracost help | grep -q "generate usage-file"; then
    infracost generate usage-file --path=tfplan.json --out-file=infracost-usage.yml || \
      echo "Warning: Usage file generation failed (proceeding without it)"
  else
    echo "Note: Older Infracost version detected (usage estimates unavailable)"
  fi
fi

# Run Infracost breakdown
echo -e "\n=== Cost Estimate ==="
infracost breakdown \
  --path=tfplan.json \
  $(test -f infracost-usage.yml && echo "--usage-file=infracost-usage.yml") \
  --format=table \
  --show-skipped

# Generate reports
infracost breakdown \
  --path=tfplan.json \
  $(test -f infracost-usage.yml && echo "--usage-file=infracost-usage.yml") \
  --format=json \
  --out-file=infracost-output.json

infracost breakdown \
  --path=tfplan.json \
  $(test -f infracost-usage.yml && echo "--usage-file=infracost-usage.yml") \
  --format=html \
  --out-file=infracost-report.html

echo -e "\nDone. Reports generated:"
ls -lh infracost-{output.json,report.html} 2>/dev/null || echo "No reports generated"