class EmotionEngine:
    def __init__(self):
        self.state = {
            "vui": 0.5,
            "buồn": 0.0,
            "giận dữ": 0.0,
            "lo âu": 0.0
        }

    def react_to(self, text: str):
        """
        Phân tích văn bản để tăng/giảm cảm xúc (rất đơn giản)
        """
        if "thành công" in text or "hoàn thành" in text:
            self.state["vui"] += 0.2
        elif "lỗi" in text or "thất bại" in text:
            self.state["buồn"] += 0.2
        elif "không đồng ý" in text or "phản đối" in text:
            self.state["giận dữ"] += 0.2
        elif "lo lắng" in text or "rủi ro" in text:
            self.state["lo âu"] += 0.2

        self._clamp()

    def current_emotion(self) -> str:
        sorted_emotions = sorted(self.state.items(), key=lambda x: -x[1])
        return sorted_emotions[0][0] if sorted_emotions else "bình thường"

    def _clamp(self):
        for key in self.state:
            self.state[key] = max(0.0, min(1.0, self.state[key]))
