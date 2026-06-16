# Since the request is for a TypeScript interface but the code is in Python,
# we will create a Python class with type hints to simulate the interface.

# inter_one.py

"""
This module contains a User class with type hints to simulate a TypeScript interface.
"""

from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    """
    A class representing a User object.
    
    Attributes:
        id (int): The unique identifier of the user.
        name (str): The name of the user.
        email (str): The email address of the user.
        age (Optional[int]): The age of the user (optional).
    """
    id: int
    name: str
    email: str
    age: Optional[int] = None

def create_user(id: int, name: str, email: str, age: Optional[int] = None) -> User:
    """
    Creates a new User object.
    
    Args:
        id (int): The unique identifier of the user.
        name (str): The name of the user.
        email (str): The email address of the user.
        age (Optional[int]): The age of the user (optional).
    
    Returns:
        User: The created User object.
    
    Raises:
        TypeError: If the input types are incorrect.
        ValueError: If the input values are invalid.
    """
    try:
        # Check if the input types are correct
        if not isinstance(id, int):
            raise TypeError("id must be an integer")
        if not isinstance(name, str):
            raise TypeError("name must be a string")
        if not isinstance(email, str):
            raise TypeError("email must be a string")
        if age is not None and not isinstance(age, int):
            raise TypeError("age must be an integer or None")
        
        # Check if the input values are valid
        if id <= 0:
            raise ValueError("id must be a positive integer")
        if not name:
            raise ValueError("name cannot be empty")
        if not email:
            raise ValueError("email cannot be empty")
        
        # Create and return the User object
        return User(id, name, email, age)
    except (TypeError, ValueError) as e:
        # Handle any errors that occur during user creation
        print(f"Error creating user: {e}")
        return None

def main():
    # Example usage:
    user = create_user(1, "John Doe", "john@example.com", 30)
    if user:
        print(user)

if __name__ == "__main__":
    main()