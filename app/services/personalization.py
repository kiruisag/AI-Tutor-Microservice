class PersonalizationEngine:
    def adjust_difficulty(self, student_performance: float) -> str:
        if student_performance < 0.4: return "beginner"
        if student_performance < 0.7: return "intermediate"
        return "advanced"

    def get_teaching_style(self, engagement_metrics: dict) -> str:
        # simplistic: if clicks per minute high, use "fast-paced"
        return "supportive"  # default