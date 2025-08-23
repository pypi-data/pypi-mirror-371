import warnings
warnings.filterwarnings("ignore")

import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from .utils import load_config

class EmailSender:

    def __init__(self, sender_addr, config):
        self.config = load_config(config)
        self.sender = sender_addr
        self.set_sender_config()


    def set_sender_config(self):
        if self.sender in self.config['email_config']:
            sender_config = self.config['email_config'][self.sender]
            self.authentication = sender_config['authentication']
            self.server_type = sender_config["server_type"]
            self.server_host = sender_config["server_host"]
            self.server_port = sender_config["server_port"]
        else:
            raise Exception(f'Sender Address {self.sender} is Invalid.')

    def send_email(self, to_addrs, bcc_addrs=[], subject='', text='', attachment_path=None):
        if isinstance(to_addrs, str):
            to_addrs = [to_addrs]
        if isinstance(bcc_addrs, str):
            bcc_addrs = [bcc_addrs]

        try:
            # 发件人和收件人信息
            message = MIMEMultipart()
            message["From"] = self.sender
            message["To"] = ",".join(to_addrs)
            if len(bcc_addrs) > 0:
                message["Bcc"] = ",".join(bcc_addrs)
            message["Subject"] = subject

            # 添加邮件正文
            message.attach(MIMEText(text, "plain"))

            if attachment_path:
                part = MIMEApplication(open(attachment_path, 'rb').read())
                filename = attachment_path.split('\\')[-1].split('/')[-1]
                part.add_header('Content-Disposition', 'attachment', filename=('gbk', '', filename))
                message.attach(part)

            # 连接到SMTP服务器
            server = smtplib.SMTP_SSL(self.server_host, self.server_port)
            server.login(self.sender, self.authentication)
            server.sendmail(from_addr=self.sender, to_addrs=to_addrs+bcc_addrs, msg=message.as_string())
            server.close()
        except Exception as e:
            current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            with open(f'log_{current_time}.txt', 'w') as f:
                f.write(str(e))
