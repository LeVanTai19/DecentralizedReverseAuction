mock_db = {
    "admin": {"name": "Chủ đầu tư", "password": "123", "role": "admin" },
    "user1": {"name": "Nhà Thầu A", "password": "1", "role": "user"},
    "user2": {"name": "Nhà Thầu B", "password": "2", "role": "user"},
    "user3": {"name": "Nhà Thầu C", "password": "3", "role": "user"},
}

def verify_login(username: str, password: str):
    if username not in mock_db:
        return {"error": "Tài khoản không tồn tại, bạn cần đăng ký!"}
    
    user_info = mock_db["username"]
    if user_info["password"] != password:
        return {"error": "Sai mật khẩu!"}
    
    return {
        "success": "Bạn đã đăng nhập thành công",
        "user_id": username,
        "role": user_info["role"],
        "name": user_info["name"]
    }