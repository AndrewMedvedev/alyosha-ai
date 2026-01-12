from uuid import UUID, uuid4

import magic

from .. import storage
from ..core import schemas
from ..database import crud, models


async def upload(user_id: int, filename: str, data: bytes) -> schemas.Attachment:
    file_id = uuid4()
    user_dir = storage.MEDIA_DIR / f"{user_id}"
    user_dir.mkdir(parents=True, exist_ok=True)
    filepath = user_dir / f"{file_id}.{filename.rsplit('.', maxsplit=1)[-1]}"
    mime_type = magic.from_buffer(data, mime=True)
    attachment = schemas.Attachment(
        id=file_id,
        uploaded_by=user_id,
        original_filename=filename,
        filepath=str(filepath),
        mime_type=mime_type,
        size=len(data),
    )
    file = schemas.File(
        path=str(filepath),
        size=len(data),
        mime_type=mime_type,
        data=data,
        uploaded_at=attachment.uploaded_at,
    )
    await storage.upload_file(file)
    await crud.create(attachment, model_class=models.Attachment)
    return attachment


async def download(file_id: UUID) -> schemas.File:
    attachment = await crud.read(
        file_id, model_class=models.Attachment, schema_class=schemas.Attachment
    )
    if attachment is None:
        raise ...
    return await storage.download_file(attachment.filepath)
