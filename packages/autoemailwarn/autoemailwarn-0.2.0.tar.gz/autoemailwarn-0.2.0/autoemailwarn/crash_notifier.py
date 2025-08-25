import os
import sys
import traceback
from typing import List, Optional

from .email_sender import EmailSender

# 模块级标记，防止重复注册
_REGISTERED = False
_ORIGINAL_EXCEPTHOOK = None


def enable_exception_email(
    sender: str,
    auth_code: str,
    receivers: List[str],
    subject: str = "程序异常退出通知",
    from_name: Optional[str] = None,
    to_names: Optional[List[str]] = None,
    smtp_host: str = "smtp.qq.com",
    smtp_port: int = 465,
    use_ssl: bool = True,
    timeout: Optional[float] = None,
) -> None:
    """启用未捕获异常的邮件自动通知。

    当进程发生未捕获异常（触发 sys.excepthook）时，将自动发送一封包含堆栈信息的邮件，随后继续调用原始 excepthook。

    参数:
        sender: 发件邮箱账号。
        auth_code: 发件邮箱授权码/应用专用密码。
        receivers: 收件人邮箱列表。
        subject: 邮件主题，默认“程序异常退出通知”。
        from_name: 发件人显示名称（可选）。
        to_names: 收件人显示名称列表（可选），需与 receivers 对齐。
        smtp_host: SMTP 服务器地址，默认 QQ 邮箱 smtp.qq.com。
        smtp_port: SMTP 服务器端口，默认 465。
        use_ssl: 是否使用 SSL，默认 True。
        timeout: 连接/请求超时（秒）。

    注意:
        - 本函数只注册一次，多次调用将被忽略。
        - 发送失败不会阻断程序的原始异常处理流程。
    """
    global _REGISTERED, _ORIGINAL_EXCEPTHOOK
    if _REGISTERED:
        return

    _ORIGINAL_EXCEPTHOOK = sys.excepthook
    mailer = EmailSender(
        sender=sender,
        auth_code=auth_code,
        smtp_host=smtp_host,
        smtp_port=smtp_port,
        use_ssl=use_ssl,
        timeout=timeout,
    )

    def _excepthook(etype, value, tb):
        """自定义 excepthook：先邮件通知，再交给原始 excepthook 处理。"""
        try:
            trace_text = "".join(traceback.format_exception(etype, value, tb))
            body = (
                "程序检测到未捕获异常并已自动告警。\n\n"
                f"异常类型: {etype.__name__}\n"
                f"异常信息: {value}\n\n"
                f"堆栈: \n{trace_text}"
            )
            mailer.send_text(
                receivers=receivers,
                subject=subject,
                content=body,
                from_name=from_name,
                to_names=to_names,
            )
        except Exception:
            # 任何在告警流程中的异常都吞掉，避免影响原始异常处理
            pass
        finally:
            try:
                if _ORIGINAL_EXCEPTHOOK:
                    _ORIGINAL_EXCEPTHOOK(etype, value, tb)
            except Exception:
                # 保底：避免因原始 excepthook 异常导致再次中断
                pass

        # 防止重复发送（一次异常只发送一次），这里不恢复 hook，保持全局有效

    sys.excepthook = _excepthook
    _REGISTERED = True


def enable_exception_email_from_env(prefix: str = "AUTOEMAILWARN_") -> bool:
    """从环境变量读取配置并启用未捕获异常的邮件通知。

    使用的环境变量（默认前缀 AUTOEMAILWARN_）：
        - ENABLE: '1'/'true' 开启。
        - SENDER: 发件邮箱。
        - AUTH_CODE: 授权码/应用专用密码。
        - RECEIVERS: 收件邮箱，多个用逗号分隔。
        - SUBJECT: 主题（可选）。
        - FROM_NAME: 发件人显示名（可选）。
        - TO_NAMES: 收件人显示名（可选），与 RECEIVERS 个数对应，逗号分隔。
        - SMTP_HOST: SMTP 服务器（可选，默认 smtp.qq.com）。
        - SMTP_PORT: 端口（可选，默认 465）。
        - USE_SSL: '1'/'true' 使用 SSL（可选，默认 true）。
        - TIMEOUT: 超时秒数（可选）。

    返回:
        bool: 若成功启用返回 True；若条件不满足或配置不完整返回 False。
    """
    enable_val = os.getenv(prefix + "ENABLE", "").strip().lower()
    if enable_val not in {"1", "true", "yes", "on"}:
        return False

    sender = os.getenv(prefix + "SENDER")
    auth_code = os.getenv(prefix + "AUTH_CODE")
    receivers_raw = os.getenv(prefix + "RECEIVERS", "")

    if not sender or not auth_code or not receivers_raw:
        return False

    receivers = [x.strip() for x in receivers_raw.split(",") if x.strip()]
    if not receivers:
        return False

    subject = os.getenv(prefix + "SUBJECT", "程序异常退出通知")
    from_name = os.getenv(prefix + "FROM_NAME") or None

    to_names_raw = os.getenv(prefix + "TO_NAMES", "").strip()
    to_names: Optional[List[str]] = None
    if to_names_raw:
        to_names = [x.strip() for x in to_names_raw.split(",")]
        if len(to_names) != len(receivers):
            to_names = None  # 数量不匹配则忽略

    smtp_host = os.getenv(prefix + "SMTP_HOST", "smtp.qq.com")
    smtp_port = int(os.getenv(prefix + "SMTP_PORT", "465") or 465)
    use_ssl = (os.getenv(prefix + "USE_SSL", "1").strip().lower() in {"1", "true", "yes", "on"})

    timeout_env = os.getenv(prefix + "TIMEOUT", "").strip()
    timeout = float(timeout_env) if timeout_env else None

    enable_exception_email(
        sender=sender,
        auth_code=auth_code,
        receivers=receivers,
        subject=subject,
        from_name=from_name,
        to_names=to_names,
        smtp_host=smtp_host,
        smtp_port=smtp_port,
        use_ssl=use_ssl,
        timeout=timeout,
    )
    return True


class EmailNotifier:
    """类似 logger 的邮件告警器类。

    通过实例初始化配置默认的邮件发送参数，可选自动注册未捕获异常钩子。
    使用场景：
        - 在项目入口 new 一个 EmailNotifier(enable_exception_hook=True)，当进程发生未捕获异常时自动发送邮件。
        - 在代码任意处调用 send/notify_exception 主动发送告警或异常详情。
    """

    def __init__(
        self,
        sender: str,
        auth_code: str,
        receivers: List[str],
        subject: str = "程序异常退出通知",
        from_name: Optional[str] = None,
        to_names: Optional[List[str]] = None,
        smtp_host: str = "smtp.qq.com",
        smtp_port: int = 465,
        use_ssl: bool = True,
        timeout: Optional[float] = None,
        enable_exception_hook: bool = True,
    ) -> None:
        """初始化邮件告警器并可选注册异常钩子。

        Args:
            sender: 发件邮箱。
            auth_code: 授权码/应用专用密码。
            receivers: 默认收件人列表。
            subject: 默认主题（异常通知时会使用）。
            from_name: 默认发件人显示名（可选）。
            to_names: 默认收件人显示名（可选），与 receivers 对齐。
            smtp_host: SMTP 服务器地址。
            smtp_port: SMTP 端口。
            use_ssl: 是否使用 SSL。
            timeout: 超时秒数。
            enable_exception_hook: 是否自动注册未捕获异常钩子。
        """
        if not receivers:
            raise ValueError("receivers 不能为空")

        self.sender = sender
        self.auth_code = auth_code
        self.receivers = receivers
        self.default_subject = subject
        self.from_name = from_name
        self.to_names = to_names

        self.mailer = EmailSender(
            sender=sender,
            auth_code=auth_code,
            smtp_host=smtp_host,
            smtp_port=smtp_port,
            use_ssl=use_ssl,
            timeout=timeout,
        )

        self._registered: bool = False
        self._original_excepthook = None

        if enable_exception_hook:
            self.enable_exception_hook()

    def enable_exception_hook(self) -> None:
        """注册全局未捕获异常钩子，以便自动发送异常告警邮件。"""
        if self._registered:
            return
        self._original_excepthook = sys.excepthook
        sys.excepthook = self._excepthook
        self._registered = True

    def disable_exception_hook(self) -> None:
        """取消已注册的异常钩子，恢复到原始 sys.excepthook。"""
        if not self._registered:
            return
        try:
            if sys.excepthook is self._excepthook and self._original_excepthook:
                sys.excepthook = self._original_excepthook
        finally:
            self._registered = False
            self._original_excepthook = None

    def send(
        self,
        content: str,
        subject: Optional[str] = None,
        receivers: Optional[List[str]] = None,
        from_name: Optional[str] = None,
        to_names: Optional[List[str]] = None,
    ) -> None:
        """主动发送一封邮件，未提供的参数使用实例初始化时的默认值。

        Args:
            content: 邮件正文（纯文本）。
            subject: 邮件主题，默认使用初始化的 subject。
            receivers: 收件人列表，默认使用初始化的 receivers。
            from_name: 发件人显示名，默认使用初始化的 from_name。
            to_names: 收件人显示名列表，默认使用初始化的 to_names。
        """
        sub = subject or self.default_subject
        tos = receivers or self.receivers
        fn = self.from_name if from_name is None else from_name
        tns = self.to_names if to_names is None else to_names
        self.mailer.send_text(
            receivers=tos,
            subject=sub,
            content=content,
            from_name=fn,
            to_names=tns,
        )

    def notify_exception(
        self,
        exc_info: Optional[tuple] = None,
        subject: Optional[str] = None,
        extra: Optional[str] = None,
    ) -> None:
        """根据异常信息构造正文并发送异常告警邮件。

        Args:
            exc_info: 一个 (etype, value, tb) 元组。若不提供，则使用 sys.exc_info()。
            subject: 覆盖默认主题（可选）。
            extra: 附加信息（可选），会追加到正文前部。
        """
        if exc_info is None:
            exc_info = sys.exc_info()
        etype, value, tb = exc_info
        trace_text = "".join(traceback.format_exception(etype, value, tb))
        parts = []
        if extra:
            parts.append(str(extra).rstrip() + "\n\n")
        parts.append("程序检测到未捕获异常并已自动告警。\n\n")
        parts.append(f"异常类型: {etype.__name__}\n")
        parts.append(f"异常信息: {value}\n\n")
        parts.append(f"堆栈: \n{trace_text}")
        body = "".join(parts)
        self.send(content=body, subject=subject)

    # 内部用：excepthook 代理
    def _excepthook(self, etype, value, tb):
        """作为 sys.excepthook 的代理，发送异常邮件后再调用原始钩子。"""
        try:
            self.notify_exception(exc_info=(etype, value, tb))
        except Exception:
            # 告警流程异常不影响原始异常处理
            pass
        finally:
            try:
                if self._original_excepthook:
                    self._original_excepthook(etype, value, tb)
            except Exception:
                pass