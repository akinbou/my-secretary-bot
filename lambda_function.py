import json
import os
import urllib.request
import time

def lambda_handler(event, context):
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
    LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
    
    # LINEからのイベント解析
    try:
        body_content = event.get('body', '{}')
        body = json.loads(body_content) if isinstance(body_content, str) else body_content
        if 'events' not in body or not body['events']: return {'statusCode': 200}
        event_data = body['events'][0]
        reply_token = event_data.get('replyToken')
        user_message = event_data.get('message', {}).get('text', '')
    except Exception as e:
        print(f"解析エラー: {e}")
        return {'statusCode': 200}

    # 1. Gemini API 呼び出し (ツールの定義を追加)
    gemini_url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    # Geminiに「カレンダー登録関数」の存在を教える
    tools = [{
        "function_declarations": [{
            "name": "add_calendar_event",
            "description": "Googleカレンダーに予定を登録します。",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "予定のタイトル"},
                    "start_datetime": {"type": "string", "description": "開始日時 (ISO 8601形式: YYYY-MM-DDTHH:MM:SS)"},
                    "end_datetime": {"type": "string", "description": "終了日時 (ISO 8601形式: YYYY-MM-DDTHH:MM:SS)"}
                },
                "required": ["title", "start_datetime", "end_datetime"]
            }
        }]
    }]

    gemini_payload = {
        "contents": [{"parts": [{"text": user_message}]}],
        "tools": tools
    }
    
    try:
        # Geminiへ送信
        gemini_req = urllib.request.Request(gemini_url, data=json.dumps(gemini_payload).encode('utf-8'), headers={'Content-Type': 'application/json'}, method='POST')
        with urllib.request.urlopen(gemini_req) as res:
            gemini_res = json.loads(res.read().decode('utf-8'))
            
        # 2. Geminiの回答を解析（関数呼び出しを求めているか？）
        part = gemini_res['candidates'][0]['content']['parts'][0]
        
        if 'functionCall' in part:
            # Geminiが「関数を使って！」と言った場合
            fn = part['functionCall']
            args = fn['args']
            # ここで実際にはカレンダーに登録する処理を呼び出す（次のステップで実装）
            reply_text = f"カレンダーに「{args['title']}」を登録する準備ができました！\n開始: {args['start_datetime']}"
        else:
            # 普通の会話の場合
            reply_text = part['text']
            
        # 3. LINEへ返信
        line_url = "https://api.line.me/v2/bot/message/reply"
        line_data = json.dumps({"replyToken": reply_token, "messages": [{"type": "text", "text": reply_text}]}).encode('utf-8')
        line_req = urllib.request.Request(line_url, data=line_data, headers={"Content-Type": "application/json", "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"}, method='POST')
        with urllib.request.urlopen(line_req) as res: pass

        return {'statusCode': 200}

    except Exception as e:
        print(f"エラー発生: {e}")
        return {'statusCode': 500}
