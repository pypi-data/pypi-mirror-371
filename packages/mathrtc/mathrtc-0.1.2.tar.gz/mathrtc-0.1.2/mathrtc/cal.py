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