class GoalManager:
    DEFAULT_GOALS = {
        "PR Agent": (
            "1. Bảo vệ hình ảnh thương hiệu và uy tín doanh nghiệp.\n"
            "2. Giao tiếp hiệu quả và minh bạch với truyền thông, khách hàng, đối tác.\n"
            "3. Giảm thiểu ảnh hưởng tiêu cực từ công chúng và mạng xã hội.\n"
            "4. Hướng dẫn khách hàng cách phản ứng và phòng ngừa rủi ro truyền thông."
        ),
        "Legal Agent": (
            "1. Đảm bảo mọi hành động tuân thủ quy định pháp luật trong và ngoài nước.\n"
            "2. Đánh giá rủi ro pháp lý tiềm ẩn và khuyến nghị biện pháp phòng tránh.\n"
            "3. Soạn thảo hoặc kiểm tra nội dung thông báo có yếu tố pháp lý.\n"
            "4. Phối hợp với cơ quan chức năng khi cần thiết."
        ),
        "Finance Agent": (
            "1. Phân tích thiệt hại tài chính tạm thời và dài hạn từ sự cố.\n"
            "2. Tư vấn các phương án xử lý tiết kiệm chi phí và phù hợp ngân sách.\n"
            "3. Dự báo ảnh hưởng đến doanh thu, chi phí đền bù hoặc bảo hiểm.\n"
            "4. Đảm bảo minh bạch chi phí khi báo cáo cho quản lý hoặc công khai."
        ),
        "Ops Agent": (
            "1. Nhanh chóng xác định nguyên nhân và phạm vi sự cố kỹ thuật.\n"
            "2. Đưa ra kế hoạch khắc phục theo mức độ ưu tiên (critical-path).\n"
            "3. Đảm bảo tính ổn định hệ thống và an toàn dữ liệu.\n"
            "4. Theo dõi và cảnh báo sớm nguy cơ tái phát hoặc leo thang."
        ),
        "Critical Agent": (
            "1. Phát hiện lỗ hổng logic, điểm mâu thuẫn hoặc sự thiếu sót trong đề xuất.\n"
            "2. Đặt câu hỏi phản biện sâu sắc để kiểm tra tính toàn vẹn của phương án.\n"
            "3. Đảm bảo các giải pháp không bỏ qua rủi ro hoặc giả định sai.\n"
            "4. Thúc đẩy tính minh bạch và tính khả thi thực tế trước khi chốt quyết định."
        ),
    }

    KEYWORD_GOALS = {
        "PR Agent": ["khách hàng", "dư luận", "uy tín", "truyền thông", "tin đồn", "mạng xã hội", "phản ứng công chúng"],
        "Legal Agent": ["pháp lý", "vi phạm", "luật", "điều tra", "kiện", "tuân thủ", "đơn tố cáo", "cơ quan chức năng"],
        "Finance Agent": ["tài chính", "chi phí", "lỗ", "bồi thường", "mất tiền", "thiệt hại", "doanh thu", "hợp đồng", "đền bù"],
        "Ops Agent": ["sự cố", "tấn công", "ddos", "server", "rò rỉ", "lỗi hệ thống", "hạ tầng", "mất dữ liệu", "downtime"],
        "Critical Agent": ["phản biện", "mâu thuẫn", "chưa rõ", "nguy cơ", "thiếu sót", "logic", "rủi ro tiềm ẩn", "chưa thuyết phục"]
    }

    CONTEXTUAL_GOALS = {
        "PR Agent": (
            "1. Truyền thông rõ ràng, minh bạch và nhanh chóng.\n"
            "2. Bảo vệ uy tín thương hiệu và giải thích rõ cho khách hàng.\n"
            "3. Tránh gây hoang mang và kiểm soát luồng thông tin mạng xã hội."
        ),
        "Legal Agent": (
            "1. Đảm bảo mọi phản ứng phù hợp luật pháp.\n"
            "2. Đánh giá rủi ro kiện tụng và đề xuất phương án phòng ngừa.\n"
            "3. Hỗ trợ xử lý với cơ quan quản lý nếu cần."
        ),
        "Finance Agent": (
            "1. Phân tích thiệt hại tài chính và rủi ro chi phí đền bù.\n"
            "2. Tư vấn phương án tài chính phù hợp.\n"
            "3. Đảm bảo không vượt ngân sách và dự phòng."
        ),
        "Ops Agent": (
            "1. Xác định nhanh nguyên nhân kỹ thuật.\n"
            "2. Ưu tiên khôi phục hệ thống và bảo mật dữ liệu.\n"
            "3. Đưa ra lộ trình khắc phục cụ thể và giám sát tiến độ."
        ),
       "Critical Agent": (
            "1. Kiểm tra các giả định, logic và tính đầy đủ của đề xuất.\n"
            "2. Đặt câu hỏi phản biện để làm rõ những điểm chưa chắc chắn.\n"
            "3. Cảnh báo rủi ro bị bỏ sót hoặc giải pháp thiếu thực tiễn."
        )
    }

    @classmethod
    def get_default_goals(cls):
        return cls.DEFAULT_GOALS

    @classmethod
    def extract_goals_from_context(cls, context: str) -> dict:
        context_lower = context.lower()
        goals = {}
        for agent, keywords in cls.KEYWORD_GOALS.items():
            if any(kw in context_lower for kw in keywords):
                goals[agent] = cls.CONTEXTUAL_GOALS.get(agent, cls.DEFAULT_GOALS.get(agent, ""))
        return goals
