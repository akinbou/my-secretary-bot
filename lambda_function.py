import json
import os
import urllib.request

def lambda_handler(event, context):
    # 1. 環境変数の取得
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
    LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
    
    # 2. LINEからのイベント解析
    try:
        body = json.loads(event.get('body', '{}'))
        event_data = body['events'][0]
        reply_token = event_data['replyToken']
        user_message = event_data['message']['text']
    except Exception as e:
        print(f"解析エラー: {e}")
        return {'statusCode': 200} # テスト時などはここで終了

    # 3. Gemini API 呼び出し (v1 / gemini-2.5-flash)
    gemini_url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    gemini_payload = {
        "contents": [{"parts": [{"text": user_message}]}]
    }
    
    try:
        # Geminiへ送信
        gemini_req = urllib.request.Request(
            gemini_url, 
            data=json.dumps(gemini_payload).encode('utf-8'), 
            headers={'Content-Type': 'application/json'}, 
            method='POST'
        )
        with urllib.request.urlopen(gemini_req) as res:
            gemini_res = json.loads(res.read().decode('utf-8'))
            gemini_text = gemini_res['candidates'][0]['content']['parts'][0]['text']
            
        # 4. LINE Messaging API で返信
        line_url = "https://api.line.me/v2/bot/message/reply"
        line_payload = {
            "replyToken": reply_token,
            "messages": [{"type": "text", "text": gemini_text}]
        }
        line_headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
        }
        
        line_req = urllib.request.Request(
            line_url, 
            data=json.dumps(line_payload).encode('utf-8'), 
            headers=line_headers, 
            method='POST'
        )
        with urllib.request.urlopen(line_req) as res:
            print("LINE返信成功")

        return {'statusCode': 200, 'body': json.dumps('success')}

    except Exception as e:
        print(f"エラー発生: {e}")
        return {'statusCode': 500, 'body': json.dumps(str(e))}
