import re
import hashlib
import secrets
import string
from typing import Optional, List, Dict, Any
from loguru import logger


def generate_random_string(length: int = 8, include_numbers: bool = True, include_uppercase: bool = True) -> str:
    """Generate a random string of specified length"""
    chars = string.ascii_lowercase
    
    if include_uppercase:
        chars += string.ascii_uppercase
    
    if include_numbers:
        chars += string.digits
    
    return ''.join(secrets.choice(chars) for _ in range(length))


def generate_uuid_hex(length: int = 8) -> str:
    """Generate a UUID-like hex string"""
    return secrets.token_hex(length // 2).upper()


def sanitize_filename(filename: str) -> str:
    """Sanitize filename by removing invalid characters"""
    # Remove invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '', filename)
    
    # Replace spaces with underscores
    sanitized = sanitized.replace(' ', '_')
    
    # Remove consecutive dots
    sanitized = re.sub(r'\.+', '.', sanitized)
    
    # Limit length
    if len(sanitized) > 255:
        name, ext = sanitized.rsplit('.', 1) if '.' in sanitized else (sanitized, '')
        sanitized = name[:255-len(ext)-1] + ('.' + ext if ext else '')
    
    return sanitized


def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone: str) -> bool:
    """Validate phone number format"""
    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', phone)
    
    # Check if it's between 10-15 digits
    return 10 <= len(digits_only) <= 15


def format_phone(phone: str) -> str:
    """Format phone number to standard format"""
    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', phone)
    
    if len(digits_only) == 10:
        # US format: (123) 456-7890
        return f"({digits_only[:3]}) {digits_only[3:6]}-{digits_only[6:]}"
    elif len(digits_only) == 11 and digits_only[0] == '1':
        # US format with country code: +1 (123) 456-7890
        return f"+1 ({digits_only[1:4]}) {digits_only[4:7]}-{digits_only[7:]}"
    else:
        # International format: +XX XXX XXX XXXX
        return f"+{digits_only}"


def hash_string(text: str, algorithm: str = 'sha256') -> str:
    """Hash a string using specified algorithm"""
    if algorithm == 'md5':
        return hashlib.md5(text.encode()).hexdigest()
    elif algorithm == 'sha1':
        return hashlib.sha1(text.encode()).hexdigest()
    elif algorithm == 'sha256':
        return hashlib.sha256(text.encode()).hexdigest()
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")


def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate string to max length with suffix"""
    if len(text) <= max_length:
        return text
    
    truncated_length = max_length - len(suffix)
    return text[:truncated_length] + suffix


def slugify(text: str) -> str:
    """Convert text to URL-friendly slug"""
    # Convert to lowercase
    text = text.lower()
    
    # Replace spaces and special characters with hyphens
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    
    # Remove leading/trailing hyphens
    return text.strip('-')


def extract_numbers(text: str) -> List[float]:
    """Extract all numbers from text"""
    pattern = r'-?\d+\.?\d*'
    matches = re.findall(pattern, text)
    return [float(match) for match in matches]


def mask_email(email: str) -> str:
    """Mask email address for privacy"""
    if '@' not in email:
        return email
    
    username, domain = email.split('@', 1)
    
    if len(username) <= 2:
        masked_username = '*' * len(username)
    else:
        masked_username = username[0] + '*' * (len(username) - 2) + username[-1]
    
    return f"{masked_username}@{domain}"


def mask_phone(phone: str) -> str:
    """Mask phone number for privacy"""
    digits_only = re.sub(r'\D', '', phone)
    
    if len(digits_only) < 4:
        return '*' * len(digits_only)
    
    # Show last 4 digits
    visible_digits = digits_only[-4:]
    masked_digits = '*' * (len(digits_only) - 4)
    
    return masked_digits + visible_digits


def format_currency(amount: float, currency: str = 'USD', locale: str = 'en_US') -> str:
    """Format amount as currency"""
    currency_symbols = {
        'USD': '$',
        'EUR': '€',
        'GBP': '£',
        'JPY': '¥',
        'MXN': '$',
        'BRL': 'R$'
    }
    
    symbol = currency_symbols.get(currency, currency)
    
    # Format with commas for thousands
    formatted = f"{amount:,.2f}"
    
    return f"{symbol}{formatted}"


def camel_to_snake(name: str) -> str:
    """Convert camelCase to snake_case"""
    # Insert underscore before uppercase letters
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def snake_to_camel(name: str) -> str:
    """Convert snake_case to camelCase"""
    components = name.split('_')
    return components[0] + ''.join(word.capitalize() for word in components[1:])


def clean_html(html: str) -> str:
    """Remove HTML tags from string"""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', html)


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"
