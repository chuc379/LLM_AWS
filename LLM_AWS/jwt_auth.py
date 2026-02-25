from fastapi import Header, HTTPException
import jwt

SECRET_KEY = "MY_SUPER_SECRET_KEY_1234567890ABCDEF"

def get_current_user(
    x_user_authorization: str = Header(None, alias="X-User-Authorization")
):
    if not x_user_authorization or not x_user_authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid user token")

    token = x_user_authorization.split(" ", 1)[1]

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        return user_id

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
