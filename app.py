from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio, httpx, json, re, time

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["*", "http://localhost:3000", "https://eduportal.pro"]}})

# 🔑 API + model
GEMINI_API_KEY = "AIzaSyA6VyEO3weAJLVm39d_GmmSlzkn8NvTuZw"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={GEMINI_API_KEY}"

# 🧩 Prompt builder
def build_prompt(exam_type, grade, subject, count, lang="en", task="generate", answers=None, student_id=""):
    if task == "generate":
        if lang == "ar":
            return f"""
            أنشئ {count} أسئلة متعددة الخيارات لامتحان {exam_type}.
            الصف: {grade}
            المادة: {subject}
            أرجع فقط JSON بالشكل:
            [{{"id":1,"question":"...","options":["أ","ب","ج","د"],"correct_answer":"أ"}}]
            """
        else:
            return f"""
            Create {count} concise multiple-choice questions for a {exam_type} exam in grade {grade} ({subject}).
            Return ONLY valid JSON like:
            [{{"id":1,"question":"...","options":["A","B","C","D"],"correct_answer":"A"}}]
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
            {{"score":0,"feedback":[{{"question":"...","student_answer":"...","correct_answer":"...","comment":"..."}}]}}
            """
        else:
            return f"""
            Evaluate student's answers for a {exam_type} exam ({subject}, grade {grade}).
            Student ID: {student_id}
            Answers:
            {answers}
            Return JSON like:
            {{"score":0,"feedback":[{{"question":"...","student_answer":"...","correct_answer":"...","comment":"..."}}]}}
            """

# ⚡ Fast async Gemini caller
async def call_gemini(prompt):
    async with httpx.AsyncClient(timeout=20) as client:
        try:
            r = await client.post(
                GEMINI_URL,
                headers={"Content-Type": "application/json"},
                json={"contents": [{"parts": [{"text": prompt}]}]},
            )
            r.raise_for_status()
            data = r.json()
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            try:
                return json.loads(text)
            except:
                match = re.search(r"\[.*\]", text, re.S)
                if match:
                    return json.loads(match.group(0))
            return []
        except Exception as e:
            print("❌ Gemini error:", e)
            return []

# 🟢 Async question generation
@app.route("/generate-questions", methods=["POST"])
def generate_questions():
    try:
        data = request.get_json(force=True)
        exam_type = data.get("examType", "TIMSS")
        grade = data.get("grade", "Grade 8")
        subject = data.get("subject", "Math")
        total_count = int(data.get("count", 10))
        lang = data.get("lang", "en")

        batch_size = 3
        batches = [(exam_type, grade, subject, batch_size, lang) 
                   for _ in range(0, total_count, batch_size)]

        async def process_all():
            start = time.time()
            tasks = []
            for b in batches:
                e_type, g, subj, c, l = b
                prompt = build_prompt(e_type, g, subj, c, l)
                tasks.append(call_gemini(prompt))
            results = await asyncio.gather(*tasks)
            questions = [q for batch in results for q in batch if isinstance(q, dict)]
            for i, q in enumerate(questions, start=1):
                q["id"] = i
            elapsed = round(time.time() - start, 2)
            return {"questions": questions, "elapsed": elapsed}

        result = asyncio.run(process_all())
        return jsonify({
            "examType": exam_type,
            "timeLimit": f"{40 + total_count//5} minutes",
            "questions": result["questions"],
            "elapsed": f"{result['elapsed']} sec"
        }), 200

    except Exception as e:
        print("❌ Error:", e)
        return jsonify({"error": str(e)}), 500

# 🟢 Evaluate answers
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

        prompt = build_prompt(exam_type, grade, subject, None, lang, "evaluate", answers, student_id)
        result = asyncio.run(call_gemini(prompt))
        return jsonify(result), 200
    except Exception as e:
        print("❌ Eval error:", e)
        return jsonify({"error": str(e)}), 500

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "EduPortal Flask API fast version running 🚀"}), 200

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
