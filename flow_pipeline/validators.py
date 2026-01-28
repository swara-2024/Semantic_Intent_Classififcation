# flow_pipeline/validators.py

import re
import json


class InputValidator:
    """
    Validates user inputs for various data types and formats.
    """
    
    @staticmethod
    def validate_email(email):
        """
        Validates email format.
        
        Args:
            email: Email string to validate
        
        Returns:
            tuple: (is_valid, error_message)
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(pattern, email):
            return True, None
        return False, "Invalid email format. Please enter a valid email address."
    
    @staticmethod
    def validate_phone(phone):
        """
        Validates phone number format (supports common formats).
        
        Args:
            phone: Phone number string
        
        Returns:
            tuple: (is_valid, error_message)
        """
        # Remove common separators
        cleaned = re.sub(r'[\s\-\(\)\+]', '', phone)
        
        # Check if it's 10-15 digits
        if re.match(r'^[\d]{10,15}$', cleaned):
            return True, None
        
        return False, "Invalid phone number. Please enter a valid phone (10-15 digits)."
    
    @staticmethod
    def validate_date(date_str, date_format="%Y-%m-%d"):
        """
        Validates date format.
        
        Args:
            date_str: Date string
            date_format: Expected format (default: YYYY-MM-DD)
        
        Returns:
            tuple: (is_valid, error_message)
        """
        try:
            from datetime import datetime
            datetime.strptime(date_str, date_format)
            return True, None
        except ValueError:
            return False, f"Invalid date format. Please use {date_format}."
    
    @staticmethod
    def validate_time(time_str, time_format="%H:%M"):
        """
        Validates time format.
        
        Args:
            time_str: Time string
            time_format: Expected format (default: HH:MM)
        
        Returns:
            tuple: (is_valid, error_message)
        """
        try:
            from datetime import datetime
            datetime.strptime(time_str, time_format)
            return True, None
        except ValueError:
            return False, f"Invalid time format. Please use {time_format}."
    
    @staticmethod
    def validate_yes_no(response):
        """
        Validates yes/no responses.
        
        Args:
            response: User response string
        
        Returns:
            tuple: (is_valid, normalized_answer)
        """
        response_lower = response.lower().strip()
        
        yes_variations = ['yes', 'y', 'sure', 'ok', 'okay', 'agree', 'affirmative', 'confirmed']
        no_variations = ['no', 'n', 'nope', 'deny', 'negative', 'declined']
        
        if response_lower in yes_variations:
            return True, 'yes'
        elif response_lower in no_variations:
            return True, 'no'
        else:
            return False, None
    
    @staticmethod
    def validate_numeric(value, min_val=None, max_val=None):
        """
        Validates numeric input.
        
        Args:
            value: Input value (string or number)
            min_val: Minimum allowed value (optional)
            max_val: Maximum allowed value (optional)
        
        Returns:
            tuple: (is_valid, numeric_value)
        """
        try:
            num = float(value)
            
            if min_val is not None and num < min_val:
                return False, None
            
            if max_val is not None and num > max_val:
                return False, None
            
            return True, num
        except (ValueError, TypeError):
            return False, None
    
    @staticmethod
    def validate_name(name):
        """
        Validates name format (alphanumeric + spaces, hyphens, apostrophes).
        
        Args:
            name: Name string
        
        Returns:
            tuple: (is_valid, error_message)
        """
        name = name.strip()
        
        if len(name) < 2:
            return False, "Name must be at least 2 characters long."
        
        if len(name) > 100:
            return False, "Name must not exceed 100 characters."
        
        # Allow letters, spaces, hyphens, apostrophes
        if re.match(r"^[a-zA-Z\s\-']+$", name):
            return True, None
        
        return False, "Name contains invalid characters. Please use only letters, spaces, hyphens, and apostrophes."
    
    @staticmethod
    def validate_text_length(text, min_length=1, max_length=1000):
        """
        Validates text length.
        
        Args:
            text: Text to validate
            min_length: Minimum length
            max_length: Maximum length
        
        Returns:
            tuple: (is_valid, error_message)
        """
        text = text.strip()
        length = len(text)
        
        if length < min_length:
            return False, f"Text must be at least {min_length} character(s)."
        
        if length > max_length:
            return False, f"Text must not exceed {max_length} characters."
        
        return True, None
    
    @staticmethod
    def validate_url(url):
        """
        Validates URL format.
        
        Args:
            url: URL string
        
        Returns:
            tuple: (is_valid, error_message)
        """
        pattern = r'^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(/.*)?$'
        if re.match(pattern, url):
            return True, None
        return False, "Invalid URL format. Please enter a valid URL starting with http:// or https://."


class SlotValidator:
    """
    Validates slots for specific flow requirements.
    """
    
    SLOT_VALIDATORS = {
        'email': InputValidator.validate_email,
        'phone': InputValidator.validate_phone,
        'name': InputValidator.validate_name,
        'date': InputValidator.validate_date,
        'time': InputValidator.validate_time,
        'yes_no': InputValidator.validate_yes_no,
    }
    
    @staticmethod
    def validate_slot(slot_name, slot_value, slot_config=None):
        """
        Validates a slot based on its type.
        
        Args:
            slot_name: Name of the slot
            slot_value: Value to validate
            slot_config: Optional configuration dictionary with validation rules
        
        Returns:
            tuple: (is_valid, error_message)
        """
        if slot_config is None:
            slot_config = {}
        
        slot_type = slot_config.get('type') or _infer_slot_type(slot_name)
        
        if slot_type in SlotValidator.SLOT_VALIDATORS:
            validator = SlotValidator.SLOT_VALIDATORS[slot_type]
            return validator(slot_value)
        
        # Default: just check it's not empty
        if slot_value.strip():
            return True, None
        return False, "This field cannot be empty."


def _infer_slot_type(slot_name):
    """
    Infers slot type from its name.
    
    Args:
        slot_name: Name of the slot
    
    Returns:
        str: Inferred type or 'text' as default
    """
    slot_name_lower = slot_name.lower()
    
    if 'email' in slot_name_lower:
        return 'email'
    elif 'phone' in slot_name_lower:
        return 'phone'
    elif 'name' in slot_name_lower:
        return 'name'
    elif 'date' in slot_name_lower:
        return 'date'
    elif 'time' in slot_name_lower:
        return 'time'
    
    return 'text'
