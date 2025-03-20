from pathlib import Path

import aiofiles
import aiofiles.os
from fastapi import UploadFile

from core.config import settings


async def save_avatar(avatar: UploadFile, username: str) -> str:
    avatar_name = username + Path(avatar.filename).suffix
    avatar_path = settings.avatar.avatars_dir / avatar_name
    try:
        async with aiofiles.open(avatar_path, "wb") as file:
            content = await avatar.read()
            await file.write(content)
        return avatar_name
    except Exception:
        if await aiofiles.os.path.exists(avatar_path):
            await delete_avatar(avatar_name)
        raise


async def delete_avatar(avatar_name: str) -> None:
    avatar_path = settings.avatar.avatars_dir / avatar_name
    if await aiofiles.os.path.exists(avatar_path):
        await aiofiles.os.remove(avatar_path)
