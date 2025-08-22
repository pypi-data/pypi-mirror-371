import asyncio
import aiohttp
import json
from typing import Dict
from ErisPulse import sdk
from ErisPulse.Core import router
from .Converter import TelegramConverter

class TelegramAdapter(sdk.BaseAdapter):
    class Send(sdk.BaseAdapter.Send):
        def Text(self, text: str):
            return asyncio.create_task(
                self._adapter.call_api(
                    endpoint="sendMessage",
                    chat_id=self._target_id,
                    text=text,
                    parse_mode=None
                )
            )

        def Markdown(self, text: str, content_type: str = "MarkdownV2"):
            return asyncio.create_task(
                self._adapter.call_api(
                    endpoint="sendMessage",
                    chat_id=self._target_id,
                    text=text,
                    parse_mode=content_type
                )
            )

        def Html(self, text: str, content_type: str = "HTML"):
            return asyncio.create_task(
                self._adapter.call_api(
                    endpoint="sendMessage",
                    chat_id=self._target_id,
                    text=text,
                    parse_mode=content_type
                )
            )

        def Image(self, file: bytes, caption: str = "", content_type: str = None):
            return asyncio.create_task(
                self._upload_file_and_call_api(
                    "sendPhoto",
                    field_name="photo",
                    file=file,
                    chat_id=self._target_id,
                    caption=caption,
                    parse_mode=content_type
                )
            )

        def Document(self, file: bytes, caption: str = "", content_type: str = None):
            return asyncio.create_task(
                self._upload_file_and_call_api(
                    "sendDocument",
                    field_name="document",
                    file=file,
                    chat_id=self._target_id,
                    caption=caption,
                    parse_mode=content_type
                )
            )

        def Video(self, file: bytes, caption: str = "", content_type: str = None):
            return asyncio.create_task(
                self._upload_file_and_call_api(
                    "sendVideo",
                    field_name="video",
                    file=file,
                    chat_id=self._target_id,
                    caption=caption,
                    parse_mode=content_type
                )
            )

        def Audio(self, file: bytes, caption: str = "", content_type: str = None):
            return asyncio.create_task(
                self._upload_file_and_call_api(
                    "sendAudio",
                    field_name="audio",
                    file=file,
                    chat_id=self._target_id,
                    caption=caption,
                    parse_mode=content_type
                )
            )

        def Edit(self, message_id: int, text: str, content_type: str = None):
            return asyncio.create_task(
                self._adapter.call_api(
                    endpoint="editMessageText",
                    chat_id=self._target_id,
                    message_id=message_id,
                    text=text,
                    parse_mode=content_type
                )
            )

        def Recall(self, message_id: int):
            return asyncio.create_task(
                self._adapter.call_api(
                    endpoint="deleteMessage",
                    chat_id=self._target_id,
                    message_id=message_id
                )
            )

        async def _upload_file_and_call_api(self, endpoint, field_name, file, **kwargs):
            # 将content_type转换为parse_mode以符合Telegram API
            if 'content_type' in kwargs:
                kwargs['parse_mode'] = kwargs.pop('content_type')
                
            url = f"{self._adapter.base_url}/{endpoint}"
            data = aiohttp.FormData()
            data.add_field(
                field_name,
                file,
                filename=f"file.{field_name}",
                content_type="application/octet-stream"
            )

            for key, value in kwargs.items():
                if isinstance(value, (dict, list)):
                    data.add_field(key, json.dumps(value))
                else:
                    data.add_field(key, str(value))

            async with self._adapter.session.post(url, data=data) as response:
                return await response.json()

    def __init__(self, sdk):
        super().__init__()
        self.sdk = sdk
        self.logger = sdk.logger
        self.config = self._load_config()
        self.token = self.config.get("token", "")
        self.session = None
        self.poll_task = None
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        self.last_update_id = 0
        self._setup_event_mapping()
        self._proxy_enabled = self.config.get("proxy_enabled", False)
        self._proxy_config = self.config.get("proxy", {}) if self._proxy_enabled else None
        self.convert = TelegramConverter(self.token).convert

    def _load_config(self):
        config = self.sdk.config.getConfig("Telegram_Adapter")
        if not config:
            default_config = {
                "token": "YOUR_BOT_TOKEN",
                "proxy_enabled": False,
                "proxy": {
                    "host": "127.0.0.1",
                    "port": 1080,
                    "type": "socks5"
                },
                "mode": "webhook",
                "webhook": {
                    "path": "/telegram/webhook",
                    "domain": None
                }
            }
            try:
                sdk.logger.warning("Telegram适配器配置不存在，已自动创建默认配置")
                self.sdk.config.setConfig("Telegram_Adapter", default_config)
                return default_config
            except Exception as e:
                self.logger.error(f"保存默认配置失败: {str(e)}")
                return default_config
        return config

    async def _process_webhook_event(self, data: Dict):
        try:
            if not isinstance(data, dict):
                raise ValueError("事件数据必须是字典类型")

            update_id = data.get("update_id")
            if update_id is None:
                raise ValueError("无效的Telegram事件数据")
            
            if hasattr(self.sdk, "adapter"):
                onebot_event = self.convert(data)
                self.logger.debug(f"OneBot12事件数据: {json.dumps(onebot_event, ensure_ascii=False)}")
                if onebot_event:
                    await self.sdk.adapter.emit(onebot_event)

        except Exception as e:
            self.logger.error(f"处理Telegram事件错误: {str(e)}")
            self.logger.debug(f"原始事件数据: {json.dumps(data, ensure_ascii=False)}")

    async def register_webhook(self):
        if not self.config.get("webhook"):
            self.logger.warning("Webhook配置不存在，将不会注册")
            return

        webhook_config = self.config["webhook"]
        path = webhook_config.get("path", "/telegram/webhook")

        router.register_http_route(
            "telegram",
            path,
            self._process_webhook_event,
            methods=["POST"]
        )

    async def set_webhook(self):
        webhook_config = self.config.get("webhook", {})
        path = webhook_config.get("path", "/telegram/webhook")
        
        # 获取服务器配置 兼容性处理
        server_config = self.sdk.config.get("ErisPulse", {}).get("server") or self.sdk.config.get("Server", {})
        
        # 优先使用webhook配置中的域名，其次使用server配置中的host
        domain = webhook_config.get("domain") or server_config.get("host", "localhost")
        port = server_config.get("port", 443)
        
        # 构造webhook URL
        webhook_url = f"https://{domain}:{port}/telegram{path}"
        self.logger.info(f"设置Telegram Webhook地址: {webhook_url}")

        return await self.call_api(
            "setWebhook",
            url=webhook_url,
            drop_pending_updates=True
        )

    async def delete_webhook(self):
        return await self.call_api("deleteWebhook")

    async def get_webhook_info(self):
        return await self.call_api("getWebhookInfo")
    
    async def _poll_updates(self):
        offset = 0
        while True:
            try:
                response = await self.call_api(
                    "getUpdates",
                    offset=offset,
                    timeout=60
                )
                
                # 检查API调用是否成功
                if response.get("status") != "ok":
                    self.logger.error(f"获取更新失败: {response.get('message')}")
                    await asyncio.sleep(5)
                    continue
                
                updates = response.get("data")
                
                if updates:
                    for update in updates:
                        update_id = update["update_id"]
                        if update_id >= offset:
                            offset = update_id + 1
                        
                        if hasattr(self.sdk, "adapter"):
                            onebot_event = self.convert(update)
                            self.logger.debug(f"OneBot12事件数据: {json.dumps(onebot_event, ensure_ascii=False)}")
                            if onebot_event:
                                await self.sdk.adapter.emit(onebot_event)
                await asyncio.sleep(1)
            except Exception as e:
                self.logger.error(f"轮询更新失败: {e}")
                await asyncio.sleep(5)

    async def call_api(self, endpoint: str, **params):
        url = f"{self.base_url}/{endpoint}"
        try:
            async with self.session.post(url, json=params) as response:
                raw_response = await response.json()
                
                self.logger.debug(f"Telegram API请求: {url}")
                self.logger.debug(f"Telegram API响应: {raw_response}")
                
                # 检查响应是否为预期的字典格式
                if not isinstance(raw_response, dict):
                    self.logger.error(f"Telegram API 返回了意外的响应格式: {type(raw_response)}, 内容: {raw_response}")
                    return {
                        "status": "failed",
                        "retcode": 34000,
                        "data": None,
                        "message_id": "",
                        "message": f"API 返回了意外格式: {type(raw_response)}",
                        "telegram_raw": raw_response,
                        "echo": params.get("echo", "")
                    }
                
                # 构建标准化响应
                response_data = {
                    "status": "ok" if raw_response.get("ok") else "failed",
                    "retcode": 0 if raw_response.get("ok") else 34000,  # 34xxx 平台错误
                    "data": raw_response.get("result"),
                    "message_id": str(raw_response.get("result", {}).get("message_id", "") if isinstance(raw_response.get("result"), dict) else ""),
                    "message": "" if raw_response.get("ok") else raw_response.get("description", "Unknown Telegram API error"),
                    "telegram_raw": raw_response
                }
                
                # 处理echo字段
                if "echo" in params:
                    response_data["echo"] = params["echo"]
                    
                return response_data
                
        except Exception as e:
            self.logger.error(f"调用Telegram API失败: {str(e)}")
            return {
                "status": "failed",
                "retcode": 33001,  # 网络错误
                "data": None,
                "message_id": "",
                "message": f"API调用失败: {str(e)}",
                "telegram_raw": None,
                "echo": params.get("echo", "")
            }
        
    async def start(self):
        import ssl
        import certifi
        from aiohttp_socks import ProxyType, ProxyConnector

        # 初始化会话
        if self._proxy_enabled and self._proxy_config:
            proxy_type = self._proxy_config.get("type")
            if proxy_type in ["socks5", "socks4"]:
                proxy_type_enum = ProxyType.SOCKS5 if proxy_type == "socks5" else ProxyType.SOCKS4
                ssl_context = ssl.create_default_context(cafile=certifi.where())
                connector = ProxyConnector(
                    proxy_type=proxy_type_enum,
                    host=self._proxy_config["host"],
                    port=self._proxy_config["port"],
                    ssl=ssl_context
                )
                self.session = aiohttp.ClientSession(connector=connector)
                self.logger.info(f"已启用{proxy_type.upper()}代理: {self._proxy_config['host']}:{self._proxy_config['port']}")
            else:
                self.logger.warning(f"不支持的代理类型: {proxy_type}, 将不使用代理")
                self.session = aiohttp.ClientSession()
        else:
            self.session = aiohttp.ClientSession()
            if self._proxy_enabled:
                self.logger.warning("代理已启用但未配置，将不使用代理")

        # 根据模式启动
        if self.config.get("mode") == "webhook":
            # 注册webhook路由
            await self.register_webhook()
            await self.set_webhook()
        elif self.config.get("mode") == "polling":
            self.poll_task = asyncio.create_task(self._poll_updates())
        else:
            self.logger.warning("未配置启动模式，请设置 mode 为 webhook 或 polling")

    async def shutdown(self):
        if self.poll_task:
            self.poll_task.cancel()
            try:
                await self.poll_task
            except asyncio.CancelledError:
                pass
            self.poll_task = None

        if self.config.get("mode") == "webhook":
            await self.delete_webhook()

        if self.session:
            await self.session.close()
            self.session = None

        self.logger.info("Telegram适配器已关闭")