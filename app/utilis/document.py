import os
from typing import AsyncGenerator, List
import aiofiles
from fastapi import UploadFile
from pathlib import Path


from app.config import Config


class DocumentValidator:
    def __init__(self):
        self.allowedExtension = {".pdf"}
        self.maxSize = Config.MAX_FILE_SIZE

    async def validatefile(self, file: UploadFile) -> dict[str, List]:
        result = {"valid": True, "errors": []}

        if not file.filename or file.filename.strip() == "":
            result["valid"] = False
            result["errors"].append("No file selected")
            return result

        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in self.allowedExtension:
            result["valid"] = False
            result["errors"].append(
                f'File extension "{file_ext}" not allowed. Use: .pdf'
            )
            return result

        file.file.seek(0, os.SEEK_END)
        filesize = file.file.tell()
        file.file.seek(0)
        if filesize > self.maxSize:
            result["valid"] = False
            result["errors"].append(
                f"File too large ({filesize // (1024 * 1024)} MB). Maximum: {self.maxSize // (1024 * 1024)} MB"
            )
            return result
        return result


class DocumentStream:
    async def fileStreamer(self, filePath: Path) -> AsyncGenerator[bytes]:
        async with aiofiles.open(filePath, mode="rb") as file:
            chunkSize = 64 * 1024
            while chunk := await file.read(chunkSize):
                yield chunk

    async def rangeStreamer(
        self, filePath: Path, start: int, end: int
    ) -> AsyncGenerator[bytes]:
        async with aiofiles.open(filePath, mode="rb") as pages:
            await pages.seek(start)
            remainingChunk = end - start + 1
            chunkSize = 64 * 1024
            while chunk := await pages.read(min(chunkSize, remainingChunk)):
                yield chunk
                remainingChunk -= len(chunk)
