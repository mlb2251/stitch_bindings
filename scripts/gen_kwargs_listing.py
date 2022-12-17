from stitch_core import compress
def help():
    try:
        compress(["foo"],1,help=True)
        assert False
    except BaseException as e:
        text = str(e)
    return text.split("OPTIONS:\n",1)[1]

text = help()

entries = text.split("\n\n")


# We want each entry to look like this:
"""
* - ``abstraction_prefix``
        - ``str``
        - ``"fn_"``
        - Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem 
          Lorem i
"""

import re

indent = ' '*8

print(f"""
.. list-table::
{indent}:header-rows: 1
{indent}:widths: 30 70

{indent}* - Argument
{indent}  - Description
{indent}* - ``programs <val>``
{indent}  - The ``List[str]`` of programs to learn abstractions from.
{indent}* - ``tasks <val>``
{indent}  - A ``List[str]`` equal in length to ``programs`` that gives names for the task each program is solving. If not provided, defaults to each program solving a unique task. This is only relevant for a DreamCoder-style compression metric that takes a *min* over programs within each task. See :ref:`compression_objectives` for more details.""")

for entry in entries:
    lines = [l.strip() for l in entry.split('\n') if l.strip() != '']
    # --no-top-lambda becomes no_top_lambda
    arg = re.search(r'--((-|\w)+)', lines[0]).group(1).replace('-','_')
    if arg in ['help', 'shuffle', 'truncate']:
        continue

    takes_val = re.search(r'<(\w+)>', lines[0]) is not None
    val = ' <val>' if takes_val else ''
    print(f"{indent}* - ``{arg}{val}``")
    print(f"{indent}  - ", end="")

    lines = lines[1:]
    lines = [l.replace("`","``").replace('fn_]','fn\_]') for l in lines]

    if len(lines) > 0:
        print(f"{lines[0]}")
    for line in lines[1:]:
        print(f"{indent}    {line}")
