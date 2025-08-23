# # header text
# """
# Some comment in example module
# """

from dataclasses import dataclass
import os

from typing import Union, Optional, Dict, Any, Generator, Tuple

# # Some inline comment

# expression 
a: int = 32

# lambda x: x + 1

# if True:
#     print("This is a conditional statement")
# else:
#     print("This is the else part") 

def example_function(param1: int, param2: str) -> str:
    """
    This is an example function that does nothing.
    
    Args:
        param1 (int): The first parameter.
        param2 (str): The second parameter.
    
    Returns:
        str: A string representation of the parameters.
    """
    a = 9
    b= a +1
    # Another inline comment
    print(f"Parameters are: {param1}, {param2}")
    return f"{param1} and {param2}"

@dataclass
class ExampleDataClass:
    """
    A simple data class example.
    
    Attributes:
        field1 (int): An integer field.
        field2 (str): A string field.
    """
    field1: int
    field2: str
    
    def example_method1(self) -> str:
        """
        A method that returns a string representation of the data class.
        
        Returns:
            str: A string representation of the data class fields.
        """
        return f"DataClass with field1={self.field1} and field2='{self.field2}'"
    
class ExampleClass:
    """
    An example class with a method and a property.
    
    Attributes:
        attribute (int): An integer attribute.
    """
    
    def __init__(self, attribute: int):
        self.attribute = attribute
    
    @property
    def double_attribute(self) -> int:
        """
        A property that returns double the value of the attribute.
        
        Returns:
            int: Double the value of the attribute.
        """
        return self.attribute * 2
    
    def example_method2(self) -> str:
        """
        A method that returns a string representation of the class.
        
        Returns:
            str: A string representation of the class attribute.
        """
        return f"ExampleClass with attribute={self.attribute}"
    
    


with open('blabla.py', 'r') as f:
    f.read()