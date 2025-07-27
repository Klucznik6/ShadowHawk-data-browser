@echo off
REM prepare_for_github.bat - Windows preparation script for GitHub

echo 🦅 ShadowHawk Database Browser - GitHub Preparation
echo ==================================================

echo 🧹 Cleaning up workspace...
if exist __pycache__ rmdir /s /q __pycache__
if exist config.json del /q config.json
del /q *.pyc 2>nul
del /q *.log 2>nul

echo 📝 Creating config.json from template...
if not exist config.json copy config.json.template config.json

echo ✅ Checking project structure...
set files=main.py README.md requirements.txt LICENSE CHANGELOG.md
for %%f in (%files%) do (
    if exist %%f (
        echo   ✓ %%f
    ) else (
        echo   ❌ Missing: %%f
    )
)

set dirs=docs tests sample_data scripts
for %%d in (%dirs%) do (
    if exist %%d (
        echo   ✓ %%d\
    ) else (
        echo   ❌ Missing: %%d\
    )
)

echo.
echo 🚀 Ready for GitHub!
echo Next steps:
echo 1. git add .
echo 2. git commit -m "feat: Complete v2.0 release with Polars integration"
echo 3. git push origin main
echo 4. Create release on GitHub

pause
