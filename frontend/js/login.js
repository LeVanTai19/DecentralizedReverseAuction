//========= Hàm Tạo Ví Wallet (Sinh khóa RSA) ===========
document.getElementById('registerForm').addEventListener('submit', function (e) {
    e.preventDefault();
    
    const username = document.getElementById('regUsername').value;
    const msgDiv = document.getElementById('regMessage');
    const btn = document.getElementById('regBtn');

    msgDiv.style.color = "blue";
    msgDiv.innerText = "Đang rèn khóa RSA... Vui lòng đợi...";
    btn.disabled = true;

    // Trình duyệt tự sinh cặp khóa RSA (1024 bit)
    var rsa = forge.pki.rsa;
    rsa.generateKeyPair({bits: 1024, workers: 2}, async function(err, keypair) {
        if (err) {
            msgDiv.innerText = "Lỗi sinh khóa: " + err;
            btn.disabled = false;
            return;
        }

        // Chuyển Key thành định dạng chuỗi PEM để dễ lưu và gửi
        var publicKeyPem = forge.pki.publicKeyToPem(keypair.publicKey);
        var privateKeyPem = forge.pki.privateKeyToPem(keypair.privateKey);

        try {
            // Gửi Username và PUBLIC KEY lên Backend
            const response = await fetch('http://127.0.0.1:8000/api/auth/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    username: username,
                    public_key: publicKeyPem 
                })
            });

            const data = await response.json();

            if (!response.ok) {
                msgDiv.style.color = "red";
                msgDiv.innerText = data.detail;
            } else {
                msgDiv.style.color = "green";
                msgDiv.innerText = "Tạo Ví thành công! Đã cấp 10.000$ vào tài khoản.";
                
                // LƯU PRIVATE KEY VÀO TRÌNH DUYỆT (LocalStorage)
                localStorage.setItem('privateKey_' + username, privateKeyPem); // Gắn tên user vào chìa khóa
                alert("Chú ý: Private Key của bạn đã được lưu an toàn trong trình duyệt này. Hệ thống không lưu giữ nó!");
            }
        } catch (error) {
            msgDiv.style.color = "red";
            msgDiv.innerText = "Không thể kết nối đến Backend.";
        }
        btn.disabled = false;
    });
});

//========= ĐĂNG NHẬP (Lưu Session) ===========
document.getElementById('loginForm').addEventListener('submit', async function (e) {
    e.preventDefault();

    const userVal = document.getElementById('logUsername').value;
    const passVal = document.getElementById('logPassword').value;
    const errorDiv = document.getElementById('logMessage');

    errorDiv.innerText = "";

    try {
        const response = await fetch('http://127.0.0.1:8000/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                username: userVal,
                password: passVal
            })
        });

        const data = await response.json();

        if (!response.ok) {
            errorDiv.innerText = data.detail || "Đăng nhập thất bại!";
        } else {
            // Kiểm tra xem User này có "Private Key + tên user" trong máy không? (Trừ admin)
            if (data.role === 'user' && !localStorage.getItem('privateKey_' + data.user_id)) {
                alert("Cảnh báo: Không tìm thấy Private Key trong trình duyệt này! Bạn sẽ không thể ký giao dịch nộp thầu.");
            }

            localStorage.setItem('user_id', data.user_id);
            localStorage.setItem('role', data.role);
            localStorage.setItem('name', data.name);

            if (data.role === 'admin') {
                window.location.href = 'admin.html';
            } else {
                window.location.href = 'user.html';
            }
        }
    } catch (error) {
        errorDiv.innerText = "Không thể kết nối đến Backend.";
    }
});