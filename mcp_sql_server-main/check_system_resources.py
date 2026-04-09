"""Check system resources for SQLCoder model."""

import psutil
import torch

print("="*70)
print("SYSTEM RESOURCE CHECK")
print("="*70)

# RAM
ram = psutil.virtual_memory()
print(f"\nRAM:")
print(f"  Total: {ram.total / (1024**3):.1f} GB")
print(f"  Available: {ram.available / (1024**3):.1f} GB")
print(f"  Used: {ram.used / (1024**3):.1f} GB ({ram.percent}%)")

# Disk
disk = psutil.disk_usage('C:\\')
print(f"\nDisk (C:):")
print(f"  Total: {disk.total / (1024**3):.1f} GB")
print(f"  Free: {disk.free / (1024**3):.1f} GB")
print(f"  Used: {disk.used / (1024**3):.1f} GB ({disk.percent}%)")

# CUDA
print(f"\nGPU:")
print(f"  CUDA Available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"  Device: {torch.cuda.get_device_name(0)}")
    print(f"  Memory: {torch.cuda.get_device_properties(0).total_memory / (1024**3):.1f} GB")

print("\n" + "="*70)
print("SQLCODER-7B-2 REQUIREMENTS")
print("="*70)
print("\nMinimum (CPU):")
print("  RAM: 16 GB")
print("  Disk: 20 GB free")
print("\nRecommended (GPU):")
print("  VRAM: 8 GB")
print("  RAM: 16 GB")

print("\n" + "="*70)
print("RECOMMENDATION")
print("="*70)

if ram.available / (1024**3) < 12:
    print("\n⚠️  WARNING: Low RAM!")
    print("   Available RAM is less than 12 GB")
    print("   SQLCoder-7B-2 may crash during loading")
    print("\n   SOLUTIONS:")
    print("   1. Close other applications to free RAM")
    print("   2. Use mock mode (disable model loading)")
    print("   3. Use cloud API (OpenAI/Gemini) instead")
else:
    print("\n✓ RAM looks sufficient")
    print("  Model should load successfully")

print("="*70 + "\n")
