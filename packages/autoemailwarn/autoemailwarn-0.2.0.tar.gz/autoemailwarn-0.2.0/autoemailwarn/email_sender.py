import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr
from typing import List, Optional


class EmailSender:
    """邮件发送工具类

    用于通过 SMTP 服务器发送邮件，默认适配 QQ 邮箱的 SSL 方式（smtp.qq.com:465）。
    
    参数:
        sender (str): 发件人邮箱账号（如 123456@qq.com）。
        auth_code (str): 发件邮箱的授权码/应用专用密码。
        smtp_host (str): SMTP 服务器地址，默认 'smtp.qq.com'。
        smtp_port (int): SMTP 服务器端口，默认 465（SSL）。
        use_ssl (bool): 是否使用 SSL 方式连接，默认 True。
        timeout (Optional[float]): 连接/请求超时时间（秒），默认 None。
    """

    def __init__(
        self,
        sender: str,
        auth_code: str,
        smtp_host: str = "smtp.qq.com",
        smtp_port: int = 465,
        use_ssl: bool = True,
        timeout: Optional[float] = None,
    ) -> None:
        """初始化邮件发送器实例。

        Args:
            sender: 发件人邮箱账号。
            auth_code: 发件邮箱的授权码/应用专用密码。
            smtp_host: SMTP 服务器地址。
            smtp_port: SMTP 服务器端口。
            use_ssl: 是否使用 SSL 方式连接。
            timeout: 连接/请求超时时间（秒）。
        """
        self.sender = sender
        self.auth_code = auth_code
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.use_ssl = use_ssl
        self.timeout = timeout

    def send_text(
        self,
        receivers: List[str],
        subject: str,
        content: str,
        from_name: Optional[str] = None,
        to_names: Optional[List[str]] = None,
    ) -> None:
        """发送一封纯文本邮件。

        Args:
            receivers: 收件人邮箱列表。
            subject: 邮件主题。
            content: 纯文本正文内容。
            from_name: 发件人显示名称（可选）。
            to_names: 与 receivers 一一对应的收件人显示名称列表（可选）。

        Raises:
            ValueError: receivers 为空或 to_names 长度与 receivers 不一致时。
            smtplib.SMTPException: SMTP 相关错误（如认证失败、发送失败等）。
        """
        if not receivers:
            raise ValueError("receivers 不能为空")

        if to_names is not None and len(to_names) != len(receivers):
            raise ValueError("to_names 的长度必须与 receivers 一致，或设置为 None")

        # 构建邮件内容
        message = MIMEText(content, 'plain', 'utf-8')

        # 正确构造 From 头：仅对显示名进行 RFC2047 编码，并使用 formataddr 组装
        if from_name:
            from_formatted = formataddr((str(Header(from_name, 'utf-8')), self.sender))
        else:
            from_formatted = self.sender
        message['From'] = from_formatted

        # 正确构造 To 头：支持多收件人，显示名仅编码人名部分
        if to_names:
            tos = [formataddr((str(Header(name, 'utf-8')), addr)) for name, addr in zip(to_names, receivers)]
        else:
            tos = receivers
        message['To'] = ', '.join(tos)

        # 主题仅需对文本部分进行编码
        message['Subject'] = str(Header(subject, 'utf-8'))

        server = None
        try:
            # 建立 SMTP 连接
            if self.use_ssl:
                server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port, timeout=self.timeout)
            else:
                server = smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=self.timeout)
                server.starttls()

            # 登录并发送
            server.login(self.sender, self.auth_code)
            server.sendmail(self.sender, receivers, message.as_string())
        except smtplib.SMTPException:
            # 透传给上层处理，更符合库的使用习惯
            raise
        finally:
            if server is not None:
                try:
                    server.quit()
                except Exception:
                    try:
                        server.close()
                    except Exception:
                        pass