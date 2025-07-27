#!/usr/bin/env python3
"""
Install Ultra-Fast Libraries for Maximum Performance
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package}: {e}")
        return False

def main():
    print("🚀 Installing Ultra-Fast Libraries for ShadowHawk")
    print("=" * 50)
    
    # Essential ultra-fast libraries
    ultra_fast_packages = [
        "polars",           # Rust-based DataFrame library (5-30x faster than pandas)
        "pyarrow",          # Columnar data format (2-10x faster)
        "fastparquet",      # Fast Parquet file support
        "duckdb",           # Ultra-fast analytical database
        "numba",            # JIT compilation for Python
    ]
    
    # Optional performance packages
    optional_packages = [
        "cudf-cu11",        # GPU DataFrames (requires NVIDIA GPU)
        "rapids-cudf",      # RAPIDS ecosystem
        "modin[ray]",       # Parallel pandas
    ]
    
    print("📦 Installing essential ultra-fast packages...")
    success_count = 0
    
    for package in ultra_fast_packages:
        print(f"\nInstalling {package}...")
        if install_package(package):
            print(f"✅ {package} installed successfully")
            success_count += 1
        else:
            print(f"❌ {package} installation failed")
    
    print(f"\n📊 Essential packages: {success_count}/{len(ultra_fast_packages)} installed")
    
    # Try optional packages (GPU support)
    print("\n🎮 Attempting GPU acceleration packages (optional)...")
    gpu_success = 0
    
    for package in optional_packages:
        print(f"\nTrying {package}...")
        if install_package(package):
            print(f"✅ {package} installed - GPU acceleration available!")
            gpu_success += 1
        else:
            print(f"⚠️ {package} not available (GPU/CUDA may not be installed)")
    
    print(f"\n🎮 GPU packages: {gpu_success}/{len(optional_packages)} installed")
    
    # Performance recommendations
    print("\n🚀 PERFORMANCE SETUP COMPLETE!")
    print("=" * 50)
    
    if success_count >= 3:
        print("✅ Ready for ultra-fast operations!")
        print("\nSpeed improvements you can expect:")
        print("  📁 CSV Import: 5-30x faster with Polars")
        print("  🔍 Search: 10-100x faster with native operations")
        print("  💾 Storage: 50-80% smaller with Parquet")
        print("  🌊 Large files: Unlimited size with streaming")
        
        if gpu_success > 0:
            print("  🎮 GPU Acceleration: 10-100x faster for large datasets!")
    else:
        print("⚠️ Some packages failed to install.")
        print("You can still use the standard fast version.")
    
    print("\n🎯 Usage:")
    print("  python ultra_fast_test.py    # Test ultra-fast performance")
    print("  python ultra_fast_browser.py # Run ultra-fast browser")

if __name__ == "__main__":
    main()
