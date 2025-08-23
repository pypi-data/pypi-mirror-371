def example_function(param1: int, param2: str):
    """
    This is an example function that does nothing.
    
    Args:
        param1 (int): The first parameter.
        param2 (str): The second parameter.
    
    Returns:
        str: A string representation of the parameters.
    """

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
    def example_method1(self):
        """
        A method that returns a string representation of the data class.
        
        Returns:
            str: A string representation of the data class fields.
        """
    
class ExampleClass:
    """
    An example class with a method and a property.
    
    Attributes:
        attribute (int): An integer attribute.
    """
    def double_attribute(self):
        """
        A property that returns double the value of the attribute.
        
        Returns:
            int: Double the value of the attribute.
        """
    def example_method2(self):
        """
        A method that returns a string representation of the class.
        
        Returns:
            str: A string representation of the class attribute.
        """
    
    