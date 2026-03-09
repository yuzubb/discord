from flask import Flask, jsonify, request
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError
import random
import os

app = Flask(__name__)
PUBLIC_KEY = os.getenv('DISCORD_PUBLIC_KEY')

@app.route('/api', methods=['POST'])
def interactions():
    # Discordからの署名検証（必須）
    signature = request.headers.get('X-Signature-Ed25519')
    timestamp = request.headers.get('X-Signature-Timestamp')
    body = request.data.decode('utf-8')

    verify_key = VerifyKey(bytes.fromhex(PUBLIC_KEY))
    try:
        verify_key.verify(f'{timestamp}{body}'.encode(), bytes.fromhex(signature))
    except BadSignatureError:
        return 'invalid request signature', 401

    data = request.json
    # Ping (Discordからの接続確認) への応答
    if data.get('type') == 1:
        return jsonify({"type": 1})

    # スラッシュコマンドへの応答
    if data.get('type') == 2:
        results = ['大吉', '中吉', '小吉', '吉', '末吉', '凶']
        choice = random.choice(results)
        return jsonify({
            "type": 4,
            "data": {"content": f"今日の運勢は **{choice}** です！"}
        })

    return jsonify({"type": 1})
