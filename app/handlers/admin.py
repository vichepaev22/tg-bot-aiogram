"""Administrative handlers for managing chat participants."""
from __future__ import annotations

import logging
from typing import Dict, Optional, Tuple

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.filters.command import CommandObject
from aiogram.types import Message
from aiogram.enums import ChatMemberStatus
from aiogram.exceptions import TelegramBadRequest

logger = logging.getLogger(__name__)

router = Router(name="admin")

# Cache of usernames observed by the bot during the current process lifetime.
_seen_users: Dict[Tuple[int, str], int] = {}


async def is_admin(message: Message, user_id: int, chat_id: int) -> bool:
    """Check whether the given user is an administrator or chat owner."""
    try:
        member = await message.bot.get_chat_member(chat_id=chat_id, user_id=user_id)
    except TelegramBadRequest:
        return False

    return member.status in {ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER}


async def can_bot_delete(message: Message, chat_id: int) -> bool:
    """Verify that the bot has permission to remove users from the chat."""
    try:
        me = await message.bot.me()
        member = await message.bot.get_chat_member(chat_id=chat_id, user_id=me.id)
    except TelegramBadRequest:
        return False

    if member.status != ChatMemberStatus.ADMINISTRATOR:
        return False

    return bool(getattr(member, "can_restrict_members", False))


def extract_target(message: Message, argument: Optional[str]) -> Tuple[Optional[int], Optional[str], Optional[str]]:
    """Extract a target user ID from the message context or provided argument."""
    if message.reply_to_message and message.reply_to_message.from_user:
        user = message.reply_to_message.from_user
        name_parts = [user.full_name]
        if user.username:
            name_parts.append(f"@{user.username}")
        return user.id, " ".join(name_parts), None

    if not argument:
        return None, None, "Команду нужно отправлять ответом на сообщение или указать ID/username."

    arg = argument.strip()
    if not arg:
        return None, None, "Команду нужно отправлять ответом на сообщение или указать ID/username."

    numeric = arg.lstrip("-")
    if numeric.isdigit():
        return int(arg), arg, None

    if arg.startswith("@"):
        username = arg[1:].strip()
        if not username:
            return None, None, "Команду нужно отправлять ответом на сообщение или указать ID/username."

        cached = _seen_users.get((message.chat.id, username.lower()))
        if cached is not None:
            return cached, f"@{username}", None

        return None, None, "Не нашёл пользователя по username; используйте ответ на сообщение или укажите числовой ID."

    return None, None, "Команду нужно отправлять ответом на сообщение или указать ID/username."


async def _process_delete(message: Message, argument: Optional[str]) -> None:
    """Shared deletion routine for commands and text triggers."""
    chat = message.chat
    initiator = message.from_user

    if not chat or not initiator:
        return

    chat_id = chat.id
    initiator_id = initiator.id

    if not await is_admin(message, initiator_id, chat_id):
        logger.warning(
            "User %s (%s) attempted to delete but is not an admin", initiator.full_name, initiator_id
        )
        await message.reply("❌ Только администраторы могут использовать эту команду.")
        return

    if not await can_bot_delete(message, chat_id):
        logger.warning(
            "Bot lacks delete permissions in chat %s (%s) for request from %s (%s)",
            chat.title,
            chat_id,
            initiator.full_name,
            initiator_id,
        )
        await message.reply(
            "❌ У бота нет прав удалять участников. Сделайте бота администратором с правом «Delete users»."
        )
        return

    target_user_id, target_label, error = extract_target(message, argument)
    if target_user_id is None:
        logger.warning(
            "Admin %s (%s) provided invalid target: %s", initiator.full_name, initiator_id, argument
        )
        await message.reply(f"❌ {error}")
        return

    me = await message.bot.me()
    if target_user_id == me.id:
        logger.warning(
            "Admin %s (%s) attempted to delete the bot in chat %s", initiator.full_name, initiator_id, chat_id
        )
        await message.reply("❌ Нельзя удалить бота.")
        return

    if target_user_id == initiator_id:
        logger.warning(
            "Admin %s (%s) attempted to delete themselves in chat %s", initiator.full_name, initiator_id, chat_id
        )
        await message.reply("❌ Нельзя удалить самого себя.")
        return

    try:
        target_member = await message.bot.get_chat_member(chat_id=chat_id, user_id=target_user_id)
    except TelegramBadRequest:
        logger.warning(
            "Admin %s (%s) attempted to delete unknown user %s in chat %s",
            initiator.full_name,
            initiator_id,
            argument or target_label or target_user_id,
            chat_id,
        )
        await message.reply("❌ Цель не найдена в чате.")
        return

    if target_member.status in {ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR}:
        logger.warning(
            "Admin %s (%s) attempted to delete administrator %s (%s)",
            initiator.full_name,
            initiator_id,
            target_member.user.full_name,
            target_member.user.id,
        )
        await message.reply("❌ Нельзя удалить владельца или администратора чата.")
        return

    display_name = target_member.user.full_name
    if target_member.user.username:
        display_name = f"{display_name} (@{target_member.user.username})"

    logger.info(
        "Admin %s (%s) is deleting user %s (%s) in chat %s",
        initiator.full_name,
        initiator_id,
        display_name,
        target_member.user.id,
        chat_id,
    )

    try:
        await message.bot.ban_chat_member(chat_id=chat_id, user_id=target_user_id)
        await message.bot.unban_chat_member(chat_id=chat_id, user_id=target_user_id, only_if_banned=True)
    except TelegramBadRequest as exc:
        logger.exception(
            "Failed to delete user %s (%s) requested by %s (%s)",
            target_member.user.full_name,
            target_member.user.id,
            initiator.full_name,
            initiator_id,
        )
        await message.reply(f"❌ Не удалось удалить пользователя: {exc}")
        return

    logger.info(
        "User %s (%s) removed by %s (%s) in chat %s",
        target_member.user.full_name,
        target_member.user.id,
        initiator.full_name,
        initiator_id,
        chat_id,
    )
    await message.reply(f"✅ Пользователь удалён: {display_name}")


@router.message(Command(commands=["delete", "kick"]))
async def handle_delete_command(message: Message, command: CommandObject) -> None:
    """Handle /delete and /kick commands."""
    await _process_delete(message, command.args)


@router.message(F.text.regexp(r"(?i)^delete\b"))
async def handle_delete_text(message: Message) -> None:
    """Handle text commands that start with "Delete"."""
    argument: Optional[str] = None
    if message.text:
        parts = message.text.split(maxsplit=1)
        if len(parts) > 1:
            argument = parts[1]
    await _process_delete(message, argument)


@router.message(priority=-100)
async def cache_usernames(message: Message) -> None:
    """Remember usernames observed in the chat for later lookups."""
    if not message.chat or not message.from_user or not message.from_user.username:
        return

    username = message.from_user.username.lower()
    _seen_users[(message.chat.id, username)] = message.from_user.id

    logger.debug(
        "Cached username @%s -> %s for chat %s",
        message.from_user.username,
        message.from_user.id,
        message.chat.id,
    )
