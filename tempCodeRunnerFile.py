from flask import Flask, request, jsonify
import requests, os, json, re

app = Flask(__name__)

# 🔑 Gemini API Configuration
GEMINI_API_KEY = "AIzaSyA1tOLp9zmbiBprpuhQZqq7s6TERss4x7s"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"


# 🧠 Helper: Build Prompt
def build_prompt(exam_type, grade, subject, count, lang="en", task="generate", answers=None, student_id=""):
    if task == "generate":
        if lang == "ar":
            return f"""
            أنت خبير في إعداد الاختبارات.
            المهمة: أنشئ {count} أسئلة فريدة ومبتكرة لامتحان {exam_type}.
            الصف: {grade}
            المادة: {subject}
            ✅ القواعد:
            - لا يوجد أسئلة مكررة.
            - يجب أن تكون الأسئلة متنوعة ومناسبة للمستوى.
            - كل سؤال يجب أن يحتوي على:
              "id": رقم,
              "question": "نص السؤال",
              "options": ["أ", "ب", "ج", "د"],
              "correct_answer": "الإجابة الصحيحة"
            - استخدم مستويات صعوبة مختلفة (سهل، متوسط، صعب).
            - أرجع فقط مصفوفة JSON صحيحة بدون أي شروح.
            مثال:
            [
              {{
                "id": 1,
                "difficulty": "سهل",
                "question": "ما نتيجة 2 + 2؟",
                "options": ["3", "4", "5", "6"],
                "correct_answer": "4"
              }},
              {{
                "id": 2,
                "difficulty": "متوسط",
                "question": "حل: 5س - 7 = 18",
                "options": ["س=3", "س=4", "س=5", "س=6"],
                "correct_answer": "س=5"
              }}
            ]
            """
        else:
            # English prompt
            return f"""
            You are an expert exam creator.
            Task: Generate {count} UNIQUE and Creative questions for a {exam_type} exam.
            Grade: {grade}
            Subject: {subject}
            ✅ Rules:
            - No duplicate or repeated questions.
            - Creative and varied concepts for each question.
            - Each question must have:
              "id": number,
              "question": "the question text",
              "options": ["A", "B", "C", "D"],
              "correct_answer": "the correct option"
            - Use **different difficulty levels** (Easy, Medium, Hard).
            - Return ONLY a valid JSON array with no explanations.
            """
    else:
        # Evaluate
        if lang == "ar":
            return f"""
            قم بتقييم إجابات الطالب لامتحان {exam_type}.
            الصف: {grade}
            المادة: {subject}
            معرف الطالب: {student_id}
            إجابات الطالب: {answers}
            أرجع JSON بالصيغة التالية:
            {{
              "score": <رقم من 0-100>,
              "feedback": [
                {{
                  "question": "...",
                  "student_answer": "...",
                  "correct_answer": "...",
                  "comment": "..."
                }}
              ]
            }}
            """
        else:
            return f"""
            Evaluate student's answers for a {exam_type} exam.
            Grade: {grade}
            Subject: {subject}
            Student ID: {student_id}
            Student answers: {answers}
            Output JSON in this format:
            {{
              "score": <number from 0-100>,
              "feedback": [
                {{
                  "question": "...",
                  "student_answer": "...",
                  "correct_answer": "...",
                  "comment": "..."
                }}
              ]
            }}
            """


# 🟢 Generate Questions Endpoint
@app.route("/generate-questions", methods=["POST"])
def generate_questions():
    data = request.get_json()
    exam_type = data.get("examType", "TIMSS")
    grade = data.get("grade", "Grade 8")
    subject = data.get("subject", "Math")
    count = data.get("count", 5)
    lang = data.get("lang", "en")

    prompt = build_prompt(exam_type, grade, subject, count, lang=lang, task="generate")

    try:
        resp = requests.post(
            GEMINI_URL,
            headers={"Content-Type": "application/json"},
            json={"contents": [{"parts": [{"text": prompt}]}]},
        )
        resp.raise_for_status()

        gemini_data = resp.json()
        raw_text = gemini_data["candidates"][0]["content"]["parts"][0]["text"]

        try:
            questions = json.loads(raw_text)
        except:
            match = re.search(r"\[.*\]", raw_text, re.S)
            if match:
                questions = json.loads(match.group(0))
            else:
                return jsonify({"error": "Invalid JSON from Gemini", "raw": raw_text}), 500

        return jsonify({
            "examType": exam_type,
            "timeLimit": "40 minutes",
            "questions": questions
        })

    except Exception as e:
        return jsonify({"error": "Failed to generate questions", "details": str(e)}), 500


# 🟢 Evaluate Answers Endpoint
@app.route("/evaluate", methods=["POST"])
def evaluate():
    data = request.get_json()
    exam_type = data.get("examType", "TIMSS")
    grade = data.get("grade", "Grade 8")
    subject = data.get("subject", "Math")
    student_id = data.get("studentId", "test_student")
    answers = data.get("answers", [])
    lang = data.get("lang", "en")

    prompt = build_prompt(
        exam_type, grade, subject, None,
        lang=lang, task="evaluate",
        answers=answers, student_id=student_id
    )

    try:
        resp = requests.post(
            GEMINI_URL,
            headers={"Content-Type": "application/json"},
            json={"contents": [{"parts": [{"text": prompt}]}]},
        )
        resp.raise_for_status()

        gemini_data = resp.json()
        raw_text = gemini_data["candidates"][0]["content"]["parts"][0]["text"]

        try:
            feedback_json = json.loads(raw_text)
        except:
            match = re.search(r"\{.*\}", raw_text, re.S)
            if match:
                feedback_json = json.loads(match.group(0))
            else:
                feedback_json = {"score": None, "feedback": raw_text}

        return jsonify(feedback_json)

    except Exception as e:
        return jsonify({"error": "Failed to evaluate answers", "details": str(e)}), 500


# 🟢 Run Flask App
if __name__ == "__main__":
    app.run(debug=True, port=5000)