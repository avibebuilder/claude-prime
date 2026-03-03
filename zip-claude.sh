#!/bin/bash
# Zip .claude directory excluding gitignored files

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

TIMESTAMP=$(date +%Y%m%d%H%M%S)
OUTPUT_FILE="claude-prime-${TIMESTAMP}.zip"

# Generate .prime-version from VERSION file
PRIME_VERSION=$(cat VERSION)
echo "$PRIME_VERSION" > .claude/.prime-version
echo "Generated .prime-version: $PRIME_VERSION"

echo "Creating ${OUTPUT_FILE}..."

# Get tracked files in .claude/ using git (respects .gitignore)
# Then add .prime-version separately (it's gitignored but needed in zip)
git ls-files .claude/ | zip -@ "$OUTPUT_FILE"
zip "$OUTPUT_FILE" .claude/.prime-version

# Clean up (file is gitignored, don't leave it around)
rm .claude/.prime-version

echo "✓ Created ${OUTPUT_FILE}"
echo "  Size: $(du -h "$OUTPUT_FILE" | cut -f1)"
echo "  Files: $(unzip -l "$OUTPUT_FILE" | tail -1 | awk '{print $2}')"
echo "  Version: $PRIME_VERSION"
