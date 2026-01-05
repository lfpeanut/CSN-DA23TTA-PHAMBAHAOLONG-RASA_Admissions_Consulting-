ct=f"✅ Phương thức: {value}")
            return {"admission_method": value}

        dispatcher.utter_message(text="Anh/chị chưa rõ phương thức này. Em nói rõ hơn giúp anh/chị nhé.\n(VD: thi THPT, học bạ, đánh giá năng lực, tuyển thẳng)")
        return {"admission_method": None}


# ==================== ƯỚC LƯỢNG KHẢ NĂNG TRÚNG TUYỂN ====================
class ActionEstimateEligibility(Action):
    def name(self) -> Text:
        return "action_estimate_eligibility"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        major = tracker.get_slot("major")
        score = tracker.get_slot("score")

        if score is None:
            dispatcher.utter_message(text="Anh/chị chưa có điểm của em nên khó ước lượng chính xác. Em cho anh/chị biết điểm được không?")
            return [SlotSet("is_eligible", None)]

        try:
            score = float(score)
        except (ValueError, TypeError):
            dispatcher.utter_message(text="Anh/chị chưa có điểm hợp lệ của em nên khó ước lượng chính xác.")
            return [SlotSet("is_eligible", None)]

        # Xác định mức độ cạnh tranh theo ngành
        competitive_majors = ["công nghệ thông tin", "cntt", "marketing", "quản trị"]
        is_competitive = False
        
        if major:
            major_lower = major.lower()
            is_competitive = any(m in major_lower for m in competitive_majors)

        # Đánh giá dựa trên điểm
        if score >= 26:
            msg = "🎉 **Xuất sắc!** Với mức điểm này, cơ hội trúng tuyển của em rất cao! Em có thể tự tin vào hầu hết các ngành."
            eligible = True
            confidence = "cao"
        elif 24 <= score < 26:
            msg = "👍 **Tốt!** Điểm của em khá ổn. Cơ hội trúng tuyển tốt, đặc biệt nếu em chọn đúng tổ hợp."
            eligible = True
            confidence = "khá cao"
        elif 22 <= score < 24:
            if is_competitive:
                msg = "⚠️ **Trung bình - Khá:** Điểm em ở mức an toàn cho các ngành ít cạnh tranh. Với ngành này, em nên cân nhắc thêm phương thức xét học bạ."
            else:
                msg = "✅ **Trung bình - Khá:** Điểm em ở mức ổn. Cơ hội trúng tuyển tốt nếu chọn đúng tổ hợp."
            eligible = True
            confidence = "trung bình"
        elif 18 <= score < 22:
            msg = "⚠️ **Cần cân nhắc:** Điểm em hơi thấp cho các ngành hot. Em nên:\n- Chọn các ngành ít cạnh tranh hơn\n- Tận dụng xét học bạ nếu có\n- Theo dõi đợt xét bổ sung"
            eligible = False
            confidence = "thấp"
        else:
            msg = "❗ **Khó khăn:** Điểm em khá thấp. Em nên:\n- Ưu tiên xét học bạ\n- Chọn ngành có điểm chuẩn thấp\n- Cân nhắc các trường khác\n- Đợi xét bổ sung"
            eligible = False
            confidence = "rất thấp"

        # Tạo thông điệp đầy đủ
        full_message = ""
        if major:
            full_message = f"📊 **Đánh giá khả năng trúng tuyển**\n\n"
            full_message += f"🎯 Ngành: {major}\n"
            full_message += f"📝 Điểm: {score}\n"
            full_message += f"📈 Độ tin cậy: {confidence.upper()}\n\n"
            full_message += msg
        else:
            full_message = f"📊 **Đánh giá khả năng trúng tuyển**\n\n"
            full_message += f"📝 Điểm: {score}\n\n"
            full_message += msg

        dispatcher.utter_message(text=full_message)

        return [SlotSet("is_eligible", eligible)]


# ==================== GỢI Ý PHƯƠNG THỨC XÉT TUYỂN ====================
class ActionSuggestAdmissionMethod(Action):
    def name(self) -> Text:
        return "action_suggest_admission_method"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        score = tracker.get_slot("score")
        admission_method = tracker.get_slot("admission_method")
        major = tracker.get_slot("major")

        suggestions = []
        
        message = "💡 **Gợi ý phương thức xét tuyển**\n\n"

        if score is not None:
            try:
                score = float(score)
                
                if score >= 24:
                    suggestions.append("✅ **Xét điểm thi THPT:** Phù hợp nhất với điểm của em. Đây là con đường chính.")
                    suggestions.append("✅ **Xét học bạ:** Đăng ký thêm để tăng cơ hội (nếu học bạ tốt).")
                elif 20 <= score < 24:
                    suggestions.append("✅ **Kết hợp cả 2:** Xét học bạ + điểm thi THPT để tối đa hóa cơ hội.")
                    suggestions.append("✅ **Xét năng lực:** Nếu trường có, em nên thử thêm kỳ thi đánh giá năng lực.")
                elif 18 <= score < 20:
                    suggestions.append("⚠️ **Ưu tiên học bạ:** Nếu học bạ tốt (>= 7.5), đây là con đường an toàn hơn.")
                    suggestions.append("✅ **Điểm thi:** Vẫn nên đăng ký nhưng chọn ngành có điểm chuẩn thấp hơn.")
                    suggestions.append("📌 **Theo dõi xét bổ sung:** Các đợt bổ sung thường có điểm thấp hơn.")
                else:
                    suggestions.append("⚠️ **Xét học bạ:** Con đường chính em nên tập trung.")
                    suggestions.append("📌 **Xét bổ sung:** Đợi các đợt xét bổ sung của các trường.")
                    suggestions.append("💼 **Cân nhắc:** Các trường cao đẳng, trung cấp chất lượng cũng là lựa chọn tốt.")

            except (ValueError, TypeError):
                pass

        # Thêm thông tin về phương thức hiện tại
        if admission_method:
            suggestions.append(f"\n🎯 **Phương thức em chọn:** {admission_method}")
            suggestions.append("💡 Gợi ý: Em có thể đăng ký thêm 1-2 phương thức khác để tăng cơ hội nhé!")

        if suggestions:
            message += "\n".join(suggestions)
        else:
            message = "💡 Anh/chị gợi ý em nên xem kỹ đề án tuyển sinh để chọn phương thức phù hợp:\n\n"
            message += "📌 **Các phương thức phổ biến:**\n"
            message += "1️⃣ Xét điểm thi THPT quốc gia\n"
            message += "2️⃣ Xét học bạ THPT\n"
            message += "3️⃣ Xét kết quả đánh giá năng lực\n"
            message += "4️⃣ Xét tuyển thẳng\n"
            message += "5️⃣ Xét kết hợp"

        dispatcher.utter_message(text=message)

        return []


# ==================== TƯ VẤN CHI TIẾT ====================
class ActionDetailedCounseling(Action):
    def name(self) -> Text:
        return "action_detailed_counseling"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        major = tracker.get_slot("major")
        score = tracker.get_slot("score")
        admission_method = tracker.get_slot("admission_method")

        if not all([major, score]):
            dispatcher.utter_message(text="Em cần cung cấp thêm thông tin để anh/chị tư vấn chi tiết:\n- Ngành em muốn học\n- Điểm xét tuyển")
            return []

        message = f"📋 **BÁO CÁO TƯ VẤN CHI TIẾT**\n\n"
        message += f"👤 **Thông tin của em:**\n"
        message += f"   • Ngành: {major}\n"
        message += f"   • Điểm: {score}\n"
        
        if admission_method:
            message += f"   • Phương thức: {admission_method}\n"
        
        message += f"\n📊 **Phân tích:**\n"
        
        try:
            score_float = float(score)
            
            # Điểm chuẩn tham khảo
            if score_float >= 24:
                message += f"   ✅ Điểm của em cao hơn điểm chuẩn trung bình\n"
                message += f"   ✅ Cơ hội trúng tuyển: Rất tốt (>80%)\n"
            elif score_float >= 20:
                message += f"   ⚠️ Điểm của em ở mức trung bình\n"
                message += f"   ⚠️ Cơ hội trúng tuyển: Khá (50-70%)\n"
            else:
                message += f"   ❌ Điểm của em thấp hơn điểm chuẩn phổ biến\n"
                message += f"   ❌ Cơ hội trúng tuyển: Thấp (<50%)\n"

            message += f"\n🎯 **Khuyến nghị:**\n"
            
            if score_float >= 24:
                message += "   1. Đăng ký xét tuyển sớm\n"
                message += "   2. Chuẩn bị hồ sơ đầy đủ\n"
                message += "   3. Tham gia orientation để làm quen môi trường\n"
            else:
                message += "   1. Đăng ký nhiều phương thức xét tuyển\n"
                message += "   2. Cân nhắc các ngành khác có điểm thấp hơn\n"
                message += "   3. Theo dõi sát các đợt xét bổ sung\n"
                message += "   4. Chuẩn bị phương án dự phòng\n"

            message += f"\n📞 **Liên hệ tư vấn trực tiếp:**\n"
            message += f"   • Hotline: 1900-xxxx\n"
            message += f"   • Email: tuyensinh@university.edu.vn"

        except (ValueError, TypeError):
            message += "   ⚠️ Không thể phân tích do thiếu thông tin điểm"

        dispatcher.utter_message(text=message)
        
        return []


# ==================== RESET TƯ VẤN ====================
class ActionResetCounseling(Action):
    def name(self) -> Text:
        return "action_reset_counseling"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="🔄 Đã reset thông tin tư vấn. Chúng ta bắt đầu lại từ đầu nhé!")
        
        return [
            SlotSet("major", None),
            SlotSet("score", None),
            SlotSet("admission_method", None),
            SlotSet("is_eligible", None),
        ]


# ==================== THỐNG KÊ CÂU HỎI THƯỜNG GẶP ====================
class ActionFAQ(Action):
    def name(self) -> Text:
        return "action_faq"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        faq_message = "❓ **CÂU HỎI THƯỜNG GẶP**\n\n"
        faq_message += "1️⃣ Thủ tục nhập học gồm những gì?\n"
        faq_message += "2️⃣ Học phí bao nhiêu?\n"
        faq_message += "3️⃣ Làm sao để đăng ký ký túc xá?\n"
        faq_message += "4️⃣ Khi nào bắt đầu học?\n"
        faq_message += "5️⃣ Có học bổng cho tân sinh viên không?\n"
        faq_message += "6️⃣ Thẻ sinh viên làm ở đâu?\n"
        faq_message += "7️⃣ Liên hệ ai để được tư vấn?\n\n"
        faq_message += "💬 Em cứ hỏi thoải mái, anh/chị sẽ trả lời chi tiết!"

        dispatcher.utter_message(text=faq_message)
        
ct=f"✅ Phương thức: {value}")
            return {"admission_method": value}

        dispatcher.utter_message(text="Anh/chị chưa rõ phương thức này. Em nói rõ hơn giúp anh/chị nhé.\n(VD: thi THPT, học bạ, đánh giá năng lực, tuyển thẳng)")
        return {"admission_method": None}


# ==================== ƯỚC LƯỢNG KHẢ NĂNG TRÚNG TUYỂN ====================
class ActionEstimateEligibility(Action):
    def name(self) -> Text:
        return "action_estimate_eligibility"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        major = tracker.get_slot("major")
        score = tracker.get_slot("score")

        if score is None:
            dispatcher.utter_message(text="Anh/chị chưa có điểm của em nên khó ước lượng chính xác. Em cho anh/chị biết điểm được không?")
            return [SlotSet("is_eligible", None)]

        try:
            score = float(score)
        except (ValueError, TypeError):
            dispatcher.utter_message(text="Anh/chị chưa có điểm hợp lệ của em nên khó ước lượng chính xác.")
            return [SlotSet("is_eligible", None)]

        # Xác định mức độ cạnh tranh theo ngành
        competitive_majors = ["công nghệ thông tin", "cntt", "marketing", "quản trị"]
        is_competitive = False
        
        if major:
            major_lower = major.lower()
            is_competitive = any(m in major_lower for m in competitive_majors)

        # Đánh giá dựa trên điểm
        if score >= 26:
            msg = "🎉 **Xuất sắc!** Với mức điểm này, cơ hội trúng tuyển của em rất cao! Em có thể tự tin vào hầu hết các ngành."
            eligible = True
            confidence = "cao"
        elif 24 <= score < 26:
            msg = "👍 **Tốt!** Điểm của em khá ổn. Cơ hội trúng tuyển tốt, đặc biệt nếu em chọn đúng tổ hợp."
            eligible = True
            confidence = "khá cao"
        elif 22 <= score < 24:
            if is_competitive:
                msg = "⚠️ **Trung bình - Khá:** Điểm em ở mức an toàn cho các ngành ít cạnh tranh. Với ngành này, em nên cân nhắc thêm phương thức xét học bạ."
            else:
                msg = "✅ **Trung bình - Khá:** Điểm em ở mức ổn. Cơ hội trúng tuyển tốt nếu chọn đúng tổ hợp."
            eligible = True
            confidence = "trung bình"
        elif 18 <= score < 22:
            msg = "⚠️ **Cần cân nhắc:** Điểm em hơi thấp cho các ngành hot. Em nên:\n- Chọn các ngành ít cạnh tranh hơn\n- Tận dụng xét học bạ nếu có\n- Theo dõi đợt xét bổ sung"
            eligible = False
            confidence = "thấp"
        else:
            msg = "❗ **Khó khăn:** Điểm em khá thấp. Em nên:\n- Ưu tiên xét học bạ\n- Chọn ngành có điểm chuẩn thấp\n- Cân nhắc các trường khác\n- Đợi xét bổ sung"
            eligible = False
            confidence = "rất thấp"

        # Tạo thông điệp đầy đủ
        full_message = ""
        if major:
            full_message = f"📊 **Đánh giá khả năng trúng tuyển**\n\n"
            full_message += f"🎯 Ngành: {major}\n"
            full_message += f"📝 Điểm: {score}\n"
            full_message += f"📈 Độ tin cậy: {confidence.upper()}\n\n"
            full_message += msg
        else:
            full_message = f"📊 **Đánh giá khả năng trúng tuyển**\n\n"
            full_message += f"📝 Điểm: {score}\n\n"
            full_message += msg

        dispatcher.utter_message(text=full_message)

        return [SlotSet("is_eligible", eligible)]


# ==================== GỢI Ý PHƯƠNG THỨC XÉT TUYỂN ====================
class ActionSuggestAdmissionMethod(Action):
    def name(self) -> Text:
        return "action_suggest_admission_method"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        score = tracker.get_slot("score")
        admission_method = tracker.get_slot("admission_method")
        major = tracker.get_slot("major")

        suggestions = []
        
        message = "💡 **Gợi ý phương thức xét tuyển**\n\n"

        if score is not None:
            try:
                score = float(score)
                
                if score >= 24:
                    suggestions.append("✅ **Xét điểm thi THPT:** Phù hợp nhất với điểm của em. Đây là con đường chính.")
                    suggestions.append("✅ **Xét học bạ:** Đăng ký thêm để tăng cơ hội (nếu học bạ tốt).")
                elif 20 <= score < 24:
                    suggestions.append("✅ **Kết hợp cả 2:** Xét học bạ + điểm thi THPT để tối đa hóa cơ hội.")
                    suggestions.append("✅ **Xét năng lực:** Nếu trường có, em nên thử thêm kỳ thi đánh giá năng lực.")
                elif 18 <= score < 20:
                    suggestions.append("⚠️ **Ưu tiên học bạ:** Nếu học bạ tốt (>= 7.5), đây là con đường an toàn hơn.")
                    suggestions.append("✅ **Điểm thi:** Vẫn nên đăng ký nhưng chọn ngành có điểm chuẩn thấp hơn.")
                    suggestions.append("📌 **Theo dõi xét bổ sung:** Các đợt bổ sung thường có điểm thấp hơn.")
                else:
                    suggestions.append("⚠️ **Xét học bạ:** Con đường chính em nên tập trung.")
                    suggestions.append("📌 **Xét bổ sung:** Đợi các đợt xét bổ sung của các trường.")
                    suggestions.append("💼 **Cân nhắc:** Các trường cao đẳng, trung cấp chất lượng cũng là lựa chọn tốt.")

            except (ValueError, TypeError):
                pass

        # Thêm thông tin về phương thức hiện tại
        if admission_method:
            suggestions.append(f"\n🎯 **Phương thức em chọn:** {admission_method}")
            suggestions.append("💡 Gợi ý: Em có thể đăng ký thêm 1-2 phương thức khác để tăng cơ hội nhé!")

        if suggestions:
            message += "\n".join(suggestions)
        else:
            message = "💡 Anh/chị gợi ý em nên xem kỹ đề án tuyển sinh để chọn phương thức phù hợp:\n\n"
            message += "📌 **Các phương thức phổ biến:**\n"
            message += "1️⃣ Xét điểm thi THPT quốc gia\n"     dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        major = tracker.get_slot("major")
        score = tracker.get_slot("score")
        admission_method = tracker.get_slot("admission_method")

        if not all([major, score]):
            dispatcher.utter_message(text="Em cần cung cấp thêm thông tin để anh/chị tư vấn chi tiết:\n- Ngành em muốn học\n- Điểm xét tuyển")
            return []

        message = f"📋 **BÁO CÁO TƯ VẤN CHI TIẾT**\n\n"
        message += f"👤 **Thông tin của em:**\n"
        message += f"   • Ngành: {major}\n"
        message += f"   • Điểm: {score}\n"
        
        if admission_method:
            message += f"   • Phương thức: {admission_method}\n"
        
        message += f"\n📊 **Phân tích:**\n"
        
        try:
            score_float = float(score)
            
            # Điểm chuẩn tham khảo
            if score_float >= 24:
                message += f"   ✅ Điểm của em cao hơn điểm chuẩn trung bình\n"
                message += f"   ✅ Cơ hội trúng tuyển: Rất tốt (>80%)\n"
            elif score_float >= 20:
                message += f"   ⚠️ Điểm của em ở mức trung bình\n"
                message += f"   ⚠️ Cơ hội trúng tuyển: Khá (50-70%)\n"
            else:
                message += f"   ❌ Điểm của em thấp hơn điểm chuẩn phổ biến\n"
                message += f"   ❌ Cơ hội trúng tuyển: Thấp (<50%)\n"

            message += f"\n🎯 **Khuyến nghị:**\n"
            
            if score_float >= 24:
                message += "   1. Đăng ký xét tuyển sớm\n"
                message += "   2. Chuẩn bị hồ sơ đầy đủ\n"
                message += "   3. Tham gia orientation để làm quen môi trường\n"
            else:
                message += "   1. Đăng ký nhiều phương thức xét tuyển\n"
                message += "   2. Cân nhắc các ngành khác có điểm thấp hơn\n"
                message += "   3. Theo dõi sát các đợt xét bổ sung\n"
                message += "   4. Chuẩn bị phương án dự phòng\n"

            message += f"\n📞 **Liên hệ tư vấn trực tiếp:**\n"
            message += f"   • Hotline: 1900-xxxx\n"
            message += f"   • Email: tuyensinh@university.edu.vn"

        except (ValueError, TypeError):
            message += "   ⚠️ Không thể phân tích do thiếu thông tin điểm"

        dispatcher.utter_message(text=message)
        
        return []


# ==================== RESET TƯ VẤN ====================
class ActionResetCounseling(Action):
    def name(self) -> Text:
        return "action_reset_counseling"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="🔄 Đã reset thông tin tư vấn. Chúng ta bắt đầu lại từ đầu nhé!")
        
        return [
            SlotSet("major", None),
            SlotSet("score", None),
            SlotSet("admission_method", None),
            SlotSet("is_eligible", None),
        ]


# ==================== THỐNG KÊ CÂU HỎI THƯỜNG GẶP ====================
class ActionFAQ(Action):
    def name(self) -> Text:
        return "action_faq"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        faq_message = "❓ **CÂU HỎI THƯỜNG GẶP**\n\n"
        faq_message += "1️⃣ Thủ tục nhập học gồm những gì?\n"
        faq_message += "2️⃣ Học phí bao nhiêu?\n"
        faq_message += "3️⃣ Làm sao để đăng ký ký túc xá?\n"
        faq_message += "4️⃣ Khi nào bắt đầu học?\n"
        faq_message += "5️⃣ Có học bổng cho tân sinh viên không?\n"
        faq_message += "6️⃣ Thẻ sinh viên làm ở đâu?\n"
        faq_message += "7️⃣ Liên hệ ai để được tư vấn?\n\n"
        faq_message += "💬 Em cứ hỏi thoải mái, anh/chị sẽ trả lời chi tiết!"

        dispatcher.utter_message(text=faq_message)
        
        return []