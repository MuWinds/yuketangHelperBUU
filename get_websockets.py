# -*- coding: utf-8 -*-
# version 1
# developed by MuWinds
import json
import websocket
import threading
import qrcode
import io
import os

class WebSocketQrcode:
    def __init__(self):
        self.fetch_qrcode_timer = None
        self.ws = None
        self.login_message=""

    def on_message(self, ws, message):
        msg = json.loads(message)
        if 'ticket' in msg:
            if(msg['qrcode']!=''):
                print_qrcode(msg['qrcode'])
        if msg.get('op') == 'requestlogin':
            self.fetch_qrcode()
        if msg.get('op') == 'loginsuccess':
            self.login_message = message
            #关闭连接
            self.ws.close()
            if self.fetch_qrcode_timer:
                self.fetch_qrcode_timer.cancel()

    def on_error(self, ws, error):
        print("Error:", error)

    def on_close(self, ws,close_status_code,bytestring):
        print("")#关闭连接
    def on_open(self, ws):
        print("Connection opened")
        self.fetch_qrcode()
        self.fetch_qrcode_timer = threading.Timer(60, self.fetch_qrcode)  # 50秒后刷新二维码
        self.fetch_qrcode_timer.start()

    def fetch_qrcode(self):
        if self.ws:
            self.ws.send(json.dumps({
                'op': "requestlogin",
                'role': "web",
                'version': 1.4,
                'type': "qrcode"
            }))

    def run(self,domain):
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
    qr.print_ascii(out=None,tty=False,invert=False)