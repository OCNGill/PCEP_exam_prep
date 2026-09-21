"""Build and validate the PCEP-only flashcard deck.

The deck is deliberately scoped to the active PCEP-30-02 objectives. The
official Python Institute syllabus is the authority; w3resource is retained as
a reputable practice-guide cross-reference. Code answers are executed in an
isolated subprocess with a timeout.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path

HERE = Path(__file__).resolve().parent
OFFICIAL = "https://pythoninstitute.org/pcep-exam-syllabus"
PRACTICE = "https://www.w3resource.com/python/certificate/index.php"
SOURCE = "Python Institute PCEP-30-02 official syllabus + w3resource PCEP guide"


def card(q: str, a: str, topic: str, objective: str, *, code: str | None = None,
         expected_output: str | None = None, expected_exception: str | None = None) -> dict:
    return {
        "q": q,
        "a": a,
        "topic": topic,
        "objective": objective,
        "source": SOURCE,
        "source_url": OFFICIAL,
        "practice_url": PRACTICE,
        "verification": "execution-verified" if code else "syllabus-reviewed",
        "code": textwrap.dedent(code).strip() if code else None,
        "expected_output": expected_output,
        "expected_exception": expected_exception,
    }


CARDS = [
    # Block 1 — Computer Programming and Python Fundamentals (25)
    card("What does a Python interpreter do with source code?",
         "It executes the source directly, typically line by line, rather than first producing a standalone machine-code executable.",
         "Block 1 · Python fundamentals", "PCEP-30-02 1.1"),
    card("How is a compiler different from an interpreter?",
         "A compiler translates a whole program before execution; an interpreter executes source instructions directly, commonly line by line.",
         "Block 1 · Python fundamentals", "PCEP-30-02 1.1"),
    card("What is the difference between syntax and semantics?",
         "Syntax is the formal structure and grammar of code; semantics is the meaning of valid code.",
         "Block 1 · Python fundamentals", "PCEP-30-02 1.1"),
    card("What is a Python keyword?",
         "A reserved word with special language meaning; it cannot be used as an identifier.",
         "Block 1 · Python structure", "PCEP-30-02 1.2"),
    card("What role does indentation play in Python?",
         "It defines block boundaries and nesting. Inconsistent indentation raises an IndentationError.",
         "Block 1 · Python structure", "PCEP-30-02 1.2"),
    card("How do you write a single-line Python comment?",
         "Put a # character before the comment text; everything after # on that line is ignored.",
         "Block 1 · Python structure", "PCEP-30-02 1.2"),
    card("What makes an identifier valid in Python?",
         "It starts with a letter or underscore, then contains letters, digits, or underscores; it is case-sensitive and cannot be a keyword.",
         "Block 1 · Variables and naming", "PCEP-30-02 1.3"),
    card("What are Python's two Boolean literals?",
         "True and False, with capital first letters.",
         "Block 1 · Literals and types", "PCEP-30-02 1.3"),
    card("How do int and float values differ in Python?",
         "int stores whole numbers exactly; float stores approximate binary floating-point values.",
         "Block 1 · Literals and types", "PCEP-30-02 1.3"),
    card("What number does 1.2e3 represent?",
         "1200.0: scientific notation means 1.2 × 10³.",
         "Block 1 · Numerals and literals", "PCEP-30-02 1.3",
         code="print(1.2e3)", expected_output="1200.0\n"),
    card("Which quote styles can delimit a Python string?",
         "Single quotes, double quotes, or triple quotes for multi-line strings.",
         "Block 1 · Strings", "PCEP-30-02 1.3"),
    card("What prefixes mark binary, octal, and hexadecimal integer literals?",
         "0b for binary, 0o for octal, and 0x for hexadecimal.",
         "Block 1 · Numerals and literals", "PCEP-30-02 1.3"),
    card("What naming style does PEP 8 recommend for variables and functions?",
         "snake_case: lowercase words separated by underscores; constants commonly use UPPER_CASE.",
         "Block 1 · Naming conventions", "PCEP-30-02 1.3"),
    card("What does + do when both operands are strings?",
         "It concatenates them into one string.",
         "Block 1 · Operators", "PCEP-30-02 1.4",
         code="print('go' + 'od')", expected_output="good\n"),
    card("What does * do when one operand is a string and the other is an integer?",
         "It repeats the string that many times.",
         "Block 1 · Operators", "PCEP-30-02 1.4",
         code="print('ha' * 3)", expected_output="hahaha\n"),
    card("What is the difference between / and //?",
         "/ performs true division and returns a float; // performs floor division and returns an integer when both operands are integers.",
         "Block 1 · Operators", "PCEP-30-02 1.4",
         code="print(7 / 2)\nprint(7 // 2)", expected_output="3.5\n3\n"),
    card("What does the % operator return?",
         "The remainder after division.",
         "Block 1 · Operators", "PCEP-30-02 1.4",
         code="print(10 % 3)", expected_output="1\n"),
    card("How does exponentiation bind: 2 ** 3 ** 2?",
         "Right to left: 2 ** (3 ** 2) = 2 ** 9 = 512.",
         "Block 1 · Operators", "PCEP-30-02 1.4",
         code="print(2 ** 3 ** 2)", expected_output="512\n"),
    card("What does the bitwise ^ operator do?",
         "It performs bitwise exclusive OR: each result bit is 1 when the input bits differ.",
         "Block 1 · Bitwise operators", "PCEP-30-02 1.4",
         code="print(5 ^ 3)", expected_output="6\n"),
    card("What does short-circuit evaluation mean for and and or?",
         "Python stops as soon as the result is known: and stops at False; or stops at True.",
         "Block 1 · Boolean operators", "PCEP-30-02 1.4",
         code="print(False or (3 > 2))", expected_output="True\n"),
    card("What does 1 < x < 5 mean?",
         "It is a chained comparison equivalent to (1 < x) and (x < 5).",
         "Block 1 · Comparisons", "PCEP-30-02 1.4",
         code="x = 3\nprint(1 < x < 5)", expected_output="True\n"),
    card("What is the difference between = and ==?",
         "= assigns a value; == tests equality.",
         "Block 1 · Operators", "PCEP-30-02 1.4"),
    card("What do int('7') and float('7') produce?",
         "int('7') produces 7; float('7') produces 7.0.",
         "Block 1 · Type casting", "PCEP-30-02 1.4",
         code="print(int('7') + 2)\nprint(float('7') + 2)", expected_output="9\n9.0\n"),
    card("What do print(..., sep=...) and print(..., end=...) control?",
         "sep controls the string between arguments; end controls what is printed after the final argument, replacing the default newline.",
         "Block 1 · Console I/O", "PCEP-30-02 1.5",
         code="print('a', 'b', sep=':', end='!')", expected_output="a:b!"),
    card("What type does input() return?",
         "A string; convert it with int() or float() when numeric input is needed.",
         "Block 1 · Console I/O", "PCEP-30-02 1.5"),

    # Block 2 — Control Flow (25)
    card("When does an if block run?",
         "Only when its condition evaluates to True.",
         "Block 2 · Conditional flow", "PCEP-30-02 2.1"),
    card("How many branches run in an if/elif/else chain?",
         "At most one: the first true condition's branch; else runs only if none are true.",
         "Block 2 · Conditional flow", "PCEP-30-02 2.1"),
    card("What is a nested conditional?",
         "An if/elif/else block placed inside another block, allowing decisions within decisions.",
         "Block 2 · Conditional flow", "PCEP-30-02 2.1"),
    card("What does the pass instruction do?",
         "It performs no operation and acts as a syntactic placeholder where a statement is required.",
         "Block 2 · Loops and placeholders", "PCEP-30-02 2.2"),
    card("When does a while loop evaluate its condition?",
         "Before each iteration; if the condition is false initially, the body never runs.",
         "Block 2 · while loops", "PCEP-30-02 2.2"),
    card("What does a for loop iterate over?",
         "Each element of a sequence or other iterable, in order.",
         "Block 2 · for loops", "PCEP-30-02 2.2"),
    card("What values does range(5) produce?",
         "0, 1, 2, 3, 4 — the stop value is excluded.",
         "Block 2 · range()", "PCEP-30-02 2.2",
         code="print(list(range(5)))", expected_output="[0, 1, 2, 3, 4]\n"),
    card("What values does range(2, 8, 2) produce?",
         "2, 4, 6 — start is inclusive, stop is exclusive, and step is 2.",
         "Block 2 · range()", "PCEP-30-02 2.2",
         code="print(list(range(2, 8, 2)))", expected_output="[2, 4, 6]\n"),
    card("What does the in operator test?",
         "Membership: whether a value occurs in a sequence or collection.",
         "Block 2 · Iteration", "PCEP-30-02 2.2"),
    card("What does break do inside a loop?",
         "It immediately exits the nearest enclosing loop.",
         "Block 2 · Loop control", "PCEP-30-02 2.2"),
    card("What does continue do inside a loop?",
         "It skips the rest of the current iteration and starts the next iteration.",
         "Block 2 · Loop control", "PCEP-30-02 2.2",
         code="for x in [1, 2, 3]:\n    if x == 2:\n        continue\n    print(x)", expected_output="1\n3\n"),
    card("When does a while-else else block run?",
         "When the loop ends normally without break; it does not run after break.",
         "Block 2 · Loop else", "PCEP-30-02 2.2"),
    card("When does a for-else else block run?",
         "When the loop exhausts the iterable without break; it does not run after break.",
         "Block 2 · Loop else", "PCEP-30-02 2.2"),
    card("How do nested loops execute?",
         "The inner loop completes its iterations for each single iteration of the outer loop.",
         "Block 2 · Nested loops", "PCEP-30-02 2.2"),
    card("What is printed by this loop?",
         "0, then 1, then 2, each on its own line.",
         "Block 2 · while loops", "PCEP-30-02 2.2",
         code="i = 0\nwhile i < 3:\n    print(i)\n    i += 1", expected_output="0\n1\n2\n"),
    card("What is printed by this continue example?",
         "1 and 3; the iteration where x == 2 is skipped.",
         "Block 2 · continue", "PCEP-30-02 2.2",
         code="for x in [1, 2, 3]:\n    if x == 2:\n        continue\n    print(x)", expected_output="1\n3\n"),
    card("What is printed by this break example?",
         "Only 1; break exits before 2 and 3 are printed.",
         "Block 2 · break", "PCEP-30-02 2.2",
         code="for x in [1, 2, 3]:\n    if x == 2:\n        break\n    print(x)", expected_output="1\n"),
    card("What total is produced by this accumulation loop?",
         "9, because 2 + 3 + 4 = 9.",
         "Block 2 · Loop state", "PCEP-30-02 2.2",
         code="total = 0\nfor n in [2, 3, 4]:\n    total += n\nprint(total)", expected_output="9\n"),
    card("What happens when break is the first statement in a while True loop?",
         "The loop terminates immediately and produces no output from the body.",
         "Block 2 · break", "PCEP-30-02 2.2",
         code="while True:\n    break", expected_output=""),
    card("What is printed when a loop is exited with break and has an else clause?",
         "Only 'done'; the loop's else clause is skipped after break.",
         "Block 2 · Loop else", "PCEP-30-02 2.2",
         code="for x in [1, 2]:\n    if x == 2:\n        break\nelse:\n    print('else')\nprint('done')", expected_output="done\n"),
    card("What list does range(3, 0, -1) produce?",
         "[3, 2, 1]; a negative step counts downward and excludes the stop value.",
         "Block 2 · range()", "PCEP-30-02 2.2",
         code="print(list(range(3, 0, -1)))", expected_output="[3, 2, 1]\n"),
    card("What does a for loop do when its iterable is a string?",
         "It iterates one character at a time.",
         "Block 2 · Iteration", "PCEP-30-02 2.2",
         code="for ch in 'ab':\n    print(ch)", expected_output="a\nb\n"),
    card("When does a while condition get checked relative to its body?",
         "Before every body execution, including the first one.",
         "Block 2 · while loops", "PCEP-30-02 2.2"),
    card("What does break affect in nested loops?",
         "Only the innermost loop containing the break.",
         "Block 2 · Nested loops", "PCEP-30-02 2.2",
         code="for i in range(2):\n    for j in range(2):\n        if j == 1:\n            break\n        print(i, j)", expected_output="0 0\n1 0\n"),
    card("What does continue affect in nested loops?",
         "Only the current iteration of the innermost loop containing it.",
         "Block 2 · Nested loops", "PCEP-30-02 2.2",
         code="for i in range(2):\n    for j in range(3):\n        if j == 1:\n            continue\n        print(i, j)", expected_output="0 0\n0 2\n1 0\n1 2\n"),

    # Block 3 — Data Collections (25)
    card("How are list indexes numbered?",
         "From zero at the first element; list[0] is the first item.",
         "Block 3 · Lists", "PCEP-30-02 3.1"),
    card("What does a negative list index mean?",
         "It counts backward from the end; -1 is the last element.",
         "Block 3 · Lists", "PCEP-30-02 3.1",
         code="print([10, 20, 30][-1])", expected_output="30\n"),
    card("What does a slice [start:stop] include?",
         "Elements from start through stop - 1; stop is excluded.",
         "Block 3 · Lists and strings", "PCEP-30-02 3.1 / 3.4",
         code="print([0, 1, 2, 3][1:3])", expected_output="[1, 2]\n"),
    card("What does len() return?",
         "The number of items in a collection or characters in a string.",
         "Block 3 · Collections", "PCEP-30-02 3.1 / 3.4"),
    card("What does list.append(value) do?",
         "It mutates the list by adding value to its end.",
         "Block 3 · List methods", "PCEP-30-02 3.1",
         code="xs = [1, 2]\nxs.append(3)\nprint(xs)", expected_output="[1, 2, 3]\n"),
    card("What does list.insert(index, value) do?",
         "It mutates the list by placing value before the specified index.",
         "Block 3 · List methods", "PCEP-30-02 3.1",
         code="xs = [1, 3]\nxs.insert(1, 2)\nprint(xs)", expected_output="[1, 2, 3]\n"),
    card("What does del list[index] do?",
         "It removes the item at that index and mutates the list.",
         "Block 3 · List mutation", "PCEP-30-02 3.1",
         code="xs = [1, 2, 3]\ndel xs[1]\nprint(xs)", expected_output="[1, 3]\n"),
    card("What is the difference between sorted(xs) and xs.sort()?",
         "sorted(xs) returns a new sorted list; xs.sort() mutates xs and returns None.",
         "Block 3 · List functions", "PCEP-30-02 3.1",
         code="a = [3, 1, 2]\nb = sorted(a)\na.sort()\nprint(a)\nprint(b)", expected_output="[1, 2, 3]\n[1, 2, 3]\n"),
    card("What does [x*x for x in range(4) if x % 2 == 0] produce?",
         "[0, 4]; the comprehension filters even x values (0 and 2) and squares them.",
         "Block 3 · List comprehensions", "PCEP-30-02 3.1",
         code="print([x*x for x in range(4) if x % 2 == 0])", expected_output="[0, 4]\n"),
    card("What is the difference between b = a and b = a[:] for a list?",
         "b = a creates an alias to the same list; b = a[:] creates a shallow independent copy.",
         "Block 3 · Copying lists", "PCEP-30-02 3.1",
         code="a = [1, 2]\nb = a\nc = a[:]\nb.append(3)\nprint(c)", expected_output="[1, 2]\n"),
    card("How do you access an element in a nested list?",
         "Use multiple indexes: matrix[row][column].",
         "Block 3 · Nested lists", "PCEP-30-02 3.1",
         code="m = [[1, 2], [3, 4]]\nprint(m[1][0])", expected_output="3\n"),
    card("What do in and not in test in a list?",
         "Whether a value is present or absent from the list.",
         "Block 3 · Lists", "PCEP-30-02 3.1"),
    card("Can a tuple be changed after creation?",
         "No. Tuples are immutable; their items cannot be assigned, appended, or deleted.",
         "Block 3 · Tuples", "PCEP-30-02 3.2"),
    card("How do you create a one-element tuple?",
         "Add a trailing comma: (value,). Parentheses alone do not make a tuple.",
         "Block 3 · Tuples", "PCEP-30-02 3.2"),
    card("Can tuples be indexed and sliced?",
         "Yes. They support the same sequence indexing and slicing operations as lists, but cannot be mutated.",
         "Block 3 · Tuples", "PCEP-30-02 3.2"),
    card("Can a list stored inside a tuple be mutated?",
         "Yes. The tuple cannot rebind that slot, but the mutable list object inside it can change.",
         "Block 3 · Tuples and lists", "PCEP-30-02 3.2",
         code="t = ([1],)\nt[0].append(2)\nprint(t)", expected_output="([1, 2],)\n"),
    card("How do you retrieve a value from a dictionary?",
         "Use its key in square brackets, such as data['name'], or use a method such as get().",
         "Block 3 · Dictionaries", "PCEP-30-02 3.3",
         code="d = {'a': 1}\nprint(d['a'])", expected_output="1\n"),
    card("How do you add or replace a dictionary entry?",
         "Assign to a key: data[key] = value; an existing key is replaced, while a new key is added.",
         "Block 3 · Dictionaries", "PCEP-30-02 3.3",
         code="d = {'a': 1}\nd['b'] = 2\nprint(d['a'], d['b'])", expected_output="1 2\n"),
    card("What do keys(), values(), and items() return?",
         "Views of the dictionary's keys, values, and (key, value) pairs, respectively.",
         "Block 3 · Dictionary methods", "PCEP-30-02 3.3",
         code="d = {'a': 1, 'b': 2}\nprint(list(d.keys()))\nprint(list(d.values()))\nprint(list(d.items()))", expected_output="['a', 'b']\n[1, 2]\n[('a', 1), ('b', 2)]\n"),
    card("What does key in dictionary test?",
         "Whether the dictionary contains that key, not whether it contains a particular value.",
         "Block 3 · Dictionaries", "PCEP-30-02 3.3",
         code="d = {'a': 1}\nprint('a' in d, 1 in d)", expected_output="True False\n"),
    card("What does {x: x*x for x in range(3)} produce?",
         "{0: 0, 1: 1, 2: 4}; it builds a dictionary with keys and computed values.",
         "Block 3 · Dictionary comprehensions", "PCEP-30-02 3.3",
         code="print({x: x*x for x in range(3)})", expected_output="{0: 0, 1: 1, 2: 4}\n"),
    card("What does 'Python'[1:4] produce?",
         "'yth'; string slicing uses the same start-inclusive, stop-exclusive rule.",
         "Block 3 · Strings", "PCEP-30-02 3.4",
         code="print('Python'[1:4])", expected_output="yth\n"),
    card("Can characters inside a string be assigned to?",
         "No. Strings are immutable; create a new string instead of changing characters in place.",
         "Block 3 · Strings", "PCEP-30-02 3.4"),
    card("What does \\n mean inside a normal Python string?",
         "A newline escape, causing output to move to the next line.",
         "Block 3 · Strings", "PCEP-30-02 3.4",
         code="print('a\\nb')", expected_output="a\nb\n"),
    card("What does '-'.join('a b'.split()) produce?",
         "'a-b'; split() separates on whitespace and join() inserts the separator.",
         "Block 3 · String methods", "PCEP-30-02 3.4",
         code="print('-'.join('a b'.split()))", expected_output="a-b\n"),

    # Block 4 — Functions and Exceptions (25)
    card("What keyword defines a user-defined function?",
         "def, followed by the function name, parameter list, colon, and indented body.",
         "Block 4 · Functions", "PCEP-30-02 4.1"),
    card("What does return do inside a function?",
         "It sends a value back to the caller and immediately ends the function's execution.",
         "Block 4 · Functions", "PCEP-30-02 4.1",
         code="def f(x):\n    return x * 2\nprint(f(4))", expected_output="8\n"),
    card("What does a function return when it has no return statement?",
         "None.",
         "Block 4 · None and functions", "PCEP-30-02 4.1",
         code="def f():\n    pass\nprint(f())", expected_output="None\n"),
    card("Why does a recursive function need a base case?",
         "The base case stops the recursion; without a reachable base case, calls continue until a recursion or resource limit is hit.",
         "Block 4 · Recursion", "PCEP-30-02 4.1",
         code="def fact(n):\n    return 1 if n <= 1 else n * fact(n - 1)\nprint(fact(5))", expected_output="120\n"),
    card("What is positional argument passing?",
         "Arguments are matched to parameters by their order in the call.",
         "Block 4 · Arguments", "PCEP-30-02 4.2",
         code="def f(a, b):\n    print(a, b)\nf(1, 2)", expected_output="1 2\n"),
    card("What is keyword argument passing?",
         "Arguments are matched to parameters by name, so order can be changed.",
         "Block 4 · Arguments", "PCEP-30-02 4.2",
         code="def f(a, b):\n    print(a, b)\nf(b=2, a=1)", expected_output="1 2\n"),
    card("What does a default parameter value do?",
         "It supplies a value when the caller omits that argument.",
         "Block 4 · Default parameters", "PCEP-30-02 4.2",
         code="def f(a=3):\n    print(a)\nf()\nf(8)", expected_output="3\n8\n"),
    card("What is the difference between a parameter and an argument?",
         "A parameter is the variable named in a function definition; an argument is the value supplied in a call.",
         "Block 4 · Arguments", "PCEP-30-02 4.2"),
    card("Where can a local variable be read?",
         "Inside the function body where it is defined; it is not automatically visible outside that function.",
         "Block 4 · Scope", "PCEP-30-02 4.2",
         code="x = 1\ndef f():\n    x = 2\n    print(x)\nf()\nprint(x)", expected_output="2\n1\n"),
    card("What does the global keyword allow inside a function?",
         "It tells Python that assignments refer to the module-level variable rather than creating a new local variable.",
         "Block 4 · Scope", "PCEP-30-02 4.2",
         code="x = 1\ndef f():\n    global x\n    x = 2\nf()\nprint(x)", expected_output="2\n"),
    card("What is name shadowing?",
         "A local name hides an outer name with the same spelling inside its scope.",
         "Block 4 · Scope", "PCEP-30-02 4.2",
         code="value = 1\ndef f(value):\n    return value + 1\nprint(f(4), value)", expected_output="5 1\n"),
    card("What does yield do in a function?",
         "It produces a generator value and pauses the function state until the next value is requested.",
         "Block 4 · Generators", "PCEP-30-02 4.1",
         code="def g():\n    yield 1\n    yield 2\nprint(list(g()))", expected_output="[1, 2]\n"),
    card("What is the relationship between BaseException and Exception?",
         "Exception inherits from BaseException; SystemExit and KeyboardInterrupt also inherit from BaseException but are not ordinary Exception subclasses.",
         "Block 4 · Exception hierarchy", "PCEP-30-02 4.3"),
    card("What code belongs in a try block?",
         "Statements that might raise an exception and whose failure should be handled by an except clause.",
         "Block 4 · Exception handling", "PCEP-30-02 4.4",
         code="try:\n    print('ok')\nexcept:\n    print('bad')", expected_output="ok\n"),
    card("When does an except branch run?",
         "When the try block raises an exception matching that branch.",
         "Block 4 · Exception handling", "PCEP-30-02 4.4",
         code="try:\n    int('x')\nexcept ValueError:\n    print('caught')", expected_output="caught\n"),
    card("Why order except branches from specific to general?",
         "Python uses the first matching branch; a broad Exception branch first would hide more specific handlers.",
         "Block 4 · Exception handling", "PCEP-30-02 4.4",
         code="try:\n    int('x')\nexcept Exception:\n    print('E')\nexcept ValueError:\n    print('V')", expected_output="E\n"),
    card("How can one except clause catch several exception types?",
         "Put the types in a parenthesized tuple: except (TypeError, ValueError):.",
         "Block 4 · Exception handling", "PCEP-30-02 4.4",
         code="for value in ['x', 'y']:\n    try:\n        int(value)\n    except (ValueError, TypeError):\n        print('caught')", expected_output="caught\ncaught\n"),
    card("Which exception is raised by an invalid list index?",
         "IndexError, a LookupError subclass.",
         "Block 4 · Built-in exceptions", "PCEP-30-02 4.3",
         code="[1, 2][5]", expected_exception="IndexError"),
    card("Which exception is raised when a dictionary key is absent?",
         "KeyError, a LookupError subclass.",
         "Block 4 · Built-in exceptions", "PCEP-30-02 4.3",
         code="{'a': 1}['b']", expected_exception="KeyError"),
    card("Which exception is raised by 1 + '2'?",
         "TypeError, because the operand types do not support that operation.",
         "Block 4 · Built-in exceptions", "PCEP-30-02 4.3",
         code="1 + '2'", expected_exception="TypeError"),
    card("Which exception is raised by int('x')?",
         "ValueError, because the string is not a valid integer literal.",
         "Block 4 · Built-in exceptions", "PCEP-30-02 4.3",
         code="int('x')", expected_exception="ValueError"),
    card("Which exception is raised by 1 / 0?",
         "ZeroDivisionError, an ArithmeticError subclass.",
         "Block 4 · Built-in exceptions", "PCEP-30-02 4.3",
         code="1 / 0", expected_exception="ZeroDivisionError"),
    card("Can an exception raised inside a called function be caught by the caller?",
         "Yes. If the callee does not handle it, it propagates through the function boundary to a matching caller-side except.",
         "Block 4 · Exception propagation", "PCEP-30-02 4.4",
         code="def f():\n    return 1 / 0\ntry:\n    f()\nexcept ZeroDivisionError:\n    print('caught')", expected_output="caught\n"),
    card("What does a bare except clause catch?",
         "Every exception, including SystemExit and KeyboardInterrupt; it is valid syntax but usually too broad for precise handling.",
         "Block 4 · Exception handling", "PCEP-30-02 4.4",
         code="try:\n    int('x')\nexcept:\n    print('caught')", expected_output="caught\n"),
    card("What does raise ValueError('bad') do?",
         "It explicitly raises a ValueError with the message 'bad'.",
         "Block 4 · Exception handling", "PCEP-30-02 4.4",
         code="try:\n    raise ValueError('bad')\nexcept ValueError:\n    print('caught')", expected_output="caught\n"),
]


def run_code(code: str) -> tuple[str | None, str | None]:
    proc = subprocess.run(
        [sys.executable, "-I", "-c", code],
        input="",
        text=True,
        capture_output=True,
        timeout=3,
        check=False,
    )
    if proc.returncode == 0:
        return proc.stdout, None
    # The last non-empty stderr line is stable for the expected built-in types.
    message = proc.stderr.strip().splitlines()
    return proc.stdout, message[-1].split(":", 1)[0] if message else "UnknownError"


def validate(cards: list[dict]) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    forbidden = ("scipy", "pandas", "numpy", "data science", "machine learning", "csv")
    counts = {f"Block {i}": 0 for i in range(1, 5)}
    for n, c in enumerate(cards, 1):
        required = ("id", "q", "a", "topic", "objective", "source", "source_url", "practice_url", "verification")
        for key in required:
            if not isinstance(c.get(key), str) or not c[key].strip():
                errors.append(f"card {n}: missing {key}")
        if c.get("id") != str(n):
            errors.append(f"card {n}: bad id")
        if c["q"] in seen:
            errors.append(f"card {n}: duplicate question")
        seen.add(c["q"])
        if not c["topic"].startswith("Block "):
            errors.append(f"card {n}: bad topic")
        else:
            block = "Block " + c["topic"].split(" ", 1)[1].split(" ", 1)[0]
            if block in counts:
                counts[block] += 1
        if not c["objective"].startswith("PCEP-30-02 "):
            errors.append(f"card {n}: bad objective")
        if c["source_url"] != OFFICIAL or c["practice_url"] != PRACTICE:
            errors.append(f"card {n}: bad source URL")
        lower = (c["q"] + " " + c["a"]).lower()
        if any(term in lower for term in forbidden):
            errors.append(f"card {n}: out-of-scope term")
        code = c.get("code")
        if code:
            try:
                stdout, exc = run_code(code)
            except subprocess.TimeoutExpired:
                errors.append(f"card {n}: code timed out")
                continue
            if c.get("expected_exception"):
                if exc != c["expected_exception"]:
                    errors.append(f"card {n}: expected {c['expected_exception']}, got {exc!r}; stderr={proc.stderr if False else ''}")
            elif stdout != c.get("expected_output"):
                errors.append(f"card {n}: expected output {c.get('expected_output')!r}, got {stdout!r}, exception {exc!r}")
    if len(cards) != 100:
        errors.append(f"expected 100 cards, got {len(cards)}")
    if any(v != 25 for v in counts.values()):
        errors.append(f"block distribution is not 25/25/25/25: {counts}")
    return errors


def main() -> int:
    for i, c in enumerate(CARDS, 1):
        c["id"] = str(i)
    errors = validate(CARDS)
    if errors:
        print("FLASHCARD VALIDATION FAILED")
        for error in errors[:50]:
            print("-", error)
        if len(errors) > 50:
            print(f"... {len(errors) - 50} more errors")
        return 1

    Path(HERE, "flashcards.json").write_text(
        json.dumps(CARDS, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    bank = json.loads(Path(HERE, "pcep_bank.json").read_text(encoding="utf-8"))
    Path(HERE, "bank.js").write_text(
        "const PCEP_BANK = " + json.dumps(bank, ensure_ascii=False) + ";\n"
        + "const PCEP_FLASHCARDS = " + json.dumps(CARDS, ensure_ascii=False) + ";\n",
        encoding="utf-8",
    )
    print(f"validated {len(CARDS)} PCEP-only flashcards")
    print("block distribution: 25 fundamentals · 25 control flow · 25 collections · 25 functions/exceptions")
    print("bank.js rebuilt with official-syllabus source metadata")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
