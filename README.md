# SpaceGuard

SpaceGuard is a static analysis engine for C code. It detects spatial memory violations—such as buffer overflows, integer wrap-arounds, use-after-free, and format string vulnerabilities—directly inside your editor.

## Features

- **AST-Based Analysis:** Uses `tree-sitter` to parse the true structure of C code, ignoring comments and formatting.
- **Spatial Tracking:** Maintains a symbol table to track declared buffer sizes.
- **Real-Time Diagnostics:** Red squiggly lines appear under unsafe function calls as you type.
- **Compiled Engine:** No Python installation required. The analysis engine is compiled into a standalone binary.

## Usage

1. Open any `.c` file in VS Code.
2. The extension will automatically scan the file.
3. Hover over any red squiggly lines to see the exact spatial violation and byte size mismatch.

## Vulnerabilities Detected

- `strcpy` / `strcat` buffer overflows
- `malloc` integer overflow (calculation explosion)
- Use-After-Free (UAF)
- Double Free
- Format String vulnerabilities (`printf` with user input)
- Off-by-One errors (`<=` in loops)