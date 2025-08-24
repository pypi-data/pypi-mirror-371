def GetUser(email):
    """
    Extracts the username from an email address.
    
    Args:
        email (str): The email address.
        
    Returns:
        str: The username part of the email address.
    """
    if "@" in email:
        return email.split("@")[0]
    else:
        return email


