#!/usr/bin/env python3
"""
Test script for the global search feature
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import ShadowHawkBrowser

if __name__ == "__main__":
    print("Starting ShadowHawk Database Browser with Global Search...")
    print("Features:")
    print("- Toggle 'Search All DBs' checkbox to enable global search")
    print("- When enabled, search will look across all loaded databases")
    print("- Results will show which database and table each match came from")
    print("- When disabled, search only current table")
    
    app = ShadowHawkBrowser()
    app.root.mainloop()
