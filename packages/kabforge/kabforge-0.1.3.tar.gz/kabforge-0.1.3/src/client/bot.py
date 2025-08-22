import httpx
import json

from typing import Dict, Any, Optional, Union

from ..core import BASE_URL
from ..utils import TelegramAPIError


class Bot:
    def __init__(self, token: str):
        self.token = token
        self.url = f"{BASE_URL}/bot{self.token}"
        self.session = httpx.AsyncClient()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

    async def close(self):
        await self.session.aclose()

    def _filter_payload(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {k: v for k, v in data.items() if v is not None}

    async def post_query(
        self,
        endpoint: str,
        payload: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None
    ) -> Any:
        url = f"{self.url}/{endpoint}"
        payload = self._filter_payload(payload or {})

        try:
            if files:
                response = await self.session.post(url, data=payload, files=files)
            else:
                response = await self.session.post(url, json=payload)

            response.raise_for_status()
            data = response.json()
        except httpx.RequestError as e:
            raise TelegramAPIError("Network error", 500, {"details": str(e)})
        except httpx.HTTPStatusError as e:
            raise TelegramAPIError("Invalid HTTP status", e.response.status_code)

        if not data.get("ok", True):
            raise TelegramAPIError(
                description=data.get("description", "Unknown error"),
                error_code=data.get("error_code", -1),
                parameters=data.get("parameters"),
            )

        return data["result"]

    async def get_me(self) -> Any:
        return await self.post_query("getMe")

    async def get_updates(self, offset: Optional[int] = None, timeout: int = 10) -> Any:
        return await self.post_query("getUpdates", {
            "offset": offset,
            "timeout": timeout,
        })

    async def send_message(
        self,
        chat_id: Union[int, str],
        text: str,
        parse_mode: Optional[str] = None,
        disable_web_page_preview: Optional[bool] = None,
        disable_notification: Optional[bool] = None,
        reply_to_message_id: Optional[int] = None,
        reply_markup: Optional[Dict[str, Any]] = None,
    ) -> Any:
        return await self.post_query("sendMessage", {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": disable_web_page_preview,
            "disable_notification": disable_notification,
            "reply_to_message_id": reply_to_message_id,
            "reply_markup": reply_markup,
        })

    async def forward_message(
        self,
        chat_id: Union[int, str],
        from_chat_id: Union[int, str],
        message_id: int,
        disable_notification: Optional[bool] = None,
    ) -> Any:
        return await self.post_query("forwardMessage", {
            "chat_id": chat_id,
            "from_chat_id": from_chat_id,
            "message_id": message_id,
            "disable_notification": disable_notification,
        })

    async def copy_message(
        self,
        chat_id: Union[int, str],
        from_chat_id: Union[int, str],
        message_id: int,
        caption: Optional[str] = None,
        parse_mode: Optional[str] = None,
        disable_notification: Optional[bool] = None,
    ) -> Any:
        return await self.post_query("copyMessage", {
            "chat_id": chat_id,
            "from_chat_id": from_chat_id,
            "message_id": message_id,
            "caption": caption,
            "parse_mode": parse_mode,
            "disable_notification": disable_notification,
        })

    async def send_photo(
        self,
        chat_id: Union[int, str],
        photo: Union[str, bytes],
        caption: Optional[str] = None,
        parse_mode: Optional[str] = None,
    ) -> Any:
        files = {"photo": photo} if isinstance(photo, bytes) else None
        payload = {
            "chat_id": chat_id,
            "caption": caption,
            "parse_mode": parse_mode,
        }
        if files:
            return await self.post_query("sendPhoto", payload, files)
        else:
            return await self.post_query("sendPhoto", {**payload, "photo": photo})

    async def send_document(
        self,
        chat_id: Union[int, str],
        document: Union[str, bytes],
        caption: Optional[str] = None,
        parse_mode: Optional[str] = None,
    ) -> Any:
        files = {"document": document} if isinstance(document, bytes) else None
        payload = {
            "chat_id": chat_id,
            "caption": caption,
            "parse_mode": parse_mode,
        }
        if files:
            return await self.post_query("sendDocument", payload, files)
        else:
            return await self.post_query("sendDocument", {**payload, "document": document})

    async def send_audio(
        self,
        chat_id: Union[int, str],
        audio: Union[str, bytes],
        caption: Optional[str] = None,
        parse_mode: Optional[str] = None,
    ) -> Any:
        files = {"audio": audio} if isinstance(audio, bytes) else None
        payload = {
            "chat_id": chat_id,
            "caption": caption,
            "parse_mode": parse_mode,
        }
        if files:
            return await self.post_query("sendAudio", payload, files)
        else:
            return await self.post_query("sendAudio", {**payload, "audio": audio})

    async def send_video(
        self,
        chat_id: Union[int, str],
        video: Union[str, bytes],
        caption: Optional[str] = None,
        parse_mode: Optional[str] = None,
    ) -> Any:
        files = {"video": video} if isinstance(video, bytes) else None
        payload = {
            "chat_id": chat_id,
            "caption": caption,
            "parse_mode": parse_mode,
        }
        if files:
            return await self.post_query("sendVideo", payload, files)
        else:
            return await self.post_query("sendVideo", {**payload, "video": video})

    async def send_voice(
        self,
        chat_id: Union[int, str],
        voice: Union[str, bytes],
        caption: Optional[str] = None,
        parse_mode: Optional[str] = None,
    ) -> Any:
        files = {"voice": voice} if isinstance(voice, bytes) else None
        payload = {
            "chat_id": chat_id,
            "caption": caption,
            "parse_mode": parse_mode,
        }
        if files:
            return await self.post_query("sendVoice", payload, files)
        else:
            return await self.post_query("sendVoice", {**payload, "voice": voice})

    async def send_poll(
        self,
        chat_id: Union[int, str],
        question: str,
        options: list[str],
        is_anonymous: Optional[bool] = None,
        type: Optional[str] = None,
        allows_multiple_answers: Optional[bool] = None,
    ) -> Any:
        return await self.post_query("sendPoll", {
            "chat_id": chat_id,
            "question": question,
            "options": json.dumps(options),
            "is_anonymous": is_anonymous,
            "type": type,
            "allows_multiple_answers": allows_multiple_answers,
        })

    async def answer_callback_query(
        self,
        callback_query_id: str,
        text: Optional[str] = None,
        show_alert: Optional[bool] = None,
        url: Optional[str] = None,
    ) -> Any:
        return await self.post_query("answerCallbackQuery", {
            "callback_query_id": callback_query_id,
            "text": text,
            "show_alert": show_alert,
            "url": url,
        })

    async def get_file(self, file_id: str) -> Any:
        return await self.post_query("getFile", {"file_id": file_id})

    async def delete_message(self, chat_id: Union[int, str], message_id: int) -> Any:
        return await self.post_query("deleteMessage", {
            "chat_id": chat_id,
            "message_id": message_id,
        })
