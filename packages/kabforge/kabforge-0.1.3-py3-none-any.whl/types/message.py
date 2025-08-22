from __future__ import annotations
from typing import Optional, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import Bot


class Message:
    def __init__(self, data: Dict[str, Any], bot: Optional["Bot"] = None):
        self._data: Dict[str, Any] = data
        self.bot: Optional["Bot"] = bot

        self.from_user: Optional[Dict[str, Any]] = data.get("from", {}) or data.get("from_user", {})
        self.user_id: Optional[int] = self.from_user.get("id") if self.from_user else None
        self.username: Optional[str] = self.from_user.get("username") if self.from_user else None
        self.first_name: Optional[str] = self.from_user.get("first_name") if self.from_user else None
        self.last_name: Optional[str] = self.from_user.get("last_name") if self.from_user else None

        chat: Dict[str, Any] = data.get("chat", {}) or {}
        self.chat_id: Optional[int] = chat.get("id")
        self.chat_type: Optional[str] = chat.get("type")

        self.message_id: Optional[int] = data.get("message_id")
        self.text: Optional[str] = data.get("text")
        self.sticker: Optional[Dict[str, Any]] = data.get("sticker")
        self.photo: Optional[list[Dict[str, Any]]] = data.get("photo")
        self.document: Optional[Dict[str, Any]] = data.get("document")
        self.audio: Optional[Dict[str, Any]] = data.get("audio")
        self.video: Optional[Dict[str, Any]] = data.get("video")
        self.voice: Optional[Dict[str, Any]] = data.get("voice")
        self.caption: Optional[str] = data.get("caption")

    async def answer(
        self,
        text: str,
        reply_markup: Optional[Dict[str, Any]] = None,
        parse_mode: Optional[str] = None,
        disable_notification: Optional[bool] = None,
    ) -> Any:
        if not self.bot:
            raise RuntimeError("Bot instance is not attached to Message")

        return await self.bot.send_message(
            chat_id=self.chat_id,
            text=text,
            reply_markup=reply_markup,
            parse_mode=parse_mode,
            disable_notification=disable_notification,
        )
    
    async def test(self):
        await self.bot.send_message(chat_id=self.chat_id, text="Эмиль пидарас")

    @property
    def is_text(self) -> bool:
        return self.text is not None

    @property
    def is_sticker(self) -> bool:
        return self.sticker is not None

    @property
    def is_photo(self) -> bool:
        return bool(self.photo)

    @property
    def is_document(self) -> bool:
        return self.document is not None

    @property
    def is_media(self) -> bool:
        return any([self.photo, self.document, self.video, self.audio, self.voice])

    @property
    def update(self) -> Dict[str, Any]:
        return self._data
