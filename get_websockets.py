# -*- coding: utf-8 -*-
# version 1
# developed by MuWinds
import json
import websocket
import threading
import qrcode
import os
import io


class WebSocketQrcode:
    def __init__(self):
        self.fetch_qrcode_timer = None
        self.ws = None
        self.login_message = ""

    def on_message(self, ws, message):
        msg = json.loads(message)
        if 'ticket' in msg:
            if (msg['qrcode'] != ''):
                print_qrcode(msg['qrcode'])
        if msg.get('op') == 'requestlogin':
            self.fetch_qrcode()
        if msg.get('op') == 'loginsuccess':
            self.login_message = message
            # 关闭连接
            self.ws.close()
            if self.fetch_qrcode_timer:
                self.fetch_qrcode_timer.cancel()

    def on_error(self, ws, error):
        print("Error:", error)

    def on_close(self, ws, close_status_code, bytestring):
        print("")  # 关闭连接

    def on_open(self, ws):
        print("Connection opened")
        self.fetch_qrcode()
        self.fetch_qrcode_timer = threading.Timer(
            60, self.fetch_qrcode)  # 50秒后刷新二维码
        self.fetch_qrcode_timer.start()

    def fetch_qrcode(self):
        if self.ws:
            self.ws.send(json.dumps({
                'op': "requestlogin",
                'role': "web",
                'version': 1.4,
                'type': "qrcode"
            }))

    def run(self, domain):
        self.ws = websocket.WebSocketApp("wss://"+domain+"/wsapp/",
                                         on_message=self.on_message,
                                         on_error=self.on_error,
                                         on_close=self.on_close)
        self.ws.on_open = self.on_open
        self.ws.run_forever()
        return self.login_message


def print_qrcode(qr_data):
    # 生成二维码
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')

    # 将二维码图像保存到内存
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)

    # 打印二维码
    os.system('cls' if os.name == 'nt' else 'clear')  # 清屏
    print("QRCode:")
    img.show()
