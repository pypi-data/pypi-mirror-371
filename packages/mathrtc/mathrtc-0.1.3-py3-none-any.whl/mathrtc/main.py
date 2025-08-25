def fact():
	try:
    	num = int(input("Enter a number: "))

  	  if num < 0:
        	print("Error: Factorial is not defined for negative numbers.")
    	else:
     	   fact = 1
       	 for i in range(1, num + 1):
            	fact *= i
       	 print("Factorial:", fact)

	except ValueError:
	    print("Error: Please enter a valid integer.")