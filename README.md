# Py++

Py++ is a small programming language that looks a lot like Python. It checks your code for common mistakes before running it.

That means a typo or a value with the wrong type is easier to spot. Py++ then translates your program into a native program you can run.

## Who is Py++ for?

Py++ is for students and beginners who want to:

- practise writing programs with variables, loops, lists, and functions;
- catch common mistakes, such as misspelling a variable name;
- explore how a programming language can translate code into a runnable program.

## Get started

### 1. Install the tools

You need Python 3.10 or newer and a C++17 compiler (such as `g++`).

- **Windows:** Install [MSYS2](https://www.msys2.org/). In the MSYS2 UCRT64 terminal, run `pacman -S mingw-w64-ucrt-x86_64-gcc`. Add `C:\msys64\ucrt64\bin` to your PATH, then restart VS Code. You can also use WSL and follow the Linux steps.
- **macOS:** Open Terminal and run `xcode-select --install`.
- **Debian or Ubuntu:** Open a terminal and run `sudo apt install g++`.

### 2. Create a program

Open the project folder in VS Code. Create a file ending in `.pyl`, such as `hello.pyl`, and write your code in it. You can use VS Code or another text editor to create the file.

### 3. Run it

In the VS Code terminal, go to the folder containing your `.pyl` file and run:

```sh
python pylc.py hello.pyl --run
```

Replace `hello.pyl` with your file's name. Py++ creates the translated C++ file and program next to your `.pyl` file.

## Running programs

| I want to... | Command |
| --- | --- |
| Compile and run | `python pylc.py prog.pyl --run` |
| Translate to C++ without running | `python pylc.py prog.pyl` |
| Run the compiled program again | `./prog` (macOS/Linux) or `prog.exe` (Windows) |
| Give the program input from a file | `./prog < answers.txt` |

## A tour of Py++

### Variables and types

Use `let` to create a variable. Py++ figures out its type from the first value. The type stays the same while the program runs.

```pyl
let name = "Ana"
let age = 20
let price = 9.5
let ok = True
age += 1
print(name, age, price, ok)
```

Output:

```text
Ana 21 9.5 True
```

| Type | Examples |
| --- | --- |
| `int` | `42`, `-7` |
| `float` | `3.14` (digits on both sides of the dot) |
| `str` | `"hello"`, `'hi'`, with escapes `\n`, `\t`, `\"` |
| `bool` | `True`, `False` |
| `list` | `[1, 2, 3]` (all items the same type) |
| `dict` | `{"a": 1}` (keys one type, values one type) |

Use `let` the first time you create a variable. After that, use `name = value` to change it. For example, `age = 21` updates an existing `age` variable.

You can store an integer in a float variable, but you cannot store a float in an integer variable.

### Operators

| Kind | Operators |
| --- | --- |
| Arithmetic | `+` `-` `*` `/` `//` `%` `**` (`/` always gives a float) |
| Comparison | `==` `!=` `<` `>` `<=` `>=` (chains like `1 < x < 10` work) |
| Logic | `and` `or` `not` |
| Update | `+=` `-=` `*=` `/=` |

### Loops

Use a `for` loop to repeat instructions for each item. `range(3)` gives you the numbers 0, 1, and 2.

```pyl
for i in range(3):
    print("i =", i)
for i in range(10, 0, -4):
    print("down", i)
for ch in "hey":
    print(ch)
let total = 0
for n in [4, 8, 15]:
    if n == 8:
        continue
    if n > 10:
        break
    total += n
print("total", total)
```

Output:

```text
i = 0
i = 1
i = 2
down 10
down 6
down 2
h
e
y
total 4
```

You can loop over a `range`, list, string, or dictionary (a dictionary loop visits its keys). A `while` loop repeats as long as its condition is true. Use `break` to stop a loop, `continue` to skip to the next item, or `pass` as a placeholder.

### Functions and scope

Use `def` to create a function. `return` sends a result back to the place where the function was called.

```pyl
def area(w, h):
    return w * h

def greet(name):
    print("hi", name)

let visits = 0
def visit():
    visits += 1

greet("Ana")
print(area(3, 4))
visit()
visit()
print(visits)
```

Output:

```text
hi Ana
12
2
```

**Where variables work:** A variable created inside a function is local to that function. A function can also read or update a variable created at the top level. If a function creates a local variable with the same name as a top-level one, the local variable is used inside that function.

Functions can call themselves; this is called recursion. Py++ learns a function's parameter types from its first call, so use the same types in later calls. To pass a list or dictionary to a function, save it in a variable first.

### Lists and dictionaries

Lists store items in order. Dictionaries store values under keys.

```pyl
let scores = [90, 85, 77]
append(scores, 100)
print(scores, len(scores), scores[-1])
scores[0] = 95
print(sorted(scores), sum(scores))
let ages = {"ann": 31, "bob": 27}
ages["cy"] = 45
print(ages["ann"], keys(ages), contains(ages, "bob"))
let words = split("the quick brown fox")
print(words, upper(words[0]), len(words))
```

Output:

```text
[90, 85, 77, 100] 4 100
[77, 85, 95, 100] 357
31 ['ann', 'bob', 'cy'] True
['the', 'quick', 'brown', 'fox'] THE 4
```

Negative list positions count from the end: `scores[-1]` is the last item. An empty list (`[]`) or dictionary (`{}`) gets its item types from the first value you add.

### Built-in functions

These functions are ready to use; you do not need to define them yourself.

| Function | What it does |
| --- | --- |
| `print(a, b, ...)` | Shows values separated by spaces. `print()` prints a blank line. |
| `input(prompt)` | Reads a line as text. The prompt is optional. |
| `len(x)` | Returns the length of a list, dictionary, or string. |
| `str(x)`, `int(x)`, `float(x)` | Convert a value to text, an integer, or a decimal number. |
| `round(x)`, `abs(x)`, `sqrt(x)`, `pow(a, b)` | Do common math operations. |
| `min(a, b)`, `max(a, b)` | Return the smaller or larger of two numbers of the same type. |
| `sum(xs)`, `sorted(xs)` | Add up a list of numbers, or return a sorted copy of a list. |
| `append(xs, item)` | Adds an item to the end of a list. |
| `keys(d)` | Returns a list of a dictionary's keys. |
| `contains(x, item)` | Checks whether an item is in a list, string, or dictionary's keys. |
| `upper(s)`, `lower(s)` | Change a string to uppercase or lowercase. |
| `split(s)`, `split(s, sep)` | Splits a string into a list of strings. |

## Understanding error messages

Error messages include the line number in your `.pyl` file. That line is a good place to start looking for the problem.

### Errors found before your program runs

These errors stop the program before it starts.

| Message | What it means | What to try |
| --- | --- | --- |
| `SyntaxError (line N): expected :, got 'NEWLINE'` | A line of code is missing something, such as the `:` after an `if`. | Check the line shown and add the missing symbol. |
| `IndentationError (line N): use spaces, not tabs` | The line is indented with a tab. | Indent using 4 spaces. |
| `NameError (line N): name 'x' is not defined` | The program uses a name it does not know. | Check the spelling, or create it with `let` first. |
| `NameError (line N): 'x' is not declared (declare it first: let x = ...)` | You tried to change a variable that has not been created. | Create it with `let x = ...`, or check the spelling. |
| `NameError (line N): 'x' is already declared in this scope` | The same variable is created twice in the same scope. | Remove the extra `let` and update it with `x = ...`. |
| `TypeError (line N): variable 'count': expected int, got str` | A variable was given a value of a different type. | Keep the same type, or create a new variable. |
| `TypeError (line N): add() takes 2 argument(s), got 1` | A function call is missing an argument. | Check how many arguments the function needs. |
| `TypeError (line N): ... put the list/dict in a variable first ...` | A list or dictionary was written directly inside a function call. | Save it in a variable, then pass the variable. |
| `ValueError (line N): integer literal too large ...` | The whole number is too large for Py++. | Try a smaller number. |


### Errors while your program runs

If one of these happens, Py++ stops the program and shows the line where it happened.

| Message | What it means |
| --- | --- |
| `IndexError: list index out of range` | The list or string position you asked for does not exist. |
| `KeyError: key not found` | The dictionary does not have that key. Use `contains` to check first. |
| `ZeroDivisionError: division by zero` | A number was divided by zero. |
| `ValueError: invalid literal for int(): 'abc'` | `int()` or `float()` received text that is not a number. |
| `RecursionError: maximum recursion depth exceeded` | A function called itself too many times. Check that it has a stopping condition. |
| `EOFError: no input available` | `input()` was called, but there was no more input to read. |

### Messages from the tools

| Message | What it means |
| --- | --- |
| `error: file not found: x.pyl` | Check that the file name is correct and that your terminal is in the right folder. |
| `error: g++ not found - install a C++17 compiler` | Install a C++17 compiler by following the setup steps above. |
| `error: the generated C++ did not compile` | This may be a Py++ bug. If you can, report it along with the program that caused it. |
| `InternalError: ...` | This may be a Py++ bug. If you can, report it along with the program that caused it. |

## What Py++ does not support yet

These are current limits of the language:

- A variable's type cannot change after it is created. For example, `x /= 2` works only if `x` is already a float.
- A function uses the parameter types from its first call. Later calls must use the same types.
- Copying a list or dictionary to another variable makes a separate copy.
- Whole numbers have a maximum size. Very large results can wrap around.
- Dictionary keys are listed in sorted order.
- Py++ does not yet support classes, tuples, `None`, lambda, `try`/`except`, imports, f-strings, slicing, or the `in` operator. Use `contains` to check for an item.

## Running the tests

The `tests` folder contains sample programs. Each `.pyl` test has a matching `.out` file with the expected output, or a `.err` file with part of the expected error message.

Run the tests from the project folder:

```sh
python tests/run_tests.py
```

The test runner prints `PASS` or `FAIL` for each test. It exits with an error code if any test fails.

## How Py++ works

Py++ reads your `.pyl` file, checks it, translates it to C++, then uses `g++` to build a native program:

```text
.pyl file -> lexer -> parser -> type checker -> C++ code -> g++ -> runnable program
```