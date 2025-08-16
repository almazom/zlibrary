#!/bin/bash
# 🎨 Install Pipeline Visualization Dependencies

echo "🎨 Installing Pipeline Visualization Dependencies..."

# Install rich for beautiful terminal UI
pip3 install rich>=13.0.0

echo "✅ Visualization dependencies installed!"
echo ""
echo "🚀 Quick start:"
echo "  python3 demo_pipeline_visual.py                     # Full demo"
echo "  python3 demo_pipeline_visual.py \"hary poter\"       # Single query" 
echo "  python3 demo_pipeline_visual.py --interactive       # Interactive mode"
echo ""
echo "🎯 Try fuzzy inputs like:"
echo "  • \"hary poter filosofer stone\""
echo "  • \"malenkiy prinz\""
echo "  • \"dostoevsky преступление\""
echo ""