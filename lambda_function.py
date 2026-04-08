import os
import json
import google.generativeai as genai

# 環境変数からキーを取得
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

def lambda_handler(event, context):
    # 1. LINEからのメッセージを取得
    body = json.loads(event['body'])
    user_message = body['events'][0]['message']['text']
    
    # 2. Geminiに「ツール（関数）」を教える
    def add_calendar_event(title: str, date: str, time: str):
        """カレンダーに予定を登録する際に呼び出す関数"""
        # ここでは実際に登録せず、AIがこの関数を選んだことを確認するためのダミー
        return f"【仮登録完了】{date} {time}に「{title}」を予約しました"

    model = genai.GenerativeModel(
        model_name='gemini-1.5-flash',
        tools=[add_calendar_event] # ここで関数を渡す！
    )

    # 3. Geminiで推論実行
    chat = model.start_chat()
    response = chat.send_message(user_message)

    # 4. Geminiが関数を呼びたがっているかチェック
    if response.candidates[0].content.parts[0].function_call:
        fn = response.candidates[0].content.parts[0].function_call
        # ここで本来はGoogle APIなどを叩く
        reply_text = f"AIが判断したデータ:\nタイトル: {fn.args['title']}\n日付: {fn.args['date']}\n時間: {fn.args['time']}"
    else:
        reply_text = response.text

    # 5. LINEに返信（簡易的なレスポンス形式）
    return {
        'statusCode': 200,
        'body': json.dumps({'reply': reply_text})
    }
