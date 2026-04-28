# app/ml/prompt_builder.py
from typing import List, Dict


class PromptBuilder:
    @staticmethod
    def tutor_prompt(
        question: str,
        context: str,
        student_level: str = "intermediate",
        teaching_style: str = "supportive"
    ) -> List[Dict[str, str]]:

        system = f"""
You are an expert AI tutor inside an LMS system.

Student level: {student_level}
Teaching style: {teaching_style}

Rules:
- Use the provided context if relevant.
- If context is weak, rely on general knowledge.
- Explain step by step.
- Use simple language for lower levels.
- Always include a short summary at the end.
"""

        user = f"""
Context:
{context}

Question:
{question}
"""

        return [
            {"role": "system", "content": system.strip()},
            {"role": "user", "content": user.strip()}
        ]

    @staticmethod
    def slide_explanation_prompt(
        slide_text: str,
        context: str,
        student_level: str = "intermediate",
        teaching_style: str = "supportive"
    ) -> List[Dict[str, str]]:

        system = f"""
You are an AI lecturer inside a learning platform.

Your job:
- Explain slide content clearly
- Adapt to student level: {student_level}
- Teaching style: {teaching_style}

Return ONLY valid JSON:
{{
  "core_idea": "...",
  "example": "...",
  "summary": "..."
}}
"""

        user = f"""
Slide:
{slide_text}

Context:
{context}
"""

        return [
            {"role": "system", "content": system.strip()},
            {"role": "user", "content": user.strip()}
        ]

    @staticmethod
    def lecture_prompt(topic: str, student_level: str = "intermediate") -> List[Dict[str, str]]:

        system = f"""
You are a real-time AI lecturer in a live classroom.

Rules:
- Teach like a human lecturer
- Use short spoken sentences
- Be interactive
- Adjust difficulty for: {student_level}
- Do NOT output JSON
"""

        user = f"Start teaching this topic: {topic}"

        return [
            {"role": "system", "content": system.strip()},
            {"role": "user", "content": user.strip()}
        ]

    @staticmethod
    def curriculum_prompt(syllabus: str, target_level: str = "intermediate") -> List[Dict[str, str]]:

        system = f"""
You are a curriculum design AI.

Task:
- Convert syllabus into structured learning path
- Adapt for level: {target_level}
- Break into modules, lessons, and outcomes
- Be structured and precise
"""

        return [
            {"role": "system", "content": system.strip()},
            {"role": "user", "content": f"Syllabus:\n{syllabus}"}
        ]