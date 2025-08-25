import bcrypt
from typing import Union
from datetime import datetime, timedelta
import jwt

from config.settings import SECRET_KEY, ALGORITHM


import asyncio

def asyncify(func):
    """Convert synchronous function to asynchronous."""
    async def inner(*args, **kwargs):
        loop = asyncio.get_running_loop()
        func_out = await loop.run_in_executor(None, func, *args, **kwargs)
        return func_out
    return inner

@asyncify
def hash_password(password: str):
    """Hash password using bcrypt and return string for database storage."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

@asyncify
def check_password(password: str, hashed_pass):
    """Check password against hash. Handles both string and bytes formats."""
    if isinstance(hashed_pass, str):
        hashed_pass = hashed_pass.encode('utf-8')
    return bcrypt.checkpw(password.encode('utf-8'), hashed_pass)

def generate_jwt(user_id: int):
    """Generate JWT token for user authentication."""
    payload = {'user_id': user_id}
    token = jwt.encode(payload, str(SECRET_KEY), algorithm=ALGORITHM)
    return token