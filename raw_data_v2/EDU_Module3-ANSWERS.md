# PCEP Module 3 Test - Correct Answers

## Question 1: Boolean Logic

**Question:** What value will be assigned to the `x` variable?

**Code:**
```python
z = 10
y = 0
x = y < z and z > y or y > z and z < y
```

**Analysis:**
- `y < z` → `0 < 10` → `True`
- `z > y` → `10 > 0` → `True`
- `y > z` → `0 > 10` → `False`
- `z < y` → `10 < 0` → `False`
- `True and True or False and False` → `True or False` → `True`

**Correct Answer:** `True`

---

## Question 2: List Manipulation with Insert

**Code:**
```python
my_list = [1, 2, 3]
for v in range(len(my_list)):
    my_list.insert(1, my_list[v])
print(my_list)
```

**Step-by-step execution:**
- Initial: `[1, 2, 3]`, `len(my_list) = 3`
- `v = 0`: `my_list.insert(1, my_list[0])` → `my_list.insert(1, 1)` → `[1, 1, 2, 3]`
- `v = 1`: `my_list.insert(1, my_list[1])` → `my_list.insert(1, 1)` → `[1, 1, 1, 2, 3]`
- `v = 2`: `my_list.insert(1, my_list[2])` → `my_list.insert(1, 1)` → `[1, 1, 1, 1, 2, 3]`

**Correct Answer:** `[1, 1, 1, 1, 2, 3]`

---

## Question 3: List Element Swapping

**Code:**
```python
vals = [0, 1, 2]
vals[0], vals[2] = vals[2], vals[0]
```

**Analysis:**
- Before: `[0, 1, 2]`
- Swaps elements at index 0 and 2
- After: `[2, 1, 0]`
- This reverses the list

**Correct Answer:** reverses the list

---

## Question 4: List Reference vs Copy (Multiple Choice)

**Code:**
```python
nums = [1, 2, 3]
vals = nums
del vals[1:2]
```

**Analysis:**
- `vals = nums` creates a reference, not a copy
- `del vals[1:2]` deletes element at index 1 (value 2)
- Both `nums` and `vals` now reference `[1, 3]` (length 2)

**Correct Answers:** 
- `nums` and `vals` are of the same length
- `nums` and `vals` refer to the same list

---

## Question 5: While Loop with Continue

**Code:**
```python
var = 0
while var < 6:
    var += 1
    if var % 2 == 0:
        continue
    print("#")
```

**Execution:**
- `var = 1`: 1 % 2 = 1 (odd) → prints "#"
- `var = 2`: 2 % 2 = 0 (even) → continue
- `var = 3`: 3 % 2 = 1 (odd) → prints "#"
- `var = 4`: 4 % 2 = 0 (even) → continue
- `var = 5`: 5 % 2 = 1 (odd) → prints "#"
- `var = 6`: exits loop

**Correct Answer:** three

---

## Question 6: List Comprehension Index Error

**Code:**
```python
my_list = [[0, 1, 2, 3] for i in range(2)]
print(my_list[2][0])
```

**Analysis:**
- Creates list: `[[0, 1, 2, 3], [0, 1, 2, 3]]` (2 sublists)
- Tries to access `my_list[2]` but only indices 0 and 1 exist
- IndexError occurs

**Correct Answer:** the snippet will cause a runtime error

---

## Question 7: Negative Indexing and Slicing

**Code:**
```python
my_list = [1, 2, 3, 4]
print(my_list[-3:-2])
```

**Analysis:**
- `my_list = [1, 2, 3, 4]`
- Index -3 = element 2, Index -2 = element 3
- Slice `[-3:-2]` gets elements from index -3 up to (but not including) -2
- Result: `[2]`

**Correct Answer:** `[2]`

---

## Question 8: Bitwise Left Shift in Loop

**Code:**
```python
var = 1
while var < 10:
    print("#")
    var = var << 1
```

**Execution:**
- `var = 1`: prints "#", `var = 1 << 1 = 2`
- `var = 2`: prints "#", `var = 2 << 1 = 4`
- `var = 4`: prints "#", `var = 4 << 1 = 8`
- `var = 8`: prints "#", `var = 8 << 1 = 16`
- `var = 16`: exits loop (16 ≥ 10)

**Correct Answer:** four

---

## Question 9: Bitwise Operations

**Code:**
```python
a = 1
b = 0
c = a & b    # 1 & 0 = 0
d = a | b    # 1 | 0 = 1
e = a ^ b    # 1 ^ 0 = 1

print(c + d + e)  # 0 + 1 + 1 = 2
```

**Correct Answer:** `2`

---

## Question 10: 2D List Comprehension and Diagonal Sum

**Code:**
```python
t = [[3-i for i in range(3)] for j in range(3)]
s = 0
for i in range(3):
    s += t[i][i]
print(s)
```

**Analysis:**
- Inner comprehension: `[3-0, 3-1, 3-2] = [3, 2, 1]`
- Outer creates 3 copies: `[[3, 2, 1], [3, 2, 1], [3, 2, 1]]`
- Diagonal sum: `t[0][0] + t[1][1] + t[2][2] = 3 + 2 + 1 = 6`

**Correct Answer:** `6`

---

## Question 11: For-Else Loop

**Code:**
```python
for i in range(1):
    print("#")
else:
    print("#")
```

**Analysis:**
- Loop executes once (i=0), prints "#"
- Else clause executes after normal loop completion, prints "#"
- Total: 2 hashes

**Correct Answer:** two

---

## Question 12: While Loop with Break

**Code:**
```python
i = 0
while i <= 5:
    i += 1
    if i % 2 == 0:
        break
    print("*")
```

**Execution:**
- `i = 1`: 1 % 2 = 1 (odd), prints "*"
- `i = 2`: 2 % 2 = 0 (even), breaks
- Total: 1 star

**Correct Answer:** one

---

## Question 13: While Loop Counter

**Code:**
```python
i = 0
while i <= 3:
    i += 2
    print("*")
```

**Execution:**
- `i = 2`: prints "*"
- `i = 4`: prints "*"
- `i = 6`: exits loop (6 > 3)
- Total: 2 stars

**Correct Answer:** two

---

## Question 14: Reverse List with Insert

**Code:**
```python
my_list_1 = [1, 2, 3]
my_list_2 = []
for v in my_list_1:
    my_list_2.insert(0, v)
print(my_list_2)
```

**Execution:**
- `v = 1`: `my_list_2 = [1]`
- `v = 2`: `my_list_2 = [2, 1]`
- `v = 3`: `my_list_2 = [3, 2, 1]`

**Correct Answer:** `[3, 2, 1]`

---

## Question 15: Negative Slicing (Multiple Choice)

**Code:**
```python
nums = [1, 2, 3]
vals = nums[-1:-2]
```

**Analysis:**
- `nums[-1:-2]` tries to slice from index -1 to -2
- Since -1 > -2, this creates an empty slice
- `vals = []`, `nums = [1, 2, 3]`

**Correct Answers:**
- `nums` is longer than `vals`
- `nums` and `vals` are two different lists

---

## Question 16: List Operations Sum

**Code:**
```python
vals = [0, 1, 2]
vals.insert(0, 1)  # [1, 0, 1, 2]
del vals[1]        # [1, 1, 2]
```

**Sum:** `1 + 1 + 2 = 4`

**Correct Answer:** `4`

---

## Question 17: Self-Comparison

**Code:**
```python
x = 1
x = x == x  # 1 == 1 is True
```

**Correct Answer:** `True`

---

## Question 18: Range List Comprehension

**Code:**
```python
my_list = [i for i in range(-1, 2)]
```

**Analysis:**
- `range(-1, 2)` generates: -1, 0, 1
- List contains 3 elements

**Correct Answer:** three

---

## Question 19: Equality Operator
**Question:** An operator able to check whether two values are equal is coded as:

**Correct Answer:** `==`

---

## Question 20: Nested Indexing

**Code:**
```python
my_list = [3, 1, -2]
print(my_list[my_list[-1]])
```

**Analysis:**
- `my_list[-1] = -2`
- `my_list[-2] = my_list[1] = 1`

**Correct Answer:** `1`

---

## Summary
- **Total Questions:** 20
- **Single Choice:** 16 questions
- **Multiple Choice:** 4 questions
- **Topics Covered:** Boolean logic, loops, lists, bitwise operations, slicing, comprehensions