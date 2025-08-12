#!/bin/bash

# Demo script to run interactive URL test with sample URLs

echo "🚀 Running Interactive URL Testing Demo"
echo "Testing 3 URLs to demonstrate the service..."
echo ""

# Create input for the interactive test
cat << 'EOF' | ./scripts/interactive_url_test.sh
https://www.podpisnie.ru/books/maniac/
https://www.goodreads.com/book/show/3735293-clean-code
https://www.amazon.com/Clean-Code-Handbook-Software-Craftsmanship/dp/0132350882
done
EOF

echo ""
echo "✅ Demo Complete!"
echo ""
echo "To run your own test:"
echo "  ./scripts/interactive_url_test.sh"
echo ""
echo "Then enter URLs one by one, type 'done' when finished."