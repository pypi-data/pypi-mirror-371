def add(a,b):
    """Returns the sum of a and b.  """
    return a + b


def subtract(a,b):
    """Returns the difference of a and b.  """
    return a - b

def multiply(a,b):
    """Returns the product of a and b.  """
    return a * b

def divide(a,b):       
    """Returns the quotient of a and b.  """
    if b == 0:
        raise ValueError("Cannot divide by zero.")
    return a / b
def power(a,b):
    """Returns a raised to the power of b.  """
    return a ** b

