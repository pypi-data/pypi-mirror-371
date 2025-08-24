def fact():
# Factorial using loop
  def factorial(n):
      result = 1
      for i in range(1, n + 1):
          result *= i
      return result

# Example with error handling
  try:
      num = int(input("Enter a number: "))
      if num < 0:
          print("Factorial is not defined for negative numbers.")
      else:
          print("Factorial of", num, "is:", factorial(num))
  except ValueError:
      print("Please enter a valid integer.")
      
 
def cal():
    # Calculator using eval

    expression = input("Enter an expression: ")

    try:
        result = eval(expression)
        print("Result:", result)
    except ZeroDivisionError:
        print("Error! Division by zero.")
    except:
        print("Invalid expression.")       
      
        
def fib():
   	# Fibonacci series using loop

  n = int(input("Enter how many terms: "))

  a, b = 0, 1

  print("Fibonacci series:")
  for _ in range(n):
      print(a, end=" ")
      a, b = b, a + b       
      
        
def addoreven():
  n = int(input("Enter a number: "))
  print("Even" if n % 2 == 0 else "Odd")