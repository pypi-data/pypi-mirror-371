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
      
 
    
      
        
      
      
        
