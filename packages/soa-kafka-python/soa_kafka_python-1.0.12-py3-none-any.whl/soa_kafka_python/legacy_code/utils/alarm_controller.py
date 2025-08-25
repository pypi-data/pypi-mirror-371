from playsound import playsound
from opcua import ua, Client
from pathlib import Path
import time
import smtplib
import requests
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.text import MIMEText

class AlarmController:
    def __init__(self, configs) -> None:
        self.__configs = configs
    
    def send_audio_alarms(self, audio_file) -> None:
        print(f"{audio_file}")
        playsound(f"{audio_file}")
            
    def send_plc_alarms(self, ns, audio_signal_start) -> None:
        client = Client(self.__configs["broadcast_plc_address"])
        ns = ns
        audio_signal_start = audio_signal_start
        if(ns<0):
            print("play with no sound")
            return
        try:
            client.connect()
            
            # Start
            var_start = client.get_node(f'ns={ns};i={audio_signal_start}')
            dv_start = ua.DataValue(True)
            var_start.set_value(dv_start)
            dv_start = ua.DataValue(False)
            var_start.set_value(dv_start)
            #print(f"play audio on {line}_{station}")
    
        finally:
            client.disconnect()
    
    def send_email_alarms(self, subject_str, content, img_path, config_segmentation) -> None:
        smtp_server = self.__configs["smtp_server"]
        receivers = config_segmentation["smtp_receivers"]
        sender = self.__configs["smtp_sender"]
        msg_root = MIMEMultipart('related')
        msg_alt = MIMEMultipart('alternative')
        msg_root["From"] = Header(sender, "utf-8")
        msg_root["To"] = Header(";".join(receivers), "utf-8")
        msg_root["Subject"] = Header(subject_str, "utf-8")
        msg_root.attach(msg_alt)
        img_tag = content + "<br>"
        if(img_path is not None):
            img_tag += "<tr>"
            img_tag += "<td width=\'100%\' height=200 >\
                        <img src=\'cid:img_1\' width=\'100%\' />\
                    "
            img_tag += "</td>"
            img_tag += "</tr>"
            msg_root.attach(self._addimg(img_path, "<img_1>"))
        msg_alt.attach(MIMEText(img_tag, 'html', 'utf-8'))
        smtp_obj = smtplib.SMTP()
        try:
            smtp_obj.connect(smtp_server)
            smtp_obj.sendmail(sender, receivers, msg_root.as_string())
        finally:
            smtp_obj.quit()
    
    def send_http_alarms(self, detector_name, line) -> None:
        config_segmentation = self.__configs["line_config"][detector_name][line]
        http_alarm_url = config_segmentation["http_alarm_url"]
        print(http_alarm_url)
        res = requests.get(http_alarm_url)
        print(res)
        
    
    def _addimg(self, img_path, img_id):
        with open(img_path, "rb") as img_file:
            msg_img = MIMEImage(img_file.read())
        msg_img.add_header("Content-ID", img_id)
        
        return msg_img

if __name__=='__main__':
    # import snap7
    # client = snap7.client.Client()
    # client.connect("192.168.0.1", 0, 1)
    # print('connnected')
    # client.disconnect()
    import time
    
    client = Client("opc.tcp://10.95.95.230:4840")
    try:
        client.connect()

        var_start = client.get_node('ns=4;i=3')
        # var_stop = client.get_node('ns=4;i=7')
        # print(var_start.get_value())
        # print(var_stop.get_value())
        dv_start = ua.DataValue(True)
        var_start.set_value(dv_start)
        dv_start = ua.DataValue(False)
        var_start.set_value(dv_start)
        # dv_start = ua.DataValue(True)
        # dv_stop = ua.DataValue(False)
        # var_stop.set_value(dv_stop)
        # var_start.set_value(dv_start)
        # print(var_start.get_value())
        # print(var_stop.get_value())
        #Sleep(5)
        # time.sleep(5)
        # dv_start = ua.DataValue(False)
        # dv_stop = ua.DataValue(True)
        # var_start.set_value(dv_start)
        # var_stop.set_value(dv_stop)
        # print(var_start.get_value())
        # print(var_stop.get_value())
        
        # dv_stop = ua.DataValue(False)
        # var_stop.set_value(dv_stop)
        # print(var_stop.get_value())
        # var1 = client.get_node('ns=3; s="PLC"."GBGF_Stop_1"."Bool"')
        # print(var1.get_value())
    finally:
        client.disconnect()