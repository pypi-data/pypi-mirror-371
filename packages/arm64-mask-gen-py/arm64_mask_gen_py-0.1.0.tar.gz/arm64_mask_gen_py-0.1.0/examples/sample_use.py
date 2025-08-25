#!/usr/bin/env python3
"""Sample usage for arm64_mask_gen_py wrapper.

Run after you install the extension into the Python used by IDA (or your system Python):

    maturin develop --release
    python examples/sample_use.py "BL #?"

If you built the extension for a different interpreter, run the script with that interpreter.
"""
import sys

def main():
    template = "BL #?"
    if len(sys.argv) > 1:
        template = sys.argv[1]

    try:
        import arm64_mask_gen_py
    except Exception as e:
        print("Failed to import 'arm64_mask_gen_py':", e)
        print("Make sure you built and installed the extension with maturin for the Python interpreter you're using.")
        print("Example: maturin develop --release ")
        return 1

    try:
        pat, msk = arm64_mask_gen_py.make_r2_mask(template)
        print("Template:", template)
        print("Pattern :", pat)
        print("Mask    :", msk)
    except Exception as e:
        print("Error while generating pattern:mask:", e)
        return 2

    return 0


if __name__ == '__main__':
    sys.exit(main())
