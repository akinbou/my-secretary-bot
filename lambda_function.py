import google.generativeai as genai
import os

# transport='rest' を入れるのがコツです
genai.configure(api_key=os.environ["GEMINI_API_KEY"], transport='rest')

def lambda_handler(event, context):
    # モデル名を最新版を指す文字列にする
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    
    # 案3で試したように、まずは tools 無しで会話ができるかテスト
    response = model.generate_content("こんにちは")
    print(response.text)
