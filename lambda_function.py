import json
import os
import urllib.request

def lambda_handler(event, context):
    # 1. 環境変数からAPIキーを取得
    api_key = os.environ.get("GEMINI_API_KEY")
    
    # 2. LINEからのメッセージを取得（テスト時のエラー回避用）
    try:
        body = json.loads(event.get('body', '{}'))
        user_message = body['events'][0]['message']['text']
    except:
        user_message = "こんにちは" # テスト用

    # 3. Gemini API 直接呼び出し (v1 エンドポイントを使用)
    # ここを v1 に固定することで 404 を物理的に回避します
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    payload = {
        "contents": [{
            "parts": [{"text": user_message}]
        }]
    }
    
    headers = {'Content-Type': 'application/json'}
    
    try:
        # リクエスト送信
        req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method='POST')
        with urllib.request.urlopen(req) as res:
            response_body = res.read().decode('utf-8')
            result = json.loads(response_body)
            # Gemini の返答を抽出
            gemini_text = result['candidates'][0]['content']['parts'][0]['text']
            
            print(f"Geminiの回答: {gemini_text}")
            
            return {
                'statusCode': 200,
                'body': json.dumps({'message': gemini_text})
            }
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
