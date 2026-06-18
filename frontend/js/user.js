//Kiểm tra đăng nhập
const userId = localStorage.getItem('user_id');
const role = localStorage.getItem('role');

if (!userId || role !== 'user') {
    alert ("Vui lòng đăng nhập với tài khoản nhà thầu");
    window.location.href = 'login.html';
}

//Xử lý header 
document.getElementById('welcomeText').innerText = "Kính chào, " + localStorage.getItem('name');
document.getElementById('logoutBtn').addEventListener('click', () => {
    localStorage.removeItem('user_id');
    localStorage.removeItem('role');
    localStorage.removeItem('name');
    
    window.location.href = 'login.html'
});

//Biến lưu trạng thái
let currentAuctionId = 1;
let currentPhase = "";

// Hàm lấy Danh Sách Dự Án
async function loadAuctions() {
    const res = await fetch('http://127.0.0.1:8000/api/auction/all');
    const auctions = await res.json();
    const select = document.getElementById('auctionSelect');

    // Tạo các options cho danh sách dropdown 
    auctions.forEach(a => {
        const option = document.createElement('option');
        option.value = a.id;
        option.text = `[ID: ${a.id}] ${a.title} - Trạng thái: ${a.phase}`;
        select.appendChild(option);
    });

    if (auctions.length > 0) {
        currentAuctionId = select.value;
        loadDashboard();
    }
}

// Xử lý Dropdown
document.getElementById('auctionSelect').addEventListener('change', function() {
    currentAuctionId = this.value;
    loadDashboard(); // Load lại thông tin user cho dự án mới
});

//Xử lý bảng trạng thái 
async function loadDashboard() {
    try {
        const res = await fetch(`http://127.0.0.1:8000/api/auction/user/${userId}/dashboard?auction_id=${currentAuctionId}`);
        const data = await res.json();

        document.getElementById('balanceDisplay').innerText = data.balance; // MỚI: Hiện số dư

        currentPhase = data.current_phase
        document.getElementById('phaseStatus').innerText = data.current_phase;

        const actionArea = document.getElementById('actionArea');
        const submitBtn = document.getElementById('submitBtn');
        const formTitle = document.getElementById('formTitle');
        const myStatus = document.getElementById('myStatus');
        const hashDisplay = document.getElementById('hashDisplay');

        if (data.current_phase === "COMMIT") {
            if (data.has_committed) {
                actionArea.style.display = "none"; // Ẩn form đi
                myStatus.innerText = "Đã nộp mã thành công. Đang chờ mở giá";
                myStatus.style.color = "green";
                hashDisplay.style.display = "block";
                hashDisplay.innerText = "Mã hash của bạn: " + data.committed_hash;
            } else {
                actionArea.style.display = "block";
                formTitle.innerText = "Nộp Giá Thầu (Sẽ được băm ẩn)";
                submitBtn.innerText = "Băm Hash & Nộp thầu";
                myStatus.innerText = "Chưa nộp thầu";
            }
        }
        else if (data.current_phase === "REVEAL") {
            if (!data.has_committed) {
                actionArea.style.display = "none";
                myStatus.innerText = "Bạn đã bỏ lỡ thời gian nộp thầu!";
                myStatus.style.color = "red";
            } else if (data.has_revealed) {
                actionArea.style.display = "none";
                myStatus.innerText = `Đã công bố giá thành công: ${data.reveal_price}$`;
                myStatus.style.color = "green";
            } else {
                actionArea.style.display = "block";
                formTitle.innerText = "Công bố giá thật (Reveal)";
                submitBtn.innerText = "Gửi giá để đối chiếu Hash";
                submitBtn.style.background = "#28a745"; 
                myStatus.innerText = "Đến giờ công bố giá!";
            }
        } 
        else if (data.current_phase === "CLOSED") {
            actionArea.style.display = "none";
            const winnerInfo = data.winner_info; 

            if (winnerInfo && winnerInfo.success) {
                const winnerMessage = winnerInfo.success; 
                    
                // KIỂM TRA LOGIC: Tên user đang đăng nhập có nằm trong câu thông báo kia 
                if (winnerMessage.includes(userId)) {
                    myStatus.innerHTML = `CHÚC MỪNG! BẠN LÀ NGƯỜI TRÚNG THẦU! <br> <small>${winnerMessage}</small>`;
                    myStatus.style.color = "#d63384";
                } else {
                    myStatus.innerHTML = `Phiên đấu giá đã kết thúc. Bạn không trúng thầu. <br> <small>${winnerMessage}</small>`;
                    myStatus.style.color = "gray";
                }
            } else {
                // Trường hợp không ai nộp thầu hợp lệ
                myStatus.innerText = "Phiên đấu giá đã kết thúc nhưng không có người thắng hợp lệ.";
                myStatus.style.color = "red";
            }
        }

    } catch (error) {
        console.error("lỗi", error);
    }
}

// Xử lý Nộp Thầu và Mở Giá
document.getElementById('bidForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const price = document.getElementById('bidPrice').value;
    const secret = document.getElementById('secretSalt').value;
    const msgDiv = document.getElementById('message');

    // lấy Private key từ trình duyệt
    const privateKeyPem = localStorage.getItem('privateKey_' + userId);
    if (!privateKeyPem) {
        msgDiv.innerText = "Lỗi: Trình duyệt không chứa Private Key của bạn. Bạn không thể Ký giao dịch!";
        msgDiv.style.color = "red";
        return;
    }
    const privateKey = forge.pki.privateKeyFromPem(privateKeyPem);
    const auctionId = 1;

    //Nếu ở phase commit thì userid và nộp hash về BE
    if (currentPhase === "COMMIT") {
    
        const rawString = `${price}-${secret}`;
        const hashValue = CryptoJS.SHA256(rawString).toString();
        
        console.log("Chuỗi gốc:", rawString);
        console.log("Hash tạo ra:", hashValue);

        // Tạo message web3: ký điện tử ở FE để gửi về BE check
        const messageToSign = `COMMIT-${currentAuctionId}-${hashValue}`;
        const md = forge.md.sha256.create();
        md.update(messageToSign,'utf8');
        const signatureBytes = privateKey.sign(md);
        const signatureBase64 = forge.util.encode64(signatureBytes); // Mã hóa ra Base64 để gửi qua mạng


        try {
            const res = await fetch('http://127.0.0.1:8000/api/auction/commit', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ auction_id: parseInt(currentAuctionId), user_id: userId, hash_value: hashValue, signature: signatureBase64 })
            });
            const result = await res.json();
            
            if (!res.ok) 
                throw new Error(result.detail);
            
            msgDiv.innerText = result.success;
            msgDiv.style.color = "green";
            setTimeout(() => location.reload(), 1500); // F5 lại trang để cập nhật UI
            
        } catch (error) {
            msgDiv.innerText = error.message;
            msgDiv.style.color = "red";
        }
    } 

    //Nếu ở phase reveal thì nộp userid và giá + salt về BE
    else if (currentPhase === "REVEAL") {
        
        // Tạo message web3: ký điện tử ở FE để gửi về BE check
        const messageToSign = `REVEAL-${currentAuctionId}-${price}-${secret}`;
        const md = forge.md.sha256.create();
        md.update(messageToSign,'utf8');
        const signatureBytes = privateKey.sign(md);
        const signatureBase64 = forge.util.encode64(signatureBytes);

        try {
            const res = await fetch('http://127.0.0.1:8000/api/auction/reveal', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ auction_id: parseInt(currentAuctionId), user_id: userId, real_price: Number(price), secret_salt: secret, signature: signatureBase64 })
            });
            const result = await res.json();
            
            if (!res.ok) 
                throw new Error(result.detail);
            
            msgDiv.innerText = result.success;
            msgDiv.style.color = "green";
            setTimeout(() => location.reload(), 1500);
            
        } catch (error) {
            msgDiv.innerText = error.message;
            msgDiv.style.color = "red";
        }
    }
});

loadAuctions();