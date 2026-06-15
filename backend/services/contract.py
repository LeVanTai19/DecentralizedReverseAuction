import hashlib
from sqlalchemy.orm import Session 
from models import User, Auction, Bid

class ReverseAuctionContract:

    # -------- PHASE 1: method nộp thầu --------
    def commit_bid (self, db: Session, user_id: str, hash_value: str, auction_id: int = 1) -> dict:
        try:
            auction = db.query(Auction).filter(Auction.id == auction_id).first()
            if not auction or auction.phase != "COMMMIT":
                return {"error": "Lỗi: Không trong giai đoạn nộp thầu!"}
            
            user = db.query(User).filter(User.id == user_id).first()

            existing_bid = db.query(Bid).filter(Bid.user_id == user_id, Bid.auction_id == auction_id).first()
            if existing_bid:
                return {"error": "Lỗi: Bạn đã nộp thầu dự án này rồi!"}
            
            # Logic Đặt cọc:
            STAKE_AMOUNT = 500.0
            if user.balance < STAKE_AMOUNT:
                return {"error": f"Lỗi: Số dư của bạn không đủ! Cần {STAKE_AMOUNT}$ để đặt cọc"}
            
            # 1. Trừ tiền cọc
            user.balance -= STAKE_AMOUNT

            # 2. Tạo hồ sơ Bid mới
            new_bid = Bid (
                user_id = user_id,
                auction_id = auction_id,
                hash_value = hash_value,
                is_staked = True
            )
            db.add(new_bid)

            db.commit()
            return {"success": f"Nộp Hash thành công! Hệ thống đã tạm giữ {STAKE_AMOUNT}$ tiền cọc"}

        except Exception as e:
            db.rollback()
            return {"error": f"Lỗi hệ thống: {e}"}
        
    # -------- PHASE 2: method công bố giá thầu --------
    def reveal_bid (self, db: Session, user_id: str, actual_price: float, secret_salt: str, auction_id: int = 1) -> dict:
        try: 
            auction = db.query(Auction).filter(Auction.id == auction_id).first()
            if not auction or auction.phase != "REVEAL":
                return {"error": "Lỗi: Chưa đến thời gian công bố giá thầu!"}
            
            bid = db.query(Bid).filter(Bid.user_id == user_id, Bid.auction_id == auction_id).first()
            if not bid:
                return {"error": "Lỗi: Bạn chưa nộp hồ sơ ẩn ở giai đoạn COMMIT!"}
            
            if bid.real_price is not None:
                return {"error": "Lỗi: Bạn đã công bố giá thành công rồi!"}
            
            # Tái tạo và đối chiếu mã hash
            raw_string = f"{actual_price}-{secret_salt}"
            generated_hash = hashlib.sha256(raw_string.encode('utf-8')).hexdigest()

            if generated_hash == bid.hash_value:
                # 1. Lưu giá thật vào DB
                bid.real_price = actual_price

                # 2. Hoàn trả cọc 
                user = db.query(User).filter(User.id == user_id).first()
                user.balance += 500.0
                bid.is_staked = False

                db.commit()
                return {"success": f"Xác thực thành công! Đã hoàn trả 500$ cọc cho {user_id}."}
            
            else:
                return {"error": "Xác thực THẤT BẠI: Giá thực tế hoặc mã bí mật bị sai!"}

        except Exception as e:
            db.rollback()
            return {"error": f"Lỗi hệ thống: {e}"}

        
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