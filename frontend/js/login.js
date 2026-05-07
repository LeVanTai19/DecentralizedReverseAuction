document.getElementById('loginForm').addEventListener('submit', async function (e) {
    e.preventDefault();

    const userVal = document.getElementById('username').value;
    const passVal = document.getElementById('password').value;

    const errorDiv = document.getElementById('errorMessage');
    errorDiv.innerText = "";

    try {

        const response = await fetch('http://127.0.0.1:8000/api/auth/login', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify ({
                username: userVal,
                password: passVal
            })
        });

        const data = await response.json();

        if (!response.ok) {
            errorDiv.innerText = data.detail || "Đăng nhập thất bại!!!";
        } else {
            alert("Đăng nhập thành công với vai trò: " + data.role);

            localStorage.setItem('user_id', data.user_id);
            localStorage.setItem('role', data.role);
            localStorage.setItem('name', data.name);

            if (data.role === 'admin') {
                window.location.href = 'admin.html';
            } else {
                window.location.href = 'user.html'
            }
        }

    } catch {
        console.error ("Lỗi kết nôi:", error);
        errorDiv.innerText = "Không thể kết nối máy chủ. Hãy chắc chắn uvicorn tại BE đang chạy!"
    }
});