# Import the required libraries
import re

# Define a function to validate an email address
def validate_email(email: str) -> bool:
    """
    Validates an email address using a regular expression.

    Args:
        email (str): The email address to be validated.

    Returns:
        bool: True if the email is valid, False otherwise.
    """
    try:
        # Regular expression for validating an email
        email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        
        # Check if the email matches the regular expression
        if re.match(email_regex, email):
            return True
        else:
            return False
    
    except TypeError as e:
        # Handle TypeError if the input is not a string
        print(f"Error: {e}. Please enter a valid string.")
        return False
    
    except Exception as e:
        # Handle any other exceptions
        print(f"An error occurred: {e}")
        return False

# Define a main function to test the validate_email function
def main():
    # Test the validate_email function
    emails = ["test@example.com", "invalid_email", "test@example", "test.example.com"]
    
    for email in emails:
        print(f"Email: {email}, Valid: {validate_email(email)}")

# Run the main function
if __name__ == "__main__":
    main()