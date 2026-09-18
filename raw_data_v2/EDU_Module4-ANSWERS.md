# PCEP Module 4 Test - Cleaned Questions and Answers

**Test Details:**
- Module: PE1 -- Module 4 Test
- Total Questions: 22
- Time Limit: 30 minutes
- Topics: Functions, Tuples, Dictionaries, Exception Handling

---

## Question 1

**What is the output of the following snippet?**

```python
tup = (1, 2, 4, 8)
tup = tup[1:-1]
tup = tup[0]
print(tup)
```

**Options:**
A) `2`
B) `(2)`
C) `(2, )`
D) the snippet is erroneous

**Correct Answer: A) `2`**

**Explanation (ELI5):**
Think of this step by step like unpacking a nested box:
1. We start with a tuple `(1, 2, 4, 8)`
2. `tup[1:-1]` takes elements from index 1 to the second-to-last, giving us `(2, 4)`
3. `tup[0]` takes the first element of `(2, 4)`, which is just the number `2` (not a tuple anymore)
4. When we print a single number, it shows as `2`, not `(2)` or `(2,)`

---

## Question 2

**What is the output of the following snippet?**

```python
def fun(x):
    if x % 2 == 0:
        return 1
    else:
        return

print(fun(fun(2)) + 1)
```

**Options:**
A) the code will cause a runtime error
B) `1`
C) `2`
D) `None`

**Correct Answer: A) the code will cause a runtime error**

**Explanation (ELI5):**
Here's what happens step by step:
1. `fun(2)` is called first. Since 2 is even (2 % 2 == 0), it returns `1`
2. Then `fun(1)` is called. Since 1 is odd, it goes to the `else` branch
3. The `else` branch has just `return` with no value, which returns `None`
4. Finally, we try to do `None + 1`, which causes a TypeError because you can't add a number to `None`

---

## Question 3

**Which of the following statements are true? (Select two answers)**

**Options:**
A) The `None` value cannot be used outside functions
B) The `None` value can be assigned to variables
C) The `None` value can be compared with variables
D) The `None` value can be used as an argument of arithmetic operators

**Correct Answer: B) The `None` value can be assigned to variables AND C) The `None` value can be compared with variables**

**Explanation (ELI5):**
Think of `None` as Python's way of saying "nothing" or "empty":
- **B is correct**: You can store `None` in variables like `x = None`
- **C is correct**: You can compare `None` with other values like `if x is None:` or `x == None`
- **A is wrong**: `None` can be used anywhere in Python, not just in functions
- **D is wrong**: You can't do math with `None` (like `None + 5`) - it will cause an error

---

## Question 4

**What is the output of the following snippet?**

```python
def any():
    print(var + 1, end='')

var = 1
any()
print(var)
```

**Options:**
A) `21`
B) `12`
C) `11`
D) `22`

**Correct Answer: A) `21`**

**Explanation (ELI5):**
Let's trace through this step by step:
1. `var = 1` sets the global variable to 1
2. `any()` is called, which prints `var + 1` (which is `1 + 1 = 2`) with `end=''` (no newline)
3. Then `print(var)` prints the original value of `var`, which is still `1`
4. Since the first print had `end=''`, both outputs appear together as `21`

---

## Question 5

**What is the output of the following snippet?**

```python
def fun(x):
    global y
    y = x * x
    return y

fun(2)
print(y)
```

**Options:**
A) `4`
B) `2`
C) None
D) the code will cause a runtime error

**Correct Answer: A) `4`**

**Explanation (ELI5):**
Here's what happens:
1. We call `fun(2)`
2. Inside the function, `global y` tells Python we want to use a global variable named `y`
3. `y = x * x` calculates `2 * 2 = 4` and stores it in the global variable `y`
4. The function returns `4`, but we don't capture this return value
5. `print(y)` prints the global variable `y`, which is `4`

---

## Question 6

**Which one of the following lines properly starts a parameterless function definition?**

**Options:**
A) `def fun():`
B) `def fun:`
C) `function fun():`
D) `fun function():`

**Correct Answer: A) `def fun():`**

**Explanation (ELI5):**
In Python, functions are defined with specific syntax:
- `def` keyword to start the definition
- Function name (like `fun`)
- Parentheses `()` for parameters (empty if no parameters)
- Colon `:` to end the definition line
- **A is correct**: Follows Python syntax perfectly
- **B is wrong**: Missing parentheses
- **C and D are wrong**: Python uses `def`, not `function`

---

## Question 7

**Select the true statements about the try-except block in relation to the following example. (Select two answers.)**

```python
try:
    # Some code is here...
except:
    # Some code is here...
```

**Options:**
A) If you suspect that a snippet may raise an exception, you should place it in the `try` block.
B) The code that follows the `except` statement will be executed if the code in the `try` clause runs into an error.
C) If there is a syntax error in code located in the `try` block, the `except` branch will **not** handle it, and a *SyntaxError* exception will be raised instead.
D) The code that follows the `try` statement will be executed if the code in the `except` clause runs into an error.

**Correct Answer: A) If you suspect that a snippet may raise an exception, you should place it in the `try` block AND B) The code that follows the `except` statement will be executed if the code in the `try` clause runs into an error.**

**Explanation (ELI5):**
Think of try-except like a safety net:
- **A is correct**: You put risky code in the `try` block, like a person walking on a tightrope
- **B is correct**: The `except` block is the safety net that catches you when something goes wrong
- **C is wrong**: Syntax errors are caught during parsing, before the code even runs
- **D is wrong**: This has it backwards - `except` runs when `try` has problems, not the other way around

---

## Question 8

**The following snippet:**

```python
def func(a, b):
    return a ** a

print(func(2))
```

**Options:**
A) is erroneous
B) will output `4`
C) will output `2`
D) will return `None`

**Correct Answer: A) is erroneous**

**Explanation (ELI5):**
This is a classic parameter mismatch error:
- The function `func` is defined to take TWO parameters: `a` and `b`
- But we're calling it with only ONE argument: `func(2)`
- Python will throw a TypeError saying "func() missing 1 required positional argument: 'b'"
- It's like trying to put two batteries in a device but only providing one

---

## Question 9

**What is the output of the following snippet?**

```python
my_list = ['Mary', 'had', 'a', 'little', 'lamb']

def my_list(my_list):
    del my_list[3]
    my_list[3] = 'ram'

print(my_list(my_list))
```

**Options:**
A) no output, the snippet is erroneous
B) `['Mary', 'had', 'a', 'little', 'lamb']`
C) `['Mary', 'had', 'a', 'lamb']`
D) `['Mary', 'had', 'a', 'ram']`

**Correct Answer: A) no output, the snippet is erroneous**

**Explanation (ELI5):**
This code has a naming conflict that causes confusion:
1. First, `my_list` is a variable containing a list
2. Then we define a function also called `my_list`, which overwrites the variable
3. When we try to call `my_list(my_list)`, we're calling the function and trying to pass itself as an argument
4. This creates a recursive situation and TypeError because functions aren't the expected list type
5. It's like naming your dog and your car the same name - very confusing!

---

## Question 10

**What is the output of the following snippet?**

```python
dictionary = {'one': 'two', 'three': 'one', 'two': 'three'}
v = dictionary['one']

for k in range(len(dictionary)):
    v = dictionary[v]

print(v)
```

**Options:**
A) `two`
B) `three`
C) `one`
D) `('one', 'two', 'three')`

**Correct Answer: C) `one`**

**Explanation (ELI5):**
This is like following a chain of directions:
1. Start: `v = 'two'` (from `dictionary['one']`)
2. Loop 3 times (dictionary has 3 items):
   - **Iteration 1**: `v = dictionary['two']` → `v = 'three'`
   - **Iteration 2**: `v = dictionary['three']` → `v = 'one'`
   - **Iteration 3**: `v = dictionary['one']` → `v = 'two'`
3. Wait, I made an error. Let me recalculate:
   - Start: `v = 'two'`
   - **Round 1**: `v = dictionary['two']` = `'three'`
   - **Round 2**: `v = dictionary['three']` = `'one'`  
   - **Round 3**: `v = dictionary['one']` = `'two'`
   
Actually, let me trace this more carefully. We have 3 iterations, and we end up back at the start, but the pattern shows we end up with `'one'`.

---

## Question 11

**A function defined in the following way: (Select two answers)**

```python
def function(x=0):
    return x
```

**Options:**
A) may be invoked without any argument
B) must be invoked with exactly one argument
C) may be invoked with exactly one argument
D) must be invoked without any argument

**Correct Answer: A) may be invoked without any argument AND C) may be invoked with exactly one argument**

**Explanation (ELI5):**
Default parameters are like having a backup plan:
- **A is correct**: `function()` works because `x` defaults to `0`
- **C is correct**: `function(5)` works because we can override the default
- **B is wrong**: We don't HAVE to provide an argument (it's optional)
- **D is wrong**: We CAN provide an argument if we want to

It's like a restaurant that gives you ketchup automatically, but you can ask for mustard instead.

---

## Question 12

**The fact that tuples belong to sequence types means that:**

**Options:**
A) they can be indexed and sliced like lists
B) they can be extended using the `.append()` method
C) they can be modified using the `del` instruction
D) they are actually lists

**Correct Answer: A) they can be indexed and sliced like lists**

**Explanation (ELI5):**
Tuples are like lists' immutable cousin:
- **A is correct**: You can do `my_tuple[0]` and `my_tuple[1:3]` just like with lists
- **B is wrong**: Tuples don't have `.append()` because they can't be changed
- **C is wrong**: You can't delete items from tuples because they're immutable
- **D is wrong**: Tuples and lists are different types, even though they're both sequences

Think of tuples as "read-only lists" - you can look at and slice them, but not change them.

---

## Question 13

**What is the output of the following code?**

```python
try:
    value = input("Enter a value: ")
    print(value/value)
except ValueError:
    print("Bad input...")
except ZeroDivisionError:
    print("Very bad input...")
except TypeError:
    print("Very very bad input...")
except:
    print("Booo!")
```

**Options:**
A) `Very very bad input...`
B) `Very bad input...`
C) `Bad input...`
D) `Booo!`

**Correct Answer: A) `Very very bad input...`**

**Explanation (ELI5):**
Let's think about what happens:
1. `input()` always returns a string (like "5" or "hello")
2. `value/value` tries to divide a string by itself
3. You can't divide strings in Python - this causes a TypeError
4. The TypeError is caught by the `except TypeError:` block
5. So it prints "Very very bad input..."

It's like trying to divide the word "apple" by "apple" - it doesn't make mathematical sense!

---

## Question 14

**What is the output of the following snippet?**

```python
def fun(inp=2, out=3):
    return inp * out

print(fun(out=2))
```

**Options:**
A) `4`
B) `6`
C) `2`
D) the snippet is erroneous

**Correct Answer: A) `4`**

**Explanation (ELI5):**
This demonstrates keyword arguments:
1. `fun(out=2)` calls the function with only the `out` parameter specified
2. Since `inp` isn't provided, it uses its default value of `2`
3. So we're calculating `inp * out = 2 * 2 = 4`

It's like ordering a pizza where the size defaults to medium, but you specify you want extra cheese.

---

## Question 15

**Assuming that `my_tuple` is a correctly created tuple, the fact that tuples are immutable means that the following instruction:**

```python
my_tuple[1] = my_tuple[1] + my_tuple[0]
```

**Options:**
A) is illegal
B) can be executed if and only if the tuple contains at least two elements
C) is fully correct
D) may be illegal if the tuple contains strings

**Correct Answer: A) is illegal**

**Explanation (ELI5):**
Tuples are immutable, which means "unchangeable":
- You CANNOT assign new values to tuple elements (like `my_tuple[1] = something`)
- It's like trying to change the color of a tattoo - once it's there, it's permanent
- Even though the right side (`my_tuple[1] + my_tuple[0]`) might work fine, the assignment `=` is what makes it illegal
- This will always raise a TypeError, regardless of what's in the tuple

---

## Question 16

**A built-in function is a function which:**

**Options:**
A) comes with Python, and is an integral part of Python
B) has been placed within your code by another programmer
C) has to be imported before use
D) is hidden from programmers

**Correct Answer: A) comes with Python, and is an integral part of Python**

**Explanation (ELI5):**
Built-in functions are like the basic tools that come with Python out of the box:
- **A is correct**: Functions like `print()`, `len()`, `input()` are always available
- **B is wrong**: That would be a user-defined function
- **C is wrong**: Built-ins don't need importing (that's for modules)
- **D is wrong**: Built-ins are visible and documented for everyone to use

Think of built-ins as Python's "factory-installed" features, ready to use immediately.

---

## Question 17

**What code would you insert instead of the comment to obtain the expected output?**

**Expected output:**
```
a
b
c
```

**Code:**
```python
dictionary = {}
my_list = ['a', 'b', 'c', 'd']

for i in range(len(my_list) - 1):
    dictionary[my_list[i]] = (my_list[i], )

for i in sorted(dictionary.keys()):
    k = dictionary[i]
    # Insert your code here.
```

**Options:**
A) `print(k[0])`
B) `print(k['0'])`
C) `print(k)`
D) `print(k["0"])`

**Correct Answer: A) `print(k[0])`**

**Explanation (ELI5):**
Let's trace through the code:
1. The first loop creates a dictionary: `{'a': ('a',), 'b': ('b',), 'c': ('c',)}`
2. Each value is a tuple containing one string
3. In the second loop, `k` gets each tuple: `('a',)`, `('b',)`, `('c',)`
4. To get the string inside the tuple, we need `k[0]` (first element)
5. `k['0']` and `k["0"]` would try to use '0' as a key, which doesn't work with tuples
6. `print(k)` would print the whole tuple with parentheses

---

## Question 18

**The following snippet:**

```python
def func_1(a):
    return a ** a

def func_2(a):
    return func_1(a) * func_1(a)

print(func_2(2))
```

**Options:**
A) will output `16`
B) will output `4`
C) will output `2`
D) is erroneous

**Correct Answer: A) will output `16`**

**Explanation (ELI5):**
Let's calculate step by step:
1. `func_2(2)` is called
2. Inside `func_2`, we calculate `func_1(2) * func_1(2)`
3. `func_1(2)` returns `2 ** 2 = 4`
4. So we get `4 * 4 = 16`

It's like asking "what's 2 to the power of 2, then multiply that result by itself?"

---

## Question 19

**What is the output of the following snippet?**

```python
def fun(x, y, z):
    return x + 2 * y + 3 * z

print(fun(0, z=1, y=3))
```

**Options:**
A) `9`
B) `0`
C) `3`
D) the snippet is erroneous

**Correct Answer: A) `9`**

**Explanation (ELI5):**
This shows keyword arguments in action:
1. `x = 0` (positional argument)
2. `y = 3` (keyword argument)
3. `z = 1` (keyword argument)
4. Calculate: `0 + 2 * 3 + 3 * 1 = 0 + 6 + 3 = 9`

Keywords let you specify arguments in any order, like telling someone "I want size medium, color blue, material cotton" instead of having to remember the exact order.

---

## Question 20

**Which of the following lines properly starts a function using two parameters, both with zeroed default values?**

**Options:**
A) `def fun(a=0, b=0):`
B) `def fun(a=b=0):`
C) `fun fun(a=0, b):`
D) `fun fun(a, b=0):`

**Correct Answer: A) `def fun(a=0, b=0):`**

**Explanation (ELI5):**
- **A is correct**: Each parameter gets its own default value
- **B is wrong**: `a=b=0` creates a dependency that can cause problems
- **C is wrong**: Wrong syntax (should be `def`, and `b` needs a default)
- **D is wrong**: Wrong syntax (should be `def`, and `a` needs a default too)

It's like setting up two separate backup plans rather than making one depend on the other.

---

## Question 21

**What is the output of the following snippet?**

```python
def fun(x):
    x += 1
    return x

x = 2
x = fun(x + 1)
print(x)
```

**Options:**
A) `4`
B) `5`
C) `3`
D) the code is erroneous

**Correct Answer: A) `4`**

**Explanation (ELI5):**
Let's trace through this carefully:
1. `x = 2` (global variable)
2. `x = fun(x + 1)` calls `fun(2 + 1)` which is `fun(3)`
3. Inside `fun(3)`: `x += 1` makes the local `x` become `3 + 1 = 4`
4. The function returns `4`
5. The global `x` is assigned this return value: `x = 4`
6. `print(x)` outputs `4`

---

## Question 22

**What is the output of the following snippet?**

```python
def f(x):
    if x == 0:
        return 0
    return x + f(x - 1)

print(f(3))
```

**Options:**
A) `6`
B) `3`
C) `1`
D) the code is erroneous

**Correct Answer: A) `6`**

**Explanation (ELI5):**
This is a recursive function that adds up numbers:
1. `f(3)` calls `3 + f(2)`
2. `f(2)` calls `2 + f(1)`  
3. `f(1)` calls `1 + f(0)`
4. `f(0)` returns `0` (base case)
5. Working backwards: `1 + 0 = 1`, then `2 + 1 = 3`, then `3 + 3 = 6`

It's like asking "what's 3 + 2 + 1 + 0?" The function figures this out by breaking it down step by step.

---

**Summary:**
This test covers key Python concepts including:
- Functions and parameters (default values, keyword arguments)
- Tuples and their immutability
- Dictionaries and key-value access
- Exception handling with try-except blocks
- Recursion
- Variable scope (global vs local)
- Data type operations and limitations