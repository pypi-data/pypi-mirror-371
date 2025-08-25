def fib():
   	# Fibonacci series using loop

  n = int(input("Enter how many terms: "))

  a, b = 0, 1

  print("Fibonacci series:")
  for _ in range(n):
      print(a, end=" ")
      a, b = b, a + b 