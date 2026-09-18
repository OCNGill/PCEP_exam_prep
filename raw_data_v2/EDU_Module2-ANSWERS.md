# PE1 — Module 2 Test (Extracted)

Below are the extracted questions and their answer choices from the provided JSON. Multi-select questions are marked accordingly.

---

## Q1. The meaning of the keyword parameter is determined by:
- A. the argument's name specified along with its value
- B. its position within the argument list
- C. its connection with existing variables
- D. its value

---

## Q2. What is the output if the user enters 2 and 4?
```python
x = int(input())
y = int(input())

x = x // y
y = y // x

print(y)
```
- A. the code will cause a runtime error
- B. 2.0
- C. 4.0
- D. 8.0

---

## Q3. What is the output of the following snippet?
```python
y = 2 + 3 * 5.
print(Y)
```
- A. the snippet will cause an execution error
- B. 25.
- C. 17
- D. 17.0

---

## Q4. The print() function can output values of:
- A. any number of arguments (including zero)
- B. any number of arguments (excluding zero)
- C. just one argument
- D. not more than five arguments

---

## Q5. Which of the following variable names are illegal? (Select two answers)
- A. True
- B. true
- C. TRUE
- D. and

---

## Q6. What is the output of the following snippet?
```python
z = y = x = 1
print(x, y, z, sep='*')
```
- A. 1*1*1
- B. 1 1 1
- C. x*y*z
- D. x y z

---

## Q7. Which of the following statements are true? (Select two answers)
- A. The result of the / operator is always an integer value.
- B. The right argument of the % operator cannot be zero.
- C. Addition precedes multiplication.
- D. The ** operator uses right-sided binding.

---

## Q8. Left-sided binding determines that the result of the following expression:
`1 // 2 * 3` is equal to:
- A. 0
- B. 4.5
- C. 0.0
- D. 0.16666666666666666

---

## Q9. The ** operator:
- A. performs exponentiation
- B. does not exist
- C. performs floating-point multiplication
- D. performs duplicated multiplication

---

## Q10. What is the output if the user enters 2 and 4?
```python
x = int(input())
y = int(input())

x = x / y
y = y / x

print(y)
```
- A. 8.0
- B. 4.0
- C. 2.0
- D. the code will cause a runtime error

---

## Q11. What is the output if the user enters 2 and 4?
```python
x = int(input())
y = int(input())

print(x + y)
```
- A. 6
- B. 24
- C. 2
- D. 4

---

## Q12. What is the output if the user enters 11 and 4?
```python
x = int(input())
y = int(input())

x = x % y
x = x % y
y = y % x

print(y)
```
- A. 1
- B. 2
- C. 3
- D. 4

---

## Q13. What is the output if the user enters 2 and 4?
```python
x = input()
y = input()
print(x + y)
```
- A. 24
- B. 2
- C. 4
- D. 6

---

## Q14. What is the output of the following snippet?
```python
x = 1
y = 2
z = x
x = y
y = z
print(x, y)
```
- A. 2 1
- B. 1 2
- C. 1 1
- D. 2 2

---

## Q15. What is the output if the user enters 3 and 6?
```python
x = input()
y = int(input())

print(x * y)
```
- A. 333333
- B. 18
- C. 666
- D. 36

---

## Q16. The 0o prefix means that the number after it is denoted as:
- A. octal
- B. binary
- C. decimal
- D. hexadecimal

---

## Q17. The result of the following division:
`1 / 1`
- A. is equal to 1.0
- B. is equal to 1
- C. cannot be evaluated
- D. cannot be predicted
- Q17: A — / gives a float: 1/1 = 1.0.
---

## Q18. The value twenty point twelve times ten raised to the power of eight should be written as:
- A. 20.12E8
- B. 20.12*10^8
- C. 20.12E8.0
- D. 20E12.8

---

## Q19. The \n digraph forces the print() function to:
- A. break the output line
- B. output exactly two characters: \\ and n
- C. duplicate the character next to the digraph
- D. stop its execution

---

## Q20. What is the output of the following snippet?
```python
x = 1 / 2 + 3 // 3 + 4 ** 2
print(x)
```
- A. 17.5
- B. 17
- C. 8
- D. 8.5

---

## Answer key (ELI5)
- Q1: A — Keyword args are matched by name, like labeling a package so it reaches the right place.
- Q2: A — 2//4 = 0; then 4//0 explodes (can’t divide by zero) → runtime error.
- Q3: A — print(Y) uses capital Y, but only y exists; that’s a NameError.
- Q4: A — print can take zero, one, or many things to print.
- Q5: A and D — True and and are reserved; true/TRUE are legal but unconventional.
- Q6: A — sep='*' puts stars between values → 1*1*1.
- Q7: B and D — Mod’s right side can’t be zero; exponent (**) groups from the right.
- Q8: A — 1//2 is 0, and 0*3 = 0.
- Q9: A — ** means “to the power of”.
- Q10: A — 2/4 = 0.5, 4/0.5 = 8.0, so it prints 8.0.
- Q11: A — 2 + 4 = 6.
- Q12: A — 11%4=3; 3%4=3; 4%3=1 → prints 1.
- Q13: A — input gives strings, so "2" + "4" glues into "24".
- Q14: A — Swaps values, ending with 2 1.
- Q15: A — "3" repeated 6 times → 333333.
- Q16: A — 0o is octal (base-8).

- Q18: A — Scientific notation: 20.12E8.
- Q19: A — \n means start a new line.
- Q20: A — 0.5 + 1 + 16 = 17.5.
