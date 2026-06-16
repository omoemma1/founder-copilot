# Since the request is for a TypeScript interface but the code is in Python,
# we will create a Python class with type hints to simulate the interface.

# inter_one.py

"""
This module contains a User class with type hints to simulate a TypeScript interface.
"""

from dataclasses import dataclass
from typing import Optional
import logging
import re

# Configure the logging module
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
        if not validate_email(email):
            raise ValueError("invalid email address")
        if age is not None and age < 0:
            raise ValueError("age must be a non-negative integer")
        
        # Create and return the User object
        return User(id, name, email, age)
    except (TypeError, ValueError) as e:
        # Handle any errors that occur during user creation
        logging.error(f"Error creating user: {e}")
        return None

def validate_email(email: str) -> bool:
    """
    Validates an email address.
    
    Args:
        email (str): The email address to validate.
    
    Returns:
        bool: True if the email address is valid, False otherwise.
    """
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(pattern, email))

def main():
    # Example usage:
    user = create_user(1, "John Doe", "john@example.com", 30)
    if user:
        logging.info(user)

if __name__ == "__main__":
    main()
# Test case 1: Valid input
user = create_user(1, "John Doe", "john@example.com", 30)
if user:
    logging.info(user)

# Test case 2: Invalid email address
user = create_user(1, "John Doe", "invalid_email", 30)
if user is None:
    logging.info("User creation failed")

# Test case 3: Negative age
user = create_user(1, "John Doe", "john@example.com", -30)
if user is None:
    logging.info("User creation failed")

# Test case 4: Empty name
user = create_user(1, "", "john@example.com", 30)
if user is None:
    logging.info("User creation failed")