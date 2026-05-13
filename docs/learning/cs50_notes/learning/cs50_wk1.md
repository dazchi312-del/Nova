# CS50 Learning Notes

> Personal study notes for CS50x. Living document — grows weekly.
> Started: October 2025 | Target completion: December 31, 2025

---

## 📚 Table of Contents

1. [Computer Science Glossary](#computer-science-glossary)
2. [Week 0: Scratch & Foundations](#week-0-scratch--foundations)
3. [Week 1: C](#week-1-c)
4. [Linux / Shell Commands](#linux--shell-commands)
5. [Tooling](#tooling)
6. [Connections to Nova](#connections-to-nova)
7. [Questions & Things to Revisit](#questions--things-to-revisit)

---

## Computer Science Glossary

General terms worth burning in. These show up everywhere in software.

### Core Concepts

| Term | Meaning |
|------|---------|
| **Schema** | The shape/contract of data — what fields exist and what types |
| **Migration** | Code that translates between schema versions |
| **Dispatcher / Registry** | A lookup-table router from name → handler |
| **Fixture** | A known, frozen piece of input data used in tests. "Given THIS input, expect THAT output." |
| **Pure function** | No side effects, deterministic — same input always gives same output |
| **Idempotent** | Running it N times = running it once (safe to repeat) |
| **Indirection** | A layer between caller and implementation |
| **Separation of concerns** | Each module does one thing well |
| **Contract** | The promise a function makes about its input/output |
| **Provenance** | The origin/history of data — where it came from, how it got here |
| **Canonical solution** | The "official" or reference correct answer |
| **Cyclomatic complexity** | A measure of how many branching paths exist in code (lower = simpler) |
| **Conditional cascade** | A chain of if/elif/else statements |
| **Strangler fig pattern** | Gradually replacing old code by wrapping it, until the old is gone |

### Code Structure

| Term | Meaning |
|------|---------|
| **Source code** | What humans write (`.c`, `.py` files) |
| **Machine code** | What computers run (binary) |
| **Compiler** | Translates source code → machine code |
| **Interpreter** | Runs source code directly (Python) |
| **Library** | Pre-written code you can use |
| **Header file** (`.h`) | Declares *what* functions exist |
| **Implementation file** (`.c`) | Defines *how* functions work |
| **Argument / parameter** | What you pass into a function |
| **Return value** | What a function gives back |

---

## Week 0: Scratch & Foundations

### Binary / Base 2

- Computers count in **base 2** (binary) — only 0 and 1
- Each digit is a **bit**
- 8 bits = 1 **byte**
- Humans count in base 10 (decimal: 0-9)

### Core Programming Concepts

- **Functions** — reusable blocks of code that do one thing
- **Conditionals** — `if`, `else`, `elif` — decisions based on truth
- **Boolean expression** — a question with a yes/no (true/false) answer
- **Loops** — repeat an action (`while`, `for`)
- **Algorithms** — a step-by-step recipe to solve a problem
- **Side effects** — when a function changes something outside itself (prints, writes a file, modifies a variable)

### Scratch → C Bridge

Scratch uses colored blocks. C uses keywords. The *shapes* of Scratch blocks map directly to C concepts:
- Scratch "when green flag clicked" → C `main()` function
- Scratch "if" block → C `if` statement
- Scratch "repeat" → C `for` / `while` loop

---

## Week 1: C

### The Compilation Flow


| Command | What it does |
|---------|--------------|
| `code hello.c` | Open source code in editor |
| `make hello` | Compile source → machine code |
| `./hello` | Run the compiled program |

### Anatomy of a C Program

```c
#include <stdio.h>          // include a library (header file)

int main(void)              // every C program starts at main()
{
    printf("hello, world\n");  // print formatted text
    return 0;                  // exit code 0 = success
}

Escape sequeces(use backslash)

| Sequence | Meaning |
| --- | --- |
| \\n | New line |
| \\r | Carriage return (cursor back to start of line) |
| \\t | Tab |
| \\" | Literal double quote |
| \\' | Literal single quote |
| \\\\ | Literal backslash |

Commands in C

// Single-line comment
/* Block comment
   spans multiple lines */

Common libraries

| Header | What it gives you |
| --- | --- |
| stdio.h | Standard input/output (printf, scanf) |
| string.h | String handling |
| cs50.h | CS50's helper functions (get_string, get_int) |

Linux navigation

| Command | Meaning |
| --- | --- |
| cd <dir> | Change directory |
| cd .. | Go up one level |
| cd ~ | Go to home directory |
| pwd | Print working directory (where am I?) |
| ls | List files in current directory |
| ls -la | List with details + hidden files |

File operations

| Command | Meaning |
| --- | --- |
| cp <src> <dst> | Copy file or directory |
| mv <src> <dst> | Move or rename |
| rm <file> | Remove (delete) file |
| rmdir <dir> | Remove empty directory |
| rm -r <dir> | Remove directory and contents (careful!) |
| mkdir <name> | Make a new directory |
| touch <file> | Create empty file / update timestamp |
| cat <file> | Print file contents to screen |

Useful Extras

| Command | Meaning |
| --- | --- |
| grep <pattern> | Search text for a pattern |
| chmod | Change file permissions |
| which <cmd> | Find where a command lives |
| man <cmd> | Read the manual page |

Novs connections

| CS50 Concept | Where it shows up in Nova |
| --- | --- |
| Functions | Every Python function we've written |
| Conditionals | Branching logic in tools.py, dispatch.py |
| Libraries (stdio.h) | Python import statements |
| Header vs implementation | errors.py (declares) vs callers (use) |
| Compilation | Python skips this — it's interpreted |
| make | Like our pytest / orchestration scripts |
| Separation of concerns | Why we moved DispatchError to nova/core/errors.py |
| Registry pattern | The C.4 work — name → handler lookup |
| Fixtures | Our test data in tests/ |