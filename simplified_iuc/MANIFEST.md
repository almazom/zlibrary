
# Manifest for the `simplified_iuc` Test Suite

**Version**: 3.0
**Status**: ACTIVE
**Standard**: The "Transparent E2E" Standard

## 🎯 Philosophy & Principles

This test suite provides **simple, transparent, end-to-end (E2E)** validation of the live Telegram bot.

1.  **Principle: Real E2E Testing.** All tests **must** perform real, multidirectional communication with the live Telegram bot to simulate a real user journey.
2.  **Tooling: Python & Telethon.** All tests **must** be standalone Python scripts that use the `telethon` library for all Telegram communications.
3.  **Principle: Transparency.** All tests **must** produce a rich, step-by-step, UX-enhanced output that makes the test's purpose, actions, and results immediately clear.

## 📁 File Naming Convention

`siuc_XX_description.py`

*   `siuc_`: Stands for "Simplified Integration User Case".
*   `XX`: A two-digit number, starting from `01`.
*   `description`: A short, snake_case description of the test's purpose.

## 🐍 Code & Output Standard

All tests must be built from the `siuc_TEMPLATE.py` file and produce the standard "UX-Enhanced" output defined within it. This includes:

*   A clear header explaining the test's purpose and expected outcome.
*   Numbered, step-by-step logging with emoji status indicators.
*   A final summary with a `PASS/FAIL` status and a visual pipeline.
*   Embedded comments from both a **Senior Developer** (explaining implementation details and best practices) and an **Architecture Guardian** (explaining the architectural significance of the test).
