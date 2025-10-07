from flask import Flask, request, jsonify
from flask_cors import CORS
import requests, os, json, re, time, concurrent.futures

app = Flask(__name__)

# ✅ Allow CORS for frontend (localhost + production)
CORS(app, resources={r"/*": {"origins": ["*", "http://localhost:3000", "https://eduportal.pro"]}})

# 🔑 Gemini API Key (keep secure in env on production)
GEMINI_API_KEY = "AIzaSyA6VyEO3weAJLVm39d_GmmSlzkn8NvTuZw"
# ⚡ Gemini 2.0 Flash is fast and handles large JSON output better
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

# ⚙️ Thread pool for parallel requests
executor = concurrent.futures.ThreadPoolExecutor(max_workers=6)

# 🧠 Build prompt helper (simplified for speed)
def build_prompt(exam_type, grade, subject, count, lang="en", task="generate", answers=None, student_id=""):
    if task == "generate":
        if lang == "ar":
            return f"""
            أنت خبير في إعداد الاختبارات.
            أنشئ {count} أسئلة متعددة الخيارات لامتحان {exam_type}.
            الصف: {grade}
            المادة: {subject}

            كل سؤال بصيغة JSON يتضمن:
            {{
                "id": رقم,
                "question": "النص",
                "options": ["أ", "ب", "ج", "د"],
                "correct_answer": "الإجابة الصحيحة"
            }}
            أرجع مصفوفة JSON فقط بدون شرح.
            """
        else:
            return f"""
            You are an expert exam creator. Create {count} concise multiple-choice questions 
            for a {exam_type} exam in grade {grade} ({subject}). 
            Return ONLY valid JSON like:
            [
              {{
                "id": 1,
                "question": "Sample question?",
                "options": ["A", "B", "C", "D"],
                "correct_answer": "A"
              }}
            ]
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

            أرجع JSON مثل:
            {{
              "score": <رقم>,
              "feedback": [{{"question": "...", "student_answer": "...", "correct_answer": "...", "comment": "..."}}]
            }}
            """
        else:
            return f"""
            Evaluate the student's answers for a {exam_type} exam ({subject}, grade {grade}).
            Student ID: {student_id}
            Answers:
            {answers}

            Return JSON like:
            {{
              "score": <number>,
              "feedback": [{{"question": "...", "student_answer": "...", "correct_answer": "...", "comment": "..."}}]
            }}
            """

# ⚡ Fast Gemini caller
def call_gemini(prompt):
    try:
        resp = requests.post(
            GEMINI_URL,
            headers={"Content-Type": "application/json"},
            json={"contents": [{"parts": [{"text": prompt}]}]},
            timeout=200
        )
        resp.raise_for_status()
        data = resp.json()
        raw_text = data["candidates"][0]["content"]["parts"][0]["text"]

        # Try parsing clean JSON
        try:
            return json.loads(raw_text)
        except:
            match = re.search(r"\[.*\]", raw_text, re.S)
            if match:
                return json.loads(match.group(0))
            raise ValueError("Invalid JSON output")

    except Exception as e:
        print(f" Gemini error: {e}")
        return []

# 🟢 Parallelized generate-questions endpoint
@app.route("/generate-questions", methods=["POST"])
def generate_questions():
    try:
        data = request.get_json(force=True)
        exam_type = data.get("examType", "TIMSS")
        grade = data.get("grade", "Grade 8")
        subject = data.get("subject", "Math")
        total_count = int(data.get("count", 10))
        lang = data.get("lang", "en")

        # ✅ Parallel batching (6 workers)
        batch_size = 5
        batches = [(exam_type, grade, subject, batch_size, lang) 
                   for _ in range(0, total_count, batch_size)]

        start_time = time.time()

        def generate_batch(params):
            e_type, g, subj, count, l = params
            prompt = build_prompt(e_type, g, subj, count, lang=l)
            return call_gemini(prompt)

        results = list(executor.map(generate_batch, batches))
        all_questions = [q for batch in results for q in batch]

        # Ensure unique IDs
        for i, q in enumerate(all_questions, start=1):
            q["id"] = i

        elapsed = round(time.time() - start_time, 2)
        print(f" Generated {len(all_questions)} questions in {elapsed} seconds.")

        return jsonify({
            "examType": exam_type,
            "timeLimit": f"{40 + total_count//5} minutes",
            "questions": all_questions,
            "elapsed": f"{elapsed} sec"
        }), 200

    except Exception as e:
        print(" Error in /generate-questions:", e)
        return jsonify({"error": str(e)}), 500

# 🟢 Evaluate endpoint
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
        result = call_gemini(prompt)
        return jsonify(result), 200

    except Exception as e:
        print(" Error in /evaluate:", e)
        return jsonify({"error": str(e)}), 500

# ✅ Health check route
@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "EduPortal Flask API running successfully"}), 200

# ✅ Run locally (Render uses gunicorn)
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
