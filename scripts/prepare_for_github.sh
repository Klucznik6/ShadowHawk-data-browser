#!/bin/bash
# prepare_for_github.sh - Final preparation script for GitHub

echo "🦅 ShadowHawk Database Browser - GitHub Preparation"
echo "=================================================="

# Remove sensitive or unnecessary files
echo "🧹 Cleaning up workspace..."
rm -rf __pycache__/ 2>/dev/null
rm -f config.json 2>/dev/null
rm -f *.pyc 2>/dev/null
rm -f *.log 2>/dev/null

# Create config from template if it doesn't exist
if [ ! -f "config.json" ]; then
    echo "📝 Creating config.json from template..."
    cp config.json.template config.json
fi

# Check if all required files exist
echo "✅ Checking project structure..."
required_files=("main.py" "README.md" "requirements.txt" "LICENSE" "CHANGELOG.md")
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✓ $file"
    else
        echo "  ❌ Missing: $file"
    fi
done

# Check directories
required_dirs=("docs" "tests" "sample_data" "scripts")
for dir in "${required_dirs[@]}"; do
    if [ -d "$dir" ]; then
        echo "  ✓ $dir/"
    else
        echo "  ❌ Missing: $dir/"
    fi
done

echo ""
echo "🚀 Ready for GitHub!"
echo "Next steps:"
echo "1. git add ."
echo "2. git commit -m 'feat: Complete v1.0.0 release with modern UI and custom icons'"
echo "3. git push origin main"
echo "4. Create release on GitHub"
