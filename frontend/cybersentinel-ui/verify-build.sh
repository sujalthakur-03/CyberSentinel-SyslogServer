#!/bin/bash

echo "======================================"
echo "CyberSentinel UI - Build Verification"
echo "======================================"
echo ""

echo "📁 Checking project structure..."
cd /home/sujal/SyslogServer/frontend/cybersentinel-ui

# Check if directories exist
for dir in src/components src/pages src/contexts src/types src/utils src/services; do
    if [ -d "$dir" ]; then
        echo "✓ $dir exists"
    else
        echo "✗ $dir missing"
    fi
done

echo ""
echo "📄 Checking key files..."

# Check key files
files=(
    "src/App.tsx"
    "src/index.tsx"
    "src/index.css"
    "src/pages/LoginPage.tsx"
    "src/pages/Dashboard.tsx"
    "src/pages/LogsPage.tsx"
    "src/pages/SearchPage.tsx"
    "src/pages/AlertsPage.tsx"
    "src/pages/SettingsPage.tsx"
    "src/components/Sidebar.tsx"
    "src/components/Header.tsx"
    "src/components/ProtectedRoute.tsx"
    "src/components/StatCard.tsx"
    "src/components/LogTable.tsx"
    "src/components/LoadingSpinner.tsx"
    "src/contexts/AuthContext.tsx"
    "src/types/index.ts"
    "src/utils/helpers.ts"
    "src/services/api.ts"
    "package.json"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        lines=$(wc -l < "$file")
        echo "✓ $file ($lines lines)"
    else
        echo "✗ $file missing"
    fi
done

echo ""
echo "📦 Checking dependencies..."
if [ -d "node_modules" ]; then
    echo "✓ node_modules installed"
    
    # Check key dependencies
    deps=("react" "react-dom" "react-router-dom" "axios" "recharts" "lucide-react" "typescript")
    for dep in "${deps[@]}"; do
        if [ -d "node_modules/$dep" ]; then
            echo "  ✓ $dep"
        else
            echo "  ✗ $dep not found"
        fi
    done
else
    echo "✗ node_modules not found - run 'npm install'"
fi

echo ""
echo "📊 Code Statistics..."
echo "TypeScript files: $(find src -name '*.tsx' -o -name '*.ts' | wc -l)"
echo "Total lines of code: $(find src -name '*.tsx' -o -name '*.ts' | xargs wc -l | tail -1)"

echo ""
echo "📚 Documentation files..."
for doc in README.md SETUP.md CSS_COMPLETION_GUIDE.md IMPLEMENTATION_COMPLETE.md; do
    if [ -f "$doc" ]; then
        echo "✓ $doc"
    else
        echo "✗ $doc"
    fi
done

echo ""
echo "======================================"
echo "Verification Complete!"
echo "======================================"
echo ""
echo "To start the application:"
echo "  npm start"
echo ""
echo "To build for production:"
echo "  npm run build"
echo ""
