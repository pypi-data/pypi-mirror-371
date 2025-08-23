# skai.py
import openai

# --- Biến toàn cục để lưu API key và model ---
_api_key = ""
_model = "gpt-3.5-turbo"

def setapi(key: str):
    """
    Thiết lập API key cho skai
    """
    global _api_key
    _api_key = key
    openai.api_key = _api_key

def setmodel(model_name: str):
    """
    Thiết lập model AI sử dụng
    """
    global _model
    _model = model_name

def askai(prompt: str) -> str:
    """
    Gửi câu hỏi đến AI và nhận trả lời (chưa in ra)
    """
    if not _api_key:
        raise ValueError("Bạn chưa thiết lập API key. Dùng skai.setapi('{apikey}') trước.")
    response = openai.ChatCompletion.create(
        model=_model,
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=500
    )
    return response['choices'][0]['message']['content'].strip()

def awnser(prefix: str, answer_text: str):
    """
    In ra câu trả lời AI với tiền tố
    """
    print(f"{prefix}{answer_text}")
