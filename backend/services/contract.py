import hashlib

class ReverseAuctionContract:
    def __init__(self):

        #khai báo giai đoạn
        self.phase = "COMMIT"
        self.phase = "REVEAL"
        self.phase = "CLOSED"

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
        
        # So sánh hash tự generate với hash được lưu ở phase 1
        rawstring = f"{real_price}-{secret_salt}"
        hash_phase2 = hashlib.sha256(rawstring.encode()).hexdigest()

        hash_phase1 = self.commitments[user_id]

        if hash_phase2 == hash_phase1:
            self.valid_bid[user_id] = real_price
            return {"success": f"Đã xác thực thành công! Giá thực của bạn là {real_price}"}
        else:
            return {"failed": f"Xác thực thất bại: Giá hoặc mã bí mật sai/gian lận"}
    

auction_service = ReverseAuctionContract()