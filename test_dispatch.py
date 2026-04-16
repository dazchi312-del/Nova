from tools.dispatcher import extract_tool_calls

test = '<<TOOL:file_read>>{"path": "test.py"}<<END_TOOL>>'
result = extract_tool_calls(test)
print(type(result))
print(result)
