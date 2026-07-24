#!/bin/bash

# Clean previous setup
echo "🧹 Cleaning previous setup..."
rm -rf SSD_Elections

# Create fresh project
mkdir -p SSD_Elections
cd SSD_Elections

# Create all directories
mkdir -p scrapers utils assets templates data/cache data/exports tests logs

# Create all files (copy from previous setup script)
# ... (include all the file creation commands from previous setup script)

# Add .python-version
echo "3.11.0" > .python-version

echo "✅ Setup complete!"
echo ""
echo "Deploy to Render:"
echo "1. Push to GitHub"
echo "2. Connect repository to Render"
echo "3. Render will auto-detect and deploy"