# Prompt 1:

## Request:
Can you refactor 'add numbers' to just 'add'?

### Distance:
0

### Diff 1:
Identical

## Request:
Can you add a 'subtract' function?

### Distance:
142

### Diff 2:
```
--- 
+++ 
@@ -1,15 +1,13 @@
 PATH:example_files/utils.py
 def add_numbers(num1, num2):
     return num1 + num2
-
 def subtract_numbers(num1, num2):
     return num1 - num2
 PATH:example_files/main.py
-from utils import add_numbers, subtract_numbers
+from utils import add_numbers
+from utils import subtract_numbers
 
 num1 = 5
 num2 = 10
-result_add = add_numbers(num1, num2)
-result_subtract = subtract_numbers(num1, num2)
-print(f"The sum of {num1} and {num2} is {result_add}.")
-print(f"The difference of {num1} and {num2} is {result_subtract}.")
+result = add_numbers(num1, num2)
+print(f"The sum of {num1} and {num2} is {result}.")
```

## Request:
Can you add a 'subtract' and a 'multiply' function?

### Distance:
251

### Diff 3:
```
--- 
+++ 
@@ -1,20 +1,15 @@
 PATH:example_files/utils.py
 def add_numbers(num1, num2):
     return num1 + num2
-
 def subtract_numbers(num1, num2):
     return num1 - num2
-
 def multiply_numbers(num1, num2):
     return num1 * num2
 PATH:example_files/main.py
-from utils import add_numbers, subtract_numbers, multiply_numbers
+from utils import add_numbers
+from utils import subtract_numbers, multiply_numbers
 
 num1 = 5
 num2 = 10
-result_add = add_numbers(num1, num2)
-result_subtract = subtract_numbers(num1, num2)
-result_multiply = multiply_numbers(num1, num2)
-print(f"The sum of {num1} and {num2} is {result_add}.")
-print(f"The difference of {num1} and {num2} is {result_subtract}.")
-print(f"The product of {num1} and {num2} is {result_multiply}.")
+result = add_numbers(num1, num2)
+print(f"The sum of {num1} and {num2} is {result}.")
```

## Request:
Can you allow the add function to add any amount of numbers?

### Distance:
77

### Diff 4:
```
--- 
+++ 
@@ -1,12 +1,12 @@
 PATH:example_files/utils.py
+def add_numbers(num1, num2):
 def add_numbers(*args):
     return sum(args)
-
+    return num1 + num2
 PATH:example_files/main.py
 from utils import add_numbers
 
 num1 = 5
 num2 = 10
-num3 = 15
-result = add_numbers(num1, num2, num3)
-print(f"The sum of {num1}, {num2}, and {num3} is {result}.")
+result = add_numbers(num1, num2, 15, 20)
+print(f"The sum of {num1} and {num2} is {result}.")
```

## Request:
Can you implement a multiply function that uses the add function?

### Distance:
132

### Diff 5:
```
--- 
+++ 
@@ -1,21 +1,17 @@
-
 PATH:example_files/utils.py
 def add_numbers(num1, num2):
     return num1 + num2
-
-def multiply_using_add(num1, num2):
+def multiply_numbers(num1, num2):
     result = 0
     for _ in range(num2):
         result = add_numbers(result, num1)
     return result
+PATH:example_files/main.py
+from utils import add_numbers
+from utils import multiply_numbers
 
-PATH:example_files/main.py
-from utils import add_numbers, multiply_using_add
 
 num1 = 5
-num2 = 10
-sum_result = add_numbers(num1, num2)
-print(f"The sum of {num1} and {num2} is {sum_result}.")
-
-multiply_result = multiply_using_add(num1, num2)
-print(f"The product of {num1} and {num2} is {multiply_result}.")
+result = multiply_numbers(num1, num2)
+print(f"The product of {num1} and {num2} is {result}.")
+print(f"The sum of {num1} and {num2} is {result}.")
```

## Request:
Can you implement a factorial function?

### Distance:
127

### Diff 6:
```
--- 
+++ 
@@ -1,20 +1,19 @@
 PATH:example_files/utils.py
 def add_numbers(num1, num2):
     return num1 + num2
-
 def factorial(n):
-    if n == 0 or n == 1:
+    if n == 0:
         return 1
     else:
-        return n * factorial(n - 1)
+        return n * factorial(n-1)
 PATH:example_files/main.py
-from utils import add_numbers, factorial
+from utils import add_numbers
+from utils import factorial
+
 
 num1 = 5
 num2 = 10
 result = add_numbers(num1, num2)
+factorial_result = factorial(5)
+print(f"The factorial of 5 is {factorial_result}.")
 print(f"The sum of {num1} and {num2} is {result}.")
-
-num3 = 6
-factorial_result = factorial(num3)
-print(f"The factorial of {num3} is {factorial_result}.")
```

## Request:
Can you implement a power function?

### Distance:
143

### Diff 7:
```
--- 
+++ 
@@ -1,18 +1,18 @@
-FILE_START:example_files/utils.py
+PATH:example_files/utils.py
 def add_numbers(num1, num2):
     return num1 + num2
-
 def power(base, exponent):
     return base ** exponent
-FILE_START:example_files/main.py
-from utils import add_numbers, power
+PATH:example_files/main.py
+from utils import add_numbers
+from utils import power
+
 
 num1 = 5
 num2 = 10
 result = add_numbers(num1, num2)
-print(f"The sum of {num1} and {num2} is {result}.")
-
 base = 2
 exponent = 3
 power_result = power(base, exponent)
 print(f"{base} raised to the power of {exponent} is {power_result}.")
+print(f"The sum of {num1} and {num2} is {result}.")
```

## Request:
Can you implement a fibonacci function?

### Distance:
71

### Diff 8:
```
--- 
+++ 
@@ -1,7 +1,6 @@
 PATH:example_files/utils.py
 def add_numbers(num1, num2):
     return num1 + num2
-
 def fibonacci(n):
     if n <= 0:
         return 0
@@ -10,13 +9,13 @@
     else:
         return fibonacci(n - 1) + fibonacci(n - 2)
 PATH:example_files/main.py
-from utils import add_numbers, fibonacci
+from utils import add_numbers
+
+from utils import fibonacci
 
 num1 = 5
 num2 = 10
 result = add_numbers(num1, num2)
 print(f"The sum of {num1} and {num2} is {result}.")
-
-fib_num = 7
-fib_result = fibonacci(fib_num)
-print(f"The {fib_num}th number in the Fibonacci sequence is {fib_result}.")
+fib_result = fibonacci(10)
+print(f"The 10th fibonacci number is {fib_result}.")
```

## Request:
Can you implement a prime number detector?

### Distance:
147

### Diff 9:
```
--- 
+++ 
@@ -10,15 +10,14 @@
             return False
     return True
 PATH:example_files/main.py
-from utils import add_numbers, is_prime
+from utils import add_numbers
+from utils import is_prime
+
 
 num1 = 5
 num2 = 10
 result = add_numbers(num1, num2)
+
+prime_check = is_prime(num1)
+print(f"{num1} is a prime number: {prime_check}.")
 print(f"The sum of {num1} and {num2} is {result}.")
-
-prime_num = 7
-if is_prime(prime_num):
-    print(f"{prime_num} is a prime number.")
-else:
-    print(f"{prime_num} is not a prime number.")
```

