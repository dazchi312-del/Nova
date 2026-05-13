## Week 1 Logic Map — How C Programs Work

A bird's-eye view of what happens when you write, compile, and run a C program.

### The Full Lifecycle


---

### Inside a C Program — Logical Flow

                ┌──────────────────┐
                │   #include <…>   │  Bring in libraries
                │   (header files) │  (stdio.h, cs50.h, etc.)
                └────────┬─────────┘
                         │
                         ▼
                ┌──────────────────┐
                │   int main(void) │  Entry point — every
                │                  │  C program starts here
                └────────┬─────────┘
                         │
                         ▼
                ┌──────────────────┐
                │       {          │  Open the function body
                └────────┬─────────┘
                         │
                         ▼
        ┌────────────────────────────────┐
        │  Statements (one per line)     │
        │  Each ends with ;              │
        │                                │
        │  • Declare variables           │
        │  • Get input (get_string, …)   │
        │  • Do calculations             │
        │  • Make decisions (if/else)    │
        │  • Loop (for/while)            │
        │  • Print output (printf)       │
        └────────────────┬───────────────┘
                         │
                         ▼
                ┌──────────────────┐
                │   return 0;      │  Tell the OS:
                │                  │  "I finished OK"
                └────────┬─────────┘
                         │
                         ▼
                ┌──────────────────┐
                │       }          │  Close the function body
                └──────────────────┘

---

### Decision Flow — How `if` Statements Work

          ┌─────────────────────┐
          │  Boolean Expression │   "Is this true?"
          │  (a question)       │
          └──────────┬──────────┘
                     │
            ┌────────┴────────┐
            │                 │
          TRUE              FALSE
            │                 │
            ▼                 ▼
    ┌───────────────┐  ┌───────────────┐
    │ Run if-block  │  │ Run else-block│
    │   { … }       │  │   { … }       │  (optional)
    └───────┬───────┘  └───────┬───────┘
            │                  │
            └────────┬─────────┘
                     ▼
             Continue program

---

### Loop Flow — How `while` Works

    ┌─────────────────────┐
    │  Check condition    │ ◄──────────┐
    │  (boolean question) │            │
    └──────────┬──────────┘            │
               │                       │
      ┌────────┴────────┐              │
      │                 │              │
    TRUE              FALSE            │
      │                 │              │
      ▼                 ▼              │
┌─────────────┐ Exit the loop │ │ Run body │ │ │ { … } │ │ └──────┬──────┘ │ │ │ └────────────────────────────────┘ (go back, check again)

---

### Mental Model — Three Layers of "Where Am I?"

┌───────────────────────────────────────────┐ │ LAYER 3: Your Program │ │ hello.c — what you wrote │ └───────────────────────────────────────────┘ ▲ │ runs on ┌───────────────────────────────────────────┐ │ LAYER 2: The Operating System │ │ Linux / macOS — manages files, memory │ └───────────────────────────────────────────┘ ▲ │ runs on ┌───────────────────────────────────────────┐ │ LAYER 1: The Hardware │ │ CPU, RAM — actually executes 1s and 0s │ └───────────────────────────────────────────┘




Every line of C you write eventually becomes electricity moving through transistors. That's not poetry — it's literally true.

---

### Quick Reference — The Week 1 Loop

For every program you write this week, the cycle is:


This loop — **write → compile → run → check** — is the heartbeat of C programming. Get comfortable with it and the rest is just adding vocabulary.


