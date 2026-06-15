from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    balance = Column(Float, default=10000.0) # Tạo acc sẽ cho 10.000$
    role = Column(String, default="user")

    # mối quan hệ 1-N (1 user sẽ có nhiều bids)
    bids = relationship("Bid", back_populates="user")

class Auction(Base):
    __tablename__ = "auctions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, index=True)
    phase = Column(String, default="COMMIT")

    # mối quan hệ 1-N
    bids = relationship("Bid", back_populates="auction")

class Bid(Base):
     __tablename__ = "bids"

     id = Column(Integer, primary_key=True, autoincrement=True)

     # FK
     auction_id = Column(Integer, ForeignKey("auctions.id"))
     user_id = Column(String, ForeignKey("users.id"))

     # Lưu trữ dữ liệu đấu giá
     hash_value = Column(String, nullable=True) # sinh ra ở phase Commit
     real_price = Column(Float, nullable=True) # mở ra ở Phase Reveal

     # dùng cho cơ chế đặt cọc, check xem đã giam cọc chưa
     is_staked = Column(Boolean, default=False)

     user = relationship("User", back_populates="bids")
     auction = relationship ("Auction", back_populates="bids")