from flask import Flask, request, jsonify, render_template_string
import requests
import sympy as sp

app = Flask(__name__)

API_KEY = "AIzaSyAUagFEGM0qxAowl1NbOxgi45s--oXtHJE"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key={API_KEY}"

HTML_PAGE = """
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ماشین حساب هوش مصنوعی</title>
    <style>
        body { font-family: sans-serif; background: #121212; color: #fff; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; padding: 20px; box-sizing: border-box; }
        .card { background: #1e1e1e; padding: 25px; border-radius: 16px; width: 100%; max-width: 400px; box-shadow: 0 4px 20px rgba(0,0,0,0.5); }
        h2 { text-align: center; margin-top: 0; color: #4dabf7; }
        input { width: 100%; padding: 12px; border-radius: 8px; border: 1px solid #333; background: #2a2a2a; color: #fff; font-size: 16px; margin-bottom: 15px; box-sizing: border-box; }
        button { width: 100%; padding: 12px; background: #228be6; color: #fff; border: none; border-radius: 8px; font-size: 16px; cursor: pointer; font-weight: bold; }
        button:disabled { background: #555; }
        .result-box { margin-top: 20px; padding: 15px; background: #252525; border-radius: 8px; display: none; }
        .equation { color: #a9e34b; font-family: monospace; font-size: 18px; margin: 5px 0; direction: ltr; text-align: left; }
        .answer { color: #ffd43b; font-size: 22px; font-weight: bold; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="card">
        <h2>ماشین‌حساب هوشمند</h2>
        <input type="text" id="userInput" placeholder="مثلاً: مساحت دایره با شعاع ۵ منهای ۳">
        <button id="calcBtn" onclick="calculate()">تبدیل و محاسبه</button>
        <div class="result-box" id="resultBox">
            <div>معادله ریاضی:</div>
            <div class="equation" id="equationText"></div>
            <div>پاسخ نهایی:</div>
            <div class="answer" id="answerText"></div>
        </div>
    </div>

    <script>
        async function calculate() {
            const input = document.getElementById('userInput').value;
            if(!input) return;
            const btn = document.getElementById('calcBtn');
            const resBox = document.getElementById('resultBox');
            btn.disabled = true;
            btn.innerText = 'در حال پردازش هوش مصنوعی...';
            resBox.style.display = 'none';

            try {
                const res = await fetch('/api/calculate', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ text: input })
                });
                const data = await res.json();
                if(data.error) {
                    alert('خطا: ' + data.error);
                } else {
                    document.getElementById('equationText').innerText = data.expression;
                    document.getElementById('answerText').innerText = data.result;
                    resBox.style.display = 'block';
                }
            } catch(e) {
                alert('خطا در برقراری ارتباط');
            } finally {
                btn.disabled = false;
                btn.innerText = 'تبدیل و محاسبه';
            }
        }
    </script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_PAGE)

@app.route("/api/calculate", methods=["POST"])
def calculate():
    try:
        req_data = request.get_json() or {}
        text = req_data.get("text", "")
        if not text:
            return jsonify({"error": "متنی وارد نشده است"}), 400

        prompt = (
            "فقط و فقط یک عبارت ریاضی پایتونی سازگار با sympy بدون هیچ متن، علامت بک‌تیک، گیومه یا توضیح اضافی بنویس. "
            f"متن: {text}"
        )
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        res = requests.post(GEMINI_URL, json=payload, timeout=20)
        data = res.json()

        if "error" in data:
            return jsonify({"error": data["error"]["message"]}), 400

        raw_text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
        expression = raw_text.replace("`", "").strip()
        result = float(sp.sympify(expression).evalf())
        return jsonify({"expression": expression, "result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
