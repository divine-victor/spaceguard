# SpaceGuard

A lightweight, blazing-fast static analysis tool for C that catches spatial memory violations (buffer overflows, use-after-free, format strings) directly in VS Code.

Unlike enterprise tools that take 40 minutes to scan a codebase, SpaceGuard uses Tree-sitter to build an AST and report vulnerabilities in **milliseconds** as you type.

## Why?
60% of severe CVEs are caused by memory unsafety in C/C++. AI coding assistants (Copilot, ChatGPT) frequently hallucinate unsafe C code. SpaceGuard acts as a real-time guardrail.

## Features
- **Buffer Overflows:** Catches `strcpy`/`strcat` writing more bytes than the destination array holds.
- **Format Strings:** Flags `printf(user_input)` vulnerabilities.
- **Use-After-Free:** Tracks variables after `free()` is called.
- **Zero Dependencies:** The analysis engine is compiled into a standalone binary. No Python or Node required.

## Installation
1. Download the `spaceguard-0.0.1.vsix` from the releases tab.
2. Open VS Code -> Extensions -> `...` -> **Install from VSIX**.

## Usage
Just open any `.c` file. The engine runs in the background.

![SpaceGuard in action](https://via.placeholder.com/600x200.png?text=Hover+over+the+red+line+to+see+the+byte+overflow)

## Roadmap
- [ ] Cross-file analysis (`#include`)
- [ ] Pointer arithmetic tracking
- [ ] CI/CD GitHub Action
