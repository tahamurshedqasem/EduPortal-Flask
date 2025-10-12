# # from flask import Flask, request, jsonify
# # import requests, os, json, re

# # app = Flask(__name__)

# # # 🔑 Gemini API Configuration
# # GEMINI_API_KEY = "AIzaSyA1tOLp9zmbiBprpuhQZqq7s6TERss4x7s"
# # GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"


# # # 🧠 Helper: Build Prompt
# # def build_prompt(exam_type, grade, subject, count, lang="en", task="generate", answers=None, student_id=""):
# #     if task == "generate":
# #         if lang == "ar":
# #             return f"""
# #             أنت خبير في إعداد الاختبارات.
# #             المهمة: أنشئ {count} أسئلة فريدة ومبتكرة لامتحان {exam_type}.
# #             الصف: {grade}
# #             المادة: {subject}
# #             ✅ القواعد:
# #             - لا يوجد أسئلة مكررة.
# #             - يجب أن تكون الأسئلة متنوعة ومناسبة للمستوى.
# #             - كل سؤال يجب أن يحتوي على:
# #               "id": رقم,
# #               "question": "نص السؤال",
# #               "options": ["أ", "ب", "ج", "د"],
# #               "correct_answer": "الإجابة الصحيحة"
# #             - استخدم مستويات صعوبة مختلفة (سهل، متوسط، صعب).
# #             - أرجع فقط مصفوفة JSON صحيحة بدون أي شروح.
# #             مثال:
# #             [
# #               {{
# #                 "id": 1,
# #                 "difficulty": "سهل",
# #                 "question": "ما نتيجة 2 + 2؟",
# #                 "options": ["3", "4", "5", "6"],
# #                 "correct_answer": "4"
# #               }},
# #               {{
# #                 "id": 2,
# #                 "difficulty": "متوسط",
# #                 "question": "حل: 5س - 7 = 18",
# #                 "options": ["س=3", "س=4", "س=5", "س=6"],
# #                 "correct_answer": "س=5"
# #               }}
# #             ]
# #             """
# #         else:
# #             # English prompt
# #             return f"""
# #             You are an expert exam creator.
# #             Task: Generate {count} UNIQUE and Creative questions for a {exam_type} exam.
# #             Grade: {grade}
# #             Subject: {subject}
# #             ✅ Rules:
# #             - No duplicate or repeated questions.
# #             - Creative and varied concepts for each question.
# #             - Each question must have:
# #               "id": number,
# #               "question": "the question text",
# #               "options": ["A", "B", "C", "D"],
# #               "correct_answer": "the correct option"
# #             - Use **different difficulty levels** (Easy, Medium, Hard).
# #             - Return ONLY a valid JSON array with no explanations.
# #             """
# #     else:
# #         # Evaluate
# #         if lang == "ar":
# #             return f"""
# #             قم بتقييم إجابات الطالب لامتحان {exam_type}.
# #             الصف: {grade}
# #             المادة: {subject}
# #             معرف الطالب: {student_id}
# #             إجابات الطالب: {answers}
# #             أرجع JSON بالصيغة التالية:
# #             {{
# #               "score": <رقم من 0-100>,
# #               "feedback": [
# #                 {{
# #                   "question": "...",
# #                   "student_answer": "...",
# #                   "correct_answer": "...",
# #                   "comment": "..."
# #                 }}
# #               ]
# #             }}
# #             """
# #         else:
# #             return f"""
# #             Evaluate student's answers for a {exam_type} exam.
# #             Grade: {grade}
# #             Subject: {subject}
# #             Student ID: {student_id}
# #             Student answers: {answers}
# #             Output JSON in this format:
# #             {{
# #               "score": <number from 0-100>,
# #               "feedback": [
# #                 {{
# #                   "question": "...",
# #                   "student_answer": "...",
# #                   "correct_answer": "...",
# #                   "comment": "..."
# #                 }}
# #               ]
# #             }}
# #             """


# # # 🟢 Generate Questions Endpoint
# # @app.route("/generate-questions", methods=["POST"])
# # def generate_questions():
# #     data = request.get_json()
# #     exam_type = data.get("examType", "TIMSS")
# #     grade = data.get("grade", "Grade 8")
# #     subject = data.get("subject", "Math")
# #     count = data.get("count", 5)
# #     lang = data.get("lang", "en")

# #     prompt = build_prompt(exam_type, grade, subject, count, lang=lang, task="generate")

# #     try:
# #         resp = requests.post(
# #             GEMINI_URL,
# #             headers={"Content-Type": "application/json"},
# #             json={"contents": [{"parts": [{"text": prompt}]}]},
# #         )
# #         resp.raise_for_status()

# #         gemini_data = resp.json()
# #         raw_text = gemini_data["candidates"][0]["content"]["parts"][0]["text"]

# #         try:
# #             questions = json.loads(raw_text)
# #         except:
# #             match = re.search(r"\[.*\]", raw_text, re.S)
# #             if match:
# #                 questions = json.loads(match.group(0))
# #             else:
# #                 return jsonify({"error": "Invalid JSON from Gemini", "raw": raw_text}), 500

# #         return jsonify({
# #             "examType": exam_type,
# #             "timeLimit": "40 minutes",
# #             "questions": questions
# #         })

# #     except Exception as e:
# #         return jsonify({"error": "Failed to generate questions", "details": str(e)}), 500


# # # 🟢 Evaluate Answers Endpoint
# # @app.route("/evaluate", methods=["POST"])
# # def evaluate():
# #     data = request.get_json()
# #     exam_type = data.get("examType", "TIMSS")
# #     grade = data.get("grade", "Grade 8")
# #     subject = data.get("subject", "Math")
# #     student_id = data.get("studentId", "test_student")
# #     answers = data.get("answers", [])
# #     lang = data.get("lang", "en")

# #     prompt = build_prompt(
# #         exam_type, grade, subject, None,
# #         lang=lang, task="evaluate",
# #         answers=answers, student_id=student_id
# #     )

# #     try:
# #         resp = requests.post(
# #             GEMINI_URL,
# #             headers={"Content-Type": "application/json"},
# #             json={"contents": [{"parts": [{"text": prompt}]}]},
# #         )
# #         resp.raise_for_status()

# #         gemini_data = resp.json()
# #         raw_text = gemini_data["candidates"][0]["content"]["parts"][0]["text"]

# #         try:
# #             feedback_json = json.loads(raw_text)
# #         except:
# #             match = re.search(r"\{.*\}", raw_text, re.S)
# #             if match:
# #                 feedback_json = json.loads(match.group(0))
# #             else:
# #                 feedback_json = {"score": None, "feedback": raw_text}

# #         return jsonify(feedback_json)

# #     except Exception as e:
# #         return jsonify({"error": "Failed to evaluate answers", "details": str(e)}), 500


# # # 🟢 Run Flask App
# # if __name__ == "__main__":
# #     app.run(debug=True, port=5000)
# from flask import Flask, request, jsonify
# import requests, os, json, re

# app = Flask(__name__)

# # 🔑 Gemini API
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"


# # 🟢 Helper: Build Prompt
# def build_prompt(exam_type, grade, subject, count, lang="en", task="generate", answers=None, student_id=""):
#     if task == "generate":
#         # ========== Arabic Version ==========
#         if lang == "ar":
#             # Normalize exam type
#             exam_type_lower = exam_type.strip().lower()

#             # Context by exam type
#             if "بيرلز" in exam_type_lower or "pirls" in exam_type_lower:
#                 framework_context = f"""
#                 اختبار PIRLS يقيس مهارات الفهم القرائي للصف {grade}.
#                 يجب أن يكون لكل اختبار نص قصير واقعي (حوالي 80 إلى 120 كلمة)، ثم {count} أسئلة متعددة الخيارات تعتمد على النص فقط.
#                 """
#             elif "تيمس" in exam_type_lower or "timss" in exam_type_lower:
#                 framework_context = f"""
#                 اختبار TIMSS يقيس المفاهيم والمهارات في مادة {subject} للصف {grade}.
#                 الأسئلة يجب أن تكون رقمية، علمية، وتغطي مستويات: معرفة، تطبيق، واستدلال.
#                 """
#             elif "بيزا" in exam_type_lower or "pisa" in exam_type_lower:
#                 framework_context = f"""
#                 اختبار PISA يقيس مهارات التفكير النقدي وحل المشكلات في مواقف حياتية واقعية لطلاب الصف {grade}.
#                 الأسئلة يجب أن تكون تطبيقية وتركز على التفسير والتحليل وليس الحفظ.
#                 """
#             else:
#                 framework_context = f"اختبار {exam_type} للصف {grade} في مادة {subject}."

#             return f"""
#             أنت خبير تربوي مختص في تصميم اختبارات {exam_type}.
#             {framework_context}

#             🎯 المطلوب:
#             أنشئ اختبارًا يحتوي على {count} أسئلة أصلية وواقعية، مرتبة حسب الصعوبة (سهل، متوسط، صعب).

#             🧩 القواعد العامة:
#             - لا تكتب أي نص خيالي أو غير منطقي.
#             - استخدم لغة عربية واضحة مناسبة للصف {grade}.
#             - اجعل كل سؤال يقيس مهارة واحدة فقط (فهم، تحليل، تطبيق، استنتاج).
#             - لا تكرر نفس نوع السؤال.
#             - أرجع النتيجة بصيغة JSON فقط، بدون أي شرح أو نص إضافي.

#             ⚙️ الصيغة المطلوبة:
#             {{
#               "exam_type": "{exam_type}",
#               "grade": "{grade}",
#               "subject": "{subject}",
#               "reading_passage": "إذا كان الامتحان PIRLS، اكتب هنا نصًا قصيرًا مناسبًا.",
#               "questions": [
#                 {{
#                   "id": 1,
#                   "difficulty": "سهل",
#                   "question": "اكتب هنا السؤال الأول الواقعي.",
#                   "options": ["الخيار أ", "الخيار ب", "الخيار ج", "الخيار د"],
#                   "correct_answer": "الخيار الصحيح",
#                   "skill": "اسم المهارة"
#                 }},
#                 {{
#                   "id": 2,
#                   "difficulty": "متوسط",
#                   "question": "اكتب هنا سؤالًا متوسط الصعوبة.",
#                   "options": ["أ", "ب", "ج", "د"],
#                   "correct_answer": "الإجابة الصحيحة",
#                   "skill": "التحليل أو التطبيق"
#                 }}
#               ]
#             }}

#             أرجع فقط كائن JSON صحيح بدون أي نص خارجي.
#             """

#         # ========== English Version ==========
#         else:
#             exam_type_lower = exam_type.strip().lower()

#             if "pirls" in exam_type_lower:
#                 framework_context = f"""
#                 PIRLS measures reading comprehension for Grade {grade}.
#                 Include one short reading passage (80–120 words) and {count} multiple-choice questions strictly based on that text.
#                 """
#             elif "timss" in exam_type_lower:
#                 framework_context = f"""
#                 TIMSS measures students’ understanding in {subject} at Grade {grade}.
#                 Questions should assess factual knowledge, reasoning, and application of real math/science concepts.
#                 """
#             elif "pisa" in exam_type_lower:
#                 framework_context = f"""
#                 PISA measures problem-solving, reasoning, and critical thinking in real-world contexts for Grade {grade}.
#                 Focus on data interpretation, logic, and applied literacy.
#                 """
#             else:
#                 framework_context = f"International {exam_type} exam for Grade {grade} in {subject}."

#             return f"""
#             You are an expert educational test designer for {exam_type} international assessments.
#             {framework_context}

#             🎯 Task:
#             Create {count} high-quality, realistic, curriculum-aligned multiple-choice questions.

#             🧠 Rules:
#             - No imaginary or nonsensical content.
#             - Keep questions aligned with student level.
#             - Every question must assess one clear skill: understanding, reasoning, application, or analysis.
#             - Use diverse difficulty levels (Easy, Medium, Hard).
#             - For PIRLS: include one short reading passage.
#             - Return **only valid JSON**, no commentary.

#             ⚙️ Expected JSON structure:
#             {{
#               "exam_type": "{exam_type}",
#               "grade": "{grade}",
#               "subject": "{subject}",
#               "reading_passage": "Include only for PIRLS exams.",
#               "questions": [
#                 {{
#                   "id": 1,
#                   "difficulty": "Easy",
#                   "question": "Write the first question text here.",
#                   "options": ["A", "B", "C", "D"],
#                   "correct_answer": "B",
#                   "skill": "Comprehension"
#                 }},
#                 {{
#                   "id": 2,
#                   "difficulty": "Medium",
#                   "question": "Write the second question text here.",
#                   "options": ["A", "B", "C", "D"],
#                   "correct_answer": "A",
#                   "skill": "Reasoning"
#                 }}
#               ]
#             }}

#             Return JSON only — no explanation or description outside of it.
#             """

#     # ========== Evaluation Prompt ==========
#     else:
#         if lang == "ar":
#             return f"""
#             قم بتقييم إجابات الطالب في اختبار {exam_type}.

#             الصف: {grade}
#             المادة: {subject}
#             معرف الطالب: {student_id}

#             إجابات الطالب:
#             {answers}

#             أرجع JSON بالصيغة التالية:
#             {{
#               "score": <رقم من 0 إلى 100>,
#               "feedback": [
#                 {{
#                   "question": "...",
#                   "student_answer": "...",
#                   "correct_answer": "...",
#                   "comment": "شرح قصير عن صحة أو خطأ الإجابة"
#                 }}
#               ]
#             }}
#             """
#         else:
#             return f"""
#             Evaluate student's answers for the {exam_type} exam.

#             Grade: {grade}
#             Subject: {subject}
#             Student ID: {student_id}

#             Student answers:
#             {answers}

#             Return JSON in this format:
#             {{
#               "score": <number between 0 and 100>,
#               "feedback": [
#                 {{
#                   "question": "...",
#                   "student_answer": "...",
#                   "correct_answer": "...",
#                   "comment": "Brief explanation or correction"
#                 }}
#               ]
#             }}
#             """

   

#     else:  # evaluate
#         if lang == "ar":
#             return f"""
#             قم بتقييم إجابات الطالب لامتحان {exam_type}.

#             الصف: {grade}
#             المادة: {subject}
#             معرف الطالب: {student_id}

#             إجابات الطالب:
#             {answers}

#             أرجع JSON بالصيغة التالية:
#             {{
#               "score": <رقم من 0-100>,
#               "feedback": [
#                 {{
#                   "question": "...",
#                   "student_answer": "...",
#                   "correct_answer": "...",
#                   "comment": "..."
#                 }}
#               ]
#             }}
#             """
#         else:
#             return f"""
#             Evaluate student's answers for a {exam_type} exam.

#             Grade: {grade}
#             Subject: {subject}
#             Student ID: {student_id}

#             Student answers:
#             {answers}

#             Output JSON in this format:
#             {{
#               "score": <number from 0-100>,
#               "feedback": [
#                 {{
#                   "question": "...",
#                   "student_answer": "...",
#                   "correct_answer": "...",
#                   "comment": "..."
#                 }}
#               ]
#             }}
#             """


# # 🟢 Generate Questions
# @app.route("/generate-questions", methods=["POST"])
# def generate_questions():
#     data = request.get_json()
#     exam_type = data.get("examType", "TIMSS")
#     grade = data.get("grade", "Grade 8")
#     subject = data.get("subject", "Math")
#     count = data.get("count", 5)
#     lang = data.get("lang", "en")  # ✅ pick language

#     prompt = build_prompt(exam_type, grade, subject, count, lang=lang, task="generate")

#     try:
#         resp = requests.post(
#             GEMINI_URL,
#             headers={"Content-Type": "application/json"},
#             json={"contents": [{"parts": [{"text": prompt}]}]},
#         )
#         resp.raise_for_status()
#         gemini_data = resp.json()

#         raw_text = gemini_data["candidates"][0]["content"]["parts"][0]["text"]

#         try:
#             questions = json.loads(raw_text)
#         except:
#             match = re.search(r"\[.*\]", raw_text, re.S)
#             if match:
#                 questions = json.loads(match.group(0))
#             else:
#                 return jsonify({"error": "Invalid JSON from Gemini", "raw": raw_text}), 500

#         return jsonify({
#             "examType": exam_type,
#             "timeLimit": "10 minutes",
#             "questions": questions
#         })

#     except Exception as e:
#         return jsonify({"error": "Failed to generate questions", "details": str(e)}), 500


# # 🟢 Evaluate Answers
# @app.route("/evaluate", methods=["POST"])
# def evaluate():
#     data = request.get_json()
#     exam_type = data.get("examType", "TIMSS")
#     grade = data.get("grade", "Grade 8")
#     subject = data.get("subject", "Math")
#     student_id = data.get("studentId", "test_student")
#     answers = data.get("answers", [])
#     lang = data.get("lang", "en")  # ✅ support Arabic feedback

#     prompt = build_prompt(exam_type, grade, subject, None, lang=lang, task="evaluate", answers=answers, student_id=student_id)

#     try:
#         resp = requests.post(
#             GEMINI_URL,
#             headers={"Content-Type": "application/json"},
#             json={"contents": [{"parts": [{"text": prompt}]}]},
#         )
#         resp.raise_for_status()
#         gemini_data = resp.json()
#         raw_text = gemini_data["candidates"][0]["content"]["parts"][0]["text"]

#         try:
#             feedback_json = json.loads(raw_text)
#         except:
#             match = re.search(r"\{.*\}", raw_text, re.S)
#             if match:
#                 feedback_json = json.loads(match.group(0))
#             else:
#                 feedback_json = {"score": None, "feedback": raw_text}

#         return jsonify(feedback_json)

#     except Exception as e:
#         return jsonify({"error": "Failed to evaluate answers", "details": str(e)}), 500


# if __name__ == "__main__":
#     app.run(debug=True, port=5000)
from flask import Flask, request, jsonify
import requests, os, json, re

app = Flask(__name__)

# 🔑 Gemini API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"


# 🧠 Helper Function: Build Prompt
def build_prompt(exam_type, grade, subject, count, lang="en", task="generate", answers=None, student_id=""):
    # ---------------------- GENERATION MODE ----------------------
    if task == "generate":
        # Arabic Prompt
        if lang == "ar":
            exam_type_lower = exam_type.strip().lower()

            # Context by exam type
            if "بيرلز" in exam_type_lower or "pirls" in exam_type_lower:
                    framework_context = f"""
                اختبار PIRLS هو اختبار دولي لقياس الفهم القرائي لدى طلاب الصف {grade}.
                الهدف هو قياس قدرة الطالب على فهم النصوص الواقعية القصيرة من خلال قراءة نص ثم الإجابة على سؤال يعتمد عليه.

                📘 مكونات الاختبار:
                - يتكون الامتحان من {count} أسئلة.
                - كل سؤال يجب أن يحتوي على **نص واقعي قصير (80–120 كلمة)** مكتوب داخل الحقل "reading_passage".
                - بعد كل نص، يجب أن يكون هناك **سؤال واحد** يعتمد كليًا على هذا النص فقط.
                - لا يجوز طرح أي سؤال بدون نص قراءة يسبقه.
                - يجب أن تكون الخيارات الأربعة منطقية ومبنية على تفاصيل النص فقط.

                🔹 تعليمات صارمة:
                - ابدأ دائمًا بكتابة النص في الحقل "reading_passage".
                - لا تكتب أسئلة أو خيارات قبل النص.
                - النصوص يجب أن تكون واقعية ومناسبة لعمر طلاب الصف {grade}.
                - لا تستخدم الخيال، ولا الحيوانات المتحدثة، ولا أسماء خيالية.
                - اجعل الأسئلة متنوعة في المهارات: الفكرة الرئيسة، التفاصيل، المعاني، الاستنتاج، الغرض.

                ⚙️ الصيغة المطلوبة (JSON فقط):
                {{
                "exam_type": "PIRLS",
                "grade": "{grade}",
                "subject": "{subject}",
                "questions": [
                    {{
                    "id": 1,
                    "reading_passage": "اكتب هنا نصًا واقعيًا قصيرًا (80–120 كلمة) مناسبًا للصف {grade}.",
                    "question": "اكتب سؤالًا يعتمد على النص أعلاه فقط.",
                    "options": ["الخيار أ", "الخيار ب", "الخيار ج", "الخيار د"],
                    "correct_answer": "الخيار الصحيح",
                    "skill": "الفكرة الرئيسة أو التفاصيل أو المعنى"
                    }},
                    {{
                    "id": 2,
                    "reading_passage": "اكتب نصًا جديدًا واقعيًا آخر (80–120 كلمة).",
                    "question": "سؤال جديد يعتمد على النص الثاني.",
                    "options": ["...", "...", "...", "..."],
                    "correct_answer": "...",
                    "skill": "الاستنتاج أو الغرض"
                    }}
                ]
                }}

                ✳️ ملاحظات مهمة:
                - يجب أن يحتوي كل سؤال على نص قراءة في الحقل "reading_passage".
                - إذا لم يكن هناك نص، فالإجابة غير صالحة.
                - أرجع فقط JSON بدون أي شرح خارجي.
                """




            elif "تيمس" in exam_type_lower or "timss" in exam_type_lower:
                framework_context = f"""
                اختبار TIMSS يقيس المفاهيم والمهارات في مادة {subject} للصف {grade}.
                يجب أن تشمل الأسئلة مفاهيم رياضية أو علمية حقيقية وتغطي مستويات:
                - المعرفة
                - التطبيق
                - الاستدلال
                """

            elif "بيزا" in exam_type_lower or "pisa" in exam_type_lower:
                framework_context = f"""
                اختبار PISA يقيس مهارات التفكير النقدي وحل المشكلات في مواقف حياتية واقعية لطلاب الصف {grade}.
                الأسئلة يجب أن تكون تطبيقية وتربط بين التعلم والواقع اليومي.
                """

            else:
                framework_context = f"اختبار {exam_type} للصف {grade} في مادة {subject}."

            # Arabic Prompt Template
            return f"""
            أنت خبير تربوي مختص في تصميم اختبارات {exam_type}.
            {framework_context}

            🎯 المطلوب:
            إنشاء اختبار يحتوي على {count} أسئلة أصلية وواقعية، مرتبة حسب الصعوبة (سهل، متوسط، صعب).

            🧩 القواعد العامة:
            - لا تكتب أي نص خيالي أو غير منطقي.
            - استخدم لغة عربية واضحة ومناسبة للصف {grade}.
            - اجعل كل سؤال يقيس مهارة واحدة فقط (فهم، تحليل، تطبيق، استنتاج).
            - لا تكرر نفس نوع السؤال.
            - أرجع النتيجة بصيغة JSON فقط بدون أي شرح إضافي.

            ⚙️ الصيغة المطلوبة:
            {{
              "exam_type": "{exam_type}",
              "grade": "{grade}",
              "subject": "{subject}",
              "reading_passage": "إذا كان الامتحان PIRLS، اكتب هنا نصًا قصيرًا (80–120 كلمة).",
              "questions": [
                {{
                  "id": 1,
                  "difficulty": "سهل",
                  "question": "اكتب هنا السؤال الأول الواقعي.",
                  "options": ["الخيار أ", "الخيار ب", "الخيار ج", "الخيار د"],
                  "correct_answer": "الخيار الصحيح",
                  "skill": "اسم المهارة"
                }},
                {{
                  "id": 2,
                  "difficulty": "متوسط",
                  "question": "اكتب هنا سؤالًا متوسط الصعوبة.",
                  "options": ["أ", "ب", "ج", "د"],
                  "correct_answer": "الإجابة الصحيحة",
                  "skill": "التحليل أو التطبيق"
                }}
              ]
            }}

            أرجع فقط كائن JSON صالح بدون أي نص خارجي.
            """

        # English Prompt
        else:
            exam_type_lower = exam_type.strip().lower()

            if "pirls" in exam_type_lower:
                framework_context = f"""
                PIRLS (Progress in International Reading Literacy Study) assesses reading comprehension
                for Grade {grade} students through short, realistic passages followed by comprehension questions.

                📘 Structure of the exam:
                1. Include one short passage (80–120 words) suitable for Grade {grade}.
                   It can be narrative (story) or informational, but must be realistic and meaningful.
                2. Include {count} multiple-choice questions directly based on the passage.

                🎯 Each question should assess a specific reading skill:
                - Main idea identification
                - Supporting detail recognition
                - Vocabulary meaning in context
                - Inference and reasoning
                - Author’s purpose
                """

            elif "timss" in exam_type_lower:
                framework_context = f"""
                TIMSS (Trends in International Mathematics and Science Study) measures
                students’ understanding of mathematics and science at Grade {grade}.
                Questions should test factual knowledge, reasoning, and problem-solving
                using real-world examples.
                """

            elif "pisa" in exam_type_lower:
                framework_context = f"""
                PISA (Programme for International Student Assessment) measures students’
                ability to apply knowledge and skills to real-life situations.
                Focus on data interpretation, logical reasoning, and problem-solving.
                """

            else:
                framework_context = f"International {exam_type} exam for Grade {grade} in {subject}."

            # English Prompt Template
            return f"""
            You are an expert educational test designer for {exam_type} assessments.
            {framework_context}

            🎯 Task:
            Create {count} high-quality, realistic, and curriculum-aligned multiple-choice questions.

            🧠 Rules:
            - Avoid fictional or illogical content.
            - Keep all questions at an appropriate grade level.
            - Each question should measure one skill (understanding, reasoning, application, analysis).
            - Vary difficulty levels (Easy, Medium, Hard).
            - For PIRLS: include one short reading passage (80–120 words).
            - Return **only valid JSON**, with no extra commentary.

            ⚙️ Expected JSON structure:
            {{
              "exam_type": "{exam_type}",
              "grade": "{grade}",
              "subject": "{subject}",
              "reading_passage": "Include only for PIRLS exams.",
              "questions": [
                {{
                  "id": 1,
                  "difficulty": "Easy",
                  "question": "Write the first question text here.",
                  "options": ["A", "B", "C", "D"],
                  "correct_answer": "B",
                  "skill": "Comprehension"
                }},
                {{
                  "id": 2,
                  "difficulty": "Medium",
                  "question": "Write the second question text here.",
                  "options": ["A", "B", "C", "D"],
                  "correct_answer": "A",
                  "skill": "Reasoning"
                }}
              ]
            }}

            Return JSON only — no explanations or extra text.
            """

    # ---------------------- EVALUATION MODE ----------------------
    else:
        if lang == "ar":
            return f"""
            قم بتقييم إجابات الطالب في اختبار {exam_type}.

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
                  "comment": "شرح قصير عن صحة أو خطأ الإجابة"
                }}
              ]
            }}
            """
        else:
            return f"""
            Evaluate the student's answers for the {exam_type} exam.

            Grade: {grade}
            Subject: {subject}
            Student ID: {student_id}

            Student answers:
            {answers}

            Return JSON in the following format:
            {{
              "score": <number between 0 and 100>,
              "feedback": [
                {{
                  "question": "...",
                  "student_answer": "...",
                  "correct_answer": "...",
                  "comment": "Brief explanation or feedback"
                }}
              ]
            }}
            """


# 🟢 Endpoint: Generate Questions
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
            timeout=60
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
            "timeLimit": "10 minutes",
            "questions": questions
        })

    except Exception as e:
        return jsonify({"error": "Failed to generate questions", "details": str(e)}), 500


# 🟢 Endpoint: Evaluate Answers
@app.route("/evaluate", methods=["POST"])
def evaluate():
    data = request.get_json()
    exam_type = data.get("examType", "TIMSS")
    grade = data.get("grade", "Grade 8")
    subject = data.get("subject", "Math")
    student_id = data.get("studentId", "test_student")
    answers = data.get("answers", [])
    lang = data.get("lang", "en")

    prompt = build_prompt(exam_type, grade, subject, None, lang=lang,
                          task="evaluate", answers=answers, student_id=student_id)

    try:
        resp = requests.post(
            GEMINI_URL,
            headers={"Content-Type": "application/json"},
            json={"contents": [{"parts": [{"text": prompt}]}]},
            timeout=60
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


# 🏁 Run Application
if __name__ == "__main__":
    app.run(debug=True, port=5000)
