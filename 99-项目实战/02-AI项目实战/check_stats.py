import re, sys

f = sys.argv[1]
text = open(f, encoding='utf-8').read()
text_nocode = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
h1 = len(re.findall(r'^# [^#]', text_nocode, re.M))
h2 = len(re.findall(r'^## ', text_nocode, re.M))
code = len(re.findall(r'^```', text, re.M))
print(f'bytes={len(text.encode("utf-8"))} h1={h1} h2={h2} code_blocks={code//2}')
