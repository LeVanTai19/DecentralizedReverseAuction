import hashlib
from sqlalchemy.orm import Session 
from models import User, Auction, Bid

class ReverseAuctionContract:

    # -------- PHASE 1: method nộp thầu --------
    def commit_bid (self, db: Session, user_id: str, hash_value: str, auction_id: int = 1) -> dict:
        try:
            auction = db.query(Auction).filter(Auction.id == auction_id).first()
            if not auction or auction.phase != "COMMIT":
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
    def get_winner(self, db: Session, auction_id: int = 1) -> dict:
        auction = db.query(Auction).filter(Auction.id == auction_id).first()
        if not auction or auction.phase != "CLOSED":
            return {"error": "Cuộc đấu giá chưa kết thúc!"}
        
        # Lệnh SQL lọc người đã reveal và sắp xếp Giá thấp nhất, nếu giá bằng nhau thì lấy ID nhỏ nhất
        winner_bid = db.query(Bid).filter(
            Bid.auction_id == auction_id,
            Bid.real_price != None,
        ).order_by(Bid.real_price.asc(), Bid.id.asc()).first()

        if not winner_bid:
            return {"error": "Không có nhà thầu nào tham gia đấu giá hợp lệ!"}
        
        return {"success": f"Đã tìm ra người trúng thầu là: {winner_bid.user_id}, với giá thấp nhất là: {winner_bid.real_price}$"}
    
    # --------- Method phụ: Đổi phase giành cho vai trò Admin và tịch thu cọc --------
    def change_phase (self, db: Session, new_phase: str, auction_id: int = 1) -> dict:

        valid_phases = ["COMMIT", "REVEAL", "CLOSED"]
        
        if new_phase not in valid_phases:
            return {"error": "Phase không hợp lệ!"}
        
        auction = db.query(Auction).filter(Auction.id == auction_id).first()
        if not auction:
            return {"error": "Không tìm thấy gói thầu!"}
        
        auction.phase = new_phase

        # Nếu Admin closed, mà nhà thầu nào ko chịu reveal (is_staked == True), thì mất cọc 500$
        if new_phase == "CLOSED":
            slashed_bids = db.query(Bid).filter(
                Bid.auction_id == auction_id,
                Bid.is_staked == True).all()
            
            for bid in slashed_bids:
                bid.is_staked == False

        db.commit()
        return {"success": f"Hệ thống đấu giá đã chuyển sang giai đoạn {new_phase}"}
    
    # --------- Method phụ: Lấy dữ liệu trả về cho trang Admin --------
    def get_admin_dashboard(self, db: Session, auction_id: int = 1) -> dict:
        auction = db.query(Auction).filter(Auction.id == auction_id).first()
        all_bids = db.query(Bid).filter(Auction.id == auction_id).all()

        commitments = {}
        valid_bids = {}
        for b in all_bids:
            commitments[b.user_id] = b.hash_value
            if b.real_price is not None:
                valid_bids[b.user_id] = b.real_price

        dashboard_data_commit = {
            "current_phase": auction.phase,
            "total_committed_users": len(commitments),
            "committed_users": list(commitments.keys()),
            "commitments": commitments
        }

        dashboard_data_reveal = {
            "current_phase": auction.phase,
            "total_revealed_users": len(valid_bids),
            "revealed_users": list(valid_bids.keys()),
            "valid_bids": valid_bids
        }

        if auction.phase == "COMMIT":
            return dashboard_data_commit
        
        if auction.phase == "REVEAL":
            return dashboard_data_reveal
        
        if auction.phase == "CLOSED":
            dashboard_data_reveal["winner_info"] = self.get_winner(db, auction_id)
            return dashboard_data_reveal
        
    # --------- Method phụ: Lấy dữ liệu trả về cho trang User theo id --------
    def get_user_info(self, db: Session, user_id: str, auction_id: int = 1):
        auction = db.query(Auction).filter(Auction.id == auction_id).first()
        user = db.query(User).filter(User.id == user_id).first()
        bid = db.query(Bid).filter(Bid.user_id == user_id, Bid.auction_id == auction_id).first()

        user_info = {
            "user_id": user_id,
            "balance": user.balance if user else 0,
            "current_phase": auction.phase if auction else "COMMIT",
            "has_committed": bid is not None,
            "has_revealed": (bid is not None and bid.real_price is not None)
        }

        if bid:
            user_info["committed_hash"] =  bid.hash_value
            if bid.real_price is not None:
                user_info["reveal_price"] = bid.real_price

        if auction and auction.phase == "CLOSED":
            user_info["winner_info"] = self.get_winner(db, auction_id)
            
        return user_info
    
auction_service = ReverseAuctionContract() # tạo instance của class để router import 