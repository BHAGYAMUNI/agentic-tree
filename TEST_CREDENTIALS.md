# Test Credentials 🔐

## Quick Start
Use these credentials to login to Tree AI:

### Primary Test Account
```
Email: demo@example.com
Password: demo123
```

### Alternative Test Accounts
```
Email: test@example.com
Password: test123
```

```
Email: user@example.com
Password: user123
```

---

## If Login Returns 400 Error

**The issue:** The test users might not exist in your database yet.

### Solution 1: Run the Seed Script (Windows PowerShell)
```powershell
cd backend
python seed.py
```

This will:
- Create 3 test users with hashed passwords
- Create a sample tree for demo@example.com
- Display all credentials in console

### Solution 2: Create a New Account
1. Click "Create Account" on the login page
2. Enter any email and password (e.g., test@test.com / testpass123)
3. Click "Create Account"
4. You'll be automatically logged in

### Solution 3: Check Backend Logs
If you still get 400 errors, check your uvicorn terminal for messages like:
- `Login attempt: demo@example.com`
- `User not found`
- `Invalid password`

---

## Default Account from Seed
When you run `seed.py`, these users are created:

| Email | Password | Has Sample Tree |
|-------|----------|-----------------|
| demo@example.com | demo123 | ✅ Yes |
| test@example.com | test123 | ❌ No |
| user@example.com | user123 | ❌ No |

---

## Troubleshooting

### "Email already registered" error
✅ This is GOOD! It means the account exists and you can login.

### "Invalid credentials" error  
- Double-check your email and password spelling
- Make sure you're typing the exact credentials above
- Try creating a new account instead

### 400 Bad Request on login
- Ensure Content-Type header is `application/json`
- Verify email and password fields are in the request body
- Check backend logs for specific error messages

---

## Development Notes

- Passwords are hashed using bcrypt (see `backend/venv/auth.py`)
- Tokens expire after 30 minutes (configurable in auth.py)
- Database: SQLite (`backend/dev.db`)
- To reset: Delete `dev.db` and run `seed.py` again
