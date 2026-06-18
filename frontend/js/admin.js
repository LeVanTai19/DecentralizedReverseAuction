//Kiểm tra role
const role = localStorage.getItem('role');
if (role !== 'admin') {
    alert("Cảnh báo: Bạn không có quyền truy cập trang này!");
    window.location.href = 'login.html';
}
document.getElementById('welcomeText').innerText = "Kính chào, " + localStorage.getItem('name');

//Nút đăng xuất
document.getElementById('logoutBtn').addEventListener('click', () => {
    localStorage.removeItem('user_id');
    localStorage.removeItem('role');
    localStorage.removeItem('name');
    
    window.location.href = 'login.html'
})

//Hàm load dữ liệu Dashboard admin
async function loadAdminDashboard() {
    try {
        const res = await fetch('http://127.0.0.1:8000/api/auction/admin/dashboard');
        const data = await res.json();

        const currentPhase = data.current_phase;

        document.getElementById('currentPhaseDisplay').innerText = currentPhase;
        document.getElementById('phaseSelect').value = currentPhase;

        const tableHeader = document.getElementById('tableHeader');
        const tableBody = document.getElementById('tableBody');
        const statText = document.getElementById('statText');
        const winnerBanner = document.getElementById('winnerBanner');

        //reset table khi đổi phase
        tableBody.innerHTML = "";
        winnerBanner.style.display = "none";

        //chia giai đoạn 
        if (currentPhase === "COMMIT") {
            statText.innerText = `Tổng số nhà thầu đã nộp thầu: ${data.total_committed_users}`;
            tableHeader.innerHTML = `<th>Mã nhà thầu</th><th>Mã Hash</th>`;

            //Duyệt qua biến lưu commitments
            for (const[user, hash] of Object.entries(data.commitments)) {
                const tr = document.createElement('tr');
                tr.innerHTML = `<td><strong>${user}</strong></td>
                                <td class="hash-text">${hash}</td>`;
                tableBody.appendChild(tr);
            }
        }

        if (currentPhase === "REVEAL" || currentPhase === "CLOSED") {
            statText.innerText = `Tống số nhà thầu có giá hợp lệ: ${data.total_revealed_users}`;
            tableHeader.innerHTML = `<th>Mã nhà thầu</th><th>Giá thầu thực tế</th>`;

            //Duyệt qua biến lưu valid_bids
            for (const[user, price] of Object.entries(data.valid_bids)) {
                const tr = document.createElement('tr');
                tr.innerHTML = `<td><strong>${user}</strong></td>
                                <td style="color: green; font-weight: bold;">${price}</td>`;
                tableBody.appendChild(tr);
            }

            if (currentPhase === "CLOSED" && data.winner_info) {
                winnerBanner.style.display = "block";

                if (data.winner_info.success) {
                    document.getElementById('winnerText').innerText = data.winner_info.success;
                } else {
                    document.getElementById('winnerText').innerText = "Lỗi: " + data.winner_info.error;
                }

            }
        }


    } catch (error) {
        console.error ("Lỗi lấy dữ liệu:", error);
    }
}

//Xử lý đổi Phase
document.getElementById('changePhaseBtn').addEventListener('click', async () => {
    const newPhase = document.getElementById('phaseSelect').value;
    const msgDiv = document.getElementById('phaseMsg');

    if(!confirm(`Bạn có chắc muốn chuyển hợp đồng sang giai đoạn ${newPhase} không?`))
        return;

    try {
        const res = await fetch('http://127.0.0.1:8000/api/auction/phase', {
            method: "POST",
            headers: {'Content-type': 'application/json'},
            body: JSON.stringify({new_phase: newPhase})
        });

        const result = await res.json();

        if(!res.ok)
            throw new Error(result.detail);
        msgDiv.innerText = "Chuyển gia đoạn thành công!"
        msgDiv.style.color = "green";

        //reset bảng lại
        setTimeout(() => {
            msgDiv.innerText ="";
            loadAdminDashboard();
        }, 1000);


    } catch (error) {
        msgDiv.innerText = error.message;
        msgDiv.style.color = "red";
    }
});

loadAdminDashboard();

