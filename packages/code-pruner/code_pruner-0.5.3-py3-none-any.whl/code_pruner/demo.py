from pathlib import Path
from prune import prune_code
from pruning.data_types import ExceptPatterns, Patterns

python_file = 'data/example.py'
code = Path(python_file).read_text()

patterns = [
    *Patterns.ALL,
    # *ExceptPatterns.IMPORT,
    # *ExceptPatterns.FUNCTION_DOCSTRING,
    *ExceptPatterns.CLASS_BODY,
    *Patterns.FUNCTION_DEF,
    *ExceptPatterns.FUNCTION_DOCSTRING
]

pruned_code = prune_code(code, patterns)

with(open(python_file.replace('.py', '_pruned.py'), 'w')) as f:
    f.write(pruned_code)