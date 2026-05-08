import hashlib

class ReverseAuctionContract:
    def __init__(self):

        #khai báo biến giai đoạn
        self.phase = "COMMIT"

        #Khai báo biến lưu
        self.commitments = {} #lưu id và hash
        self.valid_bid = {} #lưu id và giá thực

    # -------- PHASE 1: method nộp thầu --------
    def commit_bid (self, user_id: str, hash_value: str):
        if self.phase != "COMMIT":
            return {"error": "Bạn đang không trong thời gian nộp thầu!"}
        
        if user_id in self.commitments:
            return {"error": "Bạn đã nộp thầu trước đó rồi!"}
        
        self.commitments[user_id] = hash_value
        return {"success": f"Đã ghi nhận hash của {user_id}"}
    
    # -------- PHASE 2: method công bố giá thầu --------
    def reveal_bid (self, user_id: str, real_price: int, secret_salt: str ):
        if self.phase != "REVEAL":
            return {"error": "Bạn đang không trong thời gian tiết lộ!"}
        
        if user_id not in self.commitments:
            return {"error": "Bạn chưa nộp thầu trước đó!"}
        
        if user_id in self.valid_bid:
            return {"error": "Bạn đã tiết lộ giá thầu rồi!"}
        
        # So sánh hash tự generate với hash được lưu ở phase 1
        raw_string = f"{real_price}-{secret_salt}"
        print(f"==== DEBUG: Chuỗi đem đi băm là: {raw_string} ====")
        print(f"==== DEBUG: Hash trong hệ thống đang lưu là {self.commitments[user_id]} ====")

        hash_phase2 = hashlib.sha256(raw_string.encode('utf-8')).hexdigest()
        print(f"==== DEBUG: Hash vừa tự tạo ra là: {hash_phase2} ====")

        hash_phase1 = self.commitments[user_id]

        if hash_phase2 == hash_phase1:
            self.valid_bid[user_id] = real_price
            return {"success": f"Đã xác thực thành công! Giá thực của bạn là {real_price}"}
        else:
            return {"failed": f"Xác thực thất bại: Giá hoặc mã bí mật sai/gian lận"}
        
    # -------- PHASE 3: Công bố người có giá thấp nhất --------
    def get_winner(self) -> dict:
        if self.phase != "CLOSED":
            return {"error": "Cuộc đấu giá chưa kết thúc!"}
        
        if len(self.valid_bid) == 0:
            return {"error": "Không có nhà thầu nào tham gia đấu giá!"}
        
        # Danh sách lưu thứ tự nộp hash tại phase commit, nếu 2 người nộp cùng 1 mức giá thì ai commit trước thì win
        commit_order = list(self.commitments.keys())

        winner = min(
            self.valid_bid.keys(), 
            key = lambda user: (self.valid_bid[user], commit_order.index(user))
        )
        
        lowest_price = self.valid_bid[winner]
        return {"success": f"Đã tìm ra người trúng thầu là Ông/Bà: {winner}, với giá thấp nhất là: {lowest_price}"}
    
    # --------- Method phụ: Đổi phase giành cho vai trò Admin --------
    def change_phase (self, new_phase: str) -> dict:

        valid_phases = ["COMMIT", "REVEAL", "CLOSED"]
        
        if new_phase not in valid_phases:
            return {"error": "Phase không hợp lệ!"}
        
        self.phase = new_phase
        return {"success": f"Hệ hống đấu giá đã chuyển sang giai đoạn {self.phase}"}
    
    # --------- Method phụ: Lấy dữ liệu trả về cho trang Admin --------
    def get_admin_dashboard(self) -> dict:

        dashboard_data_commit = {
            "current_phase": self.phase,
            "total_committed_users": len(self.commitments),
            "committed_users": list(self.commitments.keys()),
            "commitments": self.commitments
        }

        dashboard_data_reveal = {
            "current_phase": self.phase,
            "total_revealed_users": len(self.valid_bid),
            "revealed_users": list(self.valid_bid.keys()),
            "valid_bids": self.valid_bid
        }

        if self.phase == "COMMIT":
            return dashboard_data_commit
        
        if self.phase == "REVEAL":
            return dashboard_data_reveal
        
        if self.phase == "CLOSED":
            dashboard_data_reveal["winner_info"] = self.get_winner()
            return dashboard_data_reveal
        
    # --------- Method phụ: Lấy dữ liệu trả về cho trang User theo id --------
    def get_user_info(self, user_id: str):

        user_info = {
            "user_id": user_id,
            "current_phase": self.phase,
            "has_committed": user_id in self.commitments,
            "has_revealed": user_id in self.valid_bid
        }

        if user_id in self.commitments:
            user_info["committed_hash"] =  self.commitments[user_id]

        if user_id in self.valid_bid:
            user_info["reveal_price"] = self.valid_bid[user_id]

        if self.phase == "CLOSED":
            user_info["winner_info"] = self.get_winner()
        return user_info
    
auction_service = ReverseAuctionContract() # tạo instance của class để router import 