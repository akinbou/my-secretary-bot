import json
import os
import urllib.request

def lambda_handler(event, context):
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
    LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
    
    # 1. LINEからのイベント解析
    try:
        # 文字列か辞書かを判別して読み込み
        body_content = event.get('body', '{}')
        body = json.loads(body_content) if isinstance(body_content, str) else body_content
        
        if 'events' not in body or not body['events']:
            return {'statusCode': 200}

        event_data = body['events'][0]
        reply_token = event_data.get('replyToken')
        user_message = event_data.get('message', {}).get('text', '')
        
        if not reply_token or not user_message:
            return {'statusCode': 200}
    except Exception as e:
        print(f"解析エラー: {e}")
        return {'statusCode': 200}

    # 2. Gemini API 呼び出し (v1 / gemini-2.5-flash)
    # URLに key を含める形式を維持
    gemini_url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    # Payloadの構造をより厳密に定義
    gemini_payload = {
        "contents": [
            {
                "parts": [
                    {"text": user_message}
                ]
            }
        ]
    }
    
    try:
        # Geminiへ送信
        gemini_data = json.dumps(gemini_payload).encode('utf-8')
        gemini_req = urllib.request.Request(
            gemini_url, 
            data=gemini_data, 
            headers={'Content-Type': 'application/json'}, 
            method='POST'
        )
        
        with urllib.request.urlopen(gemini_req) as res:
            gemini_res = json.loads(res.read().decode('utf-8'))
            # 回答の抽出パスを安全に取得
            gemini_text = gemini_res['candidates'][0]['content']['parts'][0]['text']
            
        # 3. LINEへ返信
        line_url = "https://api.line.me/v2/bot/message/reply"
        line_payload = {
            "replyToken": reply_token,
            "messages": [{"type": "text", "text": gemini_text}]
        }
        line_headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
        }
        
        line_data = json.dumps(line_payload).encode('utf-8')
        line_req = urllib.request.Request(line_url, data=line_data, headers=line_headers, method='POST')
        with urllib.request.urlopen(line_req) as res:
            pass # 成功

        return {'statusCode': 200}

    except urllib.error.HTTPError as e:
        # 詳細なエラー内容をログに出力
        error_body = e.read().decode('utf-8')
        print(f"HTTPエラー詳細: {e.code} - {error_body}")
        return {'statusCode': 500, 'body': error_body}
    except Exception as e:
        print(f"その他エラー: {e}")
        return {'statusCode': 500}
