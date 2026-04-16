from core.dispatcher import dispatch

fake_output = '[TOOL]\n{"tool": "read_file", "args": {"path": "nova.py"}}\n[/TOOL]'

print("--- TEST 1: dry_run=True ---")
result = dispatch(fake_output, dry_run=True)
print(result)

print("\n--- TEST 2: dry_run=False ---")
result2 = dispatch(fake_output, dry_run=False)
print(result2)
