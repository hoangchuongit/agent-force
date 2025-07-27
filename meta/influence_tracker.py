# meta/influence_tracker.py

from collections import defaultdict

class InfluenceTracker:
    def __init__(self):
        # Dạng: { "Duy": 3, "Phuong": 2, ... }
        self.vote_counts = defaultdict(int)
        self.history = []  # Danh sách vòng: [{winner: "Duy", round: 1}, ...]

    def record_vote(self, winner_name: str, round_num: int):
        """Ghi lại một phiếu bầu cho agent thắng vòng đó"""
        if winner_name:
            self.vote_counts[winner_name] += 1
            self.history.append({"winner": winner_name, "round": round_num})

    def get_influence_scores(self):
        """Trả về tổng điểm ảnh hưởng"""
        return dict(self.vote_counts)

    def get_history(self):
        """Trả về lịch sử vote từng vòng"""
        return self.history

    def reset(self):
        """Dọn dẹp cho debate mới"""
        self.vote_counts.clear()
        self.history.clear()
