import requests

def send_msg(msg):
   requests.post("https://ntfy.sh/CalcState7", data=msg.encode(encoding='utf-8'))