from flask import Flask, request, jsonify
from flask_cors import CORS
import requests, os, json, re, time

app = Flask(__name__)

# ✅ Allow CORS for frontend (localhost + production)
CORS(app, resources={r"/*": {"origins": ["*", "http://localhost:3000", "https://eduportal.pro"]}})

# 🔑 Gemini API Key
GEMINI_API_KEY = "AIzaSyCEOfdNy2sIdO-g2vlItsgT9Ncpuu58BaY"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

# 🧠 Build prompt helper
def build_prompt(exam_type, grade, subject, count, lang="en", task="generate", answers=None, student_id=""):
    if task == "generate":
        if lang == "ar":
            return f"""
            أنت خبير في إعداد الاختبارات.
            المهمة: أنشئ {count} أسئلة فريدة ومبتكرة لامتحان {exam_type}.
            الصف: {grade}
            المادة: {subject}

            ✅ القواعد:
            - لا تكرر الأسئلة.
            - يجب أن تحتوي كل سؤال على:
                "id": رقم,
                "difficulty": "سهل" أو "متوسط" أو "صعب",
                "question": "نص السؤال",
                "options": ["أ", "ب", "ج", "د"],
                "correct_answer": "الإجابة الصحيحة"
            - أرجع فقط مصفوفة JSON صحيحة بدون شروحات.
            """
        else:
            return f"""
            You are an expert exam creator.

            Task: Generate {count} unique and creative questions for a {exam_type} exam.
            Grade: {grade}
            Subject: {subject}

            ✅ Rules:
            - No duplicate questions.
            - Each question must include:
                "id": number,
                "difficulty": "Easy" or "Medium" or "Hard",
                "question": "the question text",
                "options": ["A", "B", "C", "D"],
                "correct_answer": "the correct option"
            - Return ONLY a valid JSON array, no explanations.
            """
    else:
        if lang == "ar":
            return f"""
            قم بتقييم إجابات الطالب لامتحان {exam_type}.
            الصف: {grade}
            المادة: {subject}
            معرف الطالب: {student_id}

            إجابات الطالب:
            {answers}

            أرجع JSON بالصيغة التالية:
            {{
              "score": <رقم من 0 إلى 100>,
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

            Student answers:
            {answers}

            Return JSON like:
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

# 🟢 Helper to call Gemini safely
def call_gemini(prompt):
    """Handles Gemini API request with retry and timeout."""
    for attempt in range(2):  # retry twice
        try:
            resp = requests.post(
                GEMINI_URL,
                headers={"Content-Type": "application/json"},
                json={"contents": [{"parts": [{"text": prompt}]}]},
                timeout=70
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"⚠️ Gemini request failed (attempt {attempt+1}): {e}")
            if attempt == 1:
                raise e
            time.sleep(3)  # wait before retry


# 🟢 Generate Questions Endpoint
@app.route("/generate-questions", methods=["POST"])
def generate_questions():
    try:
        data = request.get_json(force=True)
        exam_type = data.get("examType", "TIMSS")
        grade = data.get("grade", "Grade 8")
        subject = data.get("subject", "Math")
        count = data.get("count", 5)
        lang = data.get("lang", "en")

        prompt = build_prompt(exam_type, grade, subject, count, lang=lang, task="generate")

        gemini_data = call_gemini(prompt)
        raw_text = gemini_data["candidates"][0]["content"]["parts"][0]["text"]

        # Try to parse valid JSON array
        try:
            questions = json.loads(raw_text)
        except:
            match = re.search(r"\[.*\]", raw_text, re.S)
            if match:
                questions = json.loads(match.group(0))
            else:
                return jsonify({"error": "Invalid JSON returned from Gemini", "raw": raw_text}), 500

        return jsonify({
            "examType": exam_type,
            "timeLimit": "40 minutes",
            "questions": questions
        }), 200

    except Exception as e:
        print("❌ Error in /generate-questions:", e)
        return jsonify({"error": "Failed to generate questions", "details": str(e)}), 500


# 🟢 Evaluate Endpoint
@app.route("/evaluate", methods=["POST"])
def evaluate():
    try:
        data = request.get_json(force=True)
        exam_type = data.get("examType", "TIMSS")
        grade = data.get("grade", "Grade 8")
        subject = data.get("subject", "Math")
        student_id = data.get("studentId", "test_student")
        answers = data.get("answers", [])
        lang = data.get("lang", "en")

        prompt = build_prompt(exam_type, grade, subject, None, lang=lang, task="evaluate", answers=answers, student_id=student_id)

        gemini_data = call_gemini(prompt)
        raw_text = gemini_data["candidates"][0]["content"]["parts"][0]["text"]

        try:
            feedback_json = json.loads(raw_text)
        except:
            match = re.search(r"\{.*\}", raw_text, re.S)
            if match:
                feedback_json = json.loads(match.group(0))
            else:
                feedback_json = {"score": None, "feedback": raw_text}

        return jsonify(feedback_json), 200

    except Exception as e:
        print("❌ Error in /evaluate:", e)
        return jsonify({"error": "Failed to evaluate answers", "details": str(e)}), 500


# ✅ Health check route
@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "EduPortal Flask API running successfully"}), 200


# ✅ Run locally (Render uses gunicorn)
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
