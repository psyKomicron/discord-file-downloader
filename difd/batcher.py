import asyncio
import logging
import hashlib
import os
import aiofiles
import math
from config import HASH_FILENAMES, FILE_EXT_RE
from aiohttp import ClientSession, ClientTimeout
from console import shortPrint

class Batcher:
    logger = logging.getLogger(__name__)
    maxBatchCount: int
    batchSize: int
    _successRate: int = 0

    def __init__(self, batchSize: int, maxBatchCount: int) -> None:
        self.batchSize = batchSize
        self.maxBatchCount = maxBatchCount
        self.downloadFolderPath: str = None


    async def batch(self, urls: list[str]) -> int:
        urls = [*set(urls)] # Remove duplicated strings from the list.            
        if len(urls) > (self.batchSize * self.maxBatchCount):
            self.logger.debug(f"Trimming urls ({len(urls)} > {(self.batchSize * self.maxBatchCount)})")
            urls = urls[0:(self.batchSize * self.maxBatchCount)]
        else:
            self.logger.info(f"Starting download for {len(urls)} urls")
        downloadCount = 0
        for i in range(0, len(urls), self.batchSize):
            async with ClientSession(timeout=ClientTimeout(total=None)) as session:
                tasks = []
                upperBound = (i + self.batchSize) if (i + self.batchSize) < len(urls) else len(urls)
                for j in range(i, upperBound):
                    self.logger.debug(F"Downloading {shortPrint(urls[j], 50)}")
                    tasks.append(asyncio.create_task(self.download(urls[j], session)))
                self.logger.debug(f"Waiting for tasks {i}-{i + upperBound} to finish...")
                try:
                    futures = await asyncio.gather(*tasks)
                    for result in futures:
                        if result:
                            downloadCount += 1
                            self._successRate = downloadCount / len(urls)
                except* TimeoutError as ex:
                    self.logger.error("Timeout-ed while waiting for tasks to finish: ")
                    self.logger.error(ex)
                except* Exception as ex:
                    self.logger.error(f"While waiting for tasks to finish: {ex}")
                self.logger.info(f"Batch {math.ceil((i + 1) / self.batchSize)}/{math.ceil(len(urls) / self.batchSize)} done")
            if i > (self.batchSize * self.maxBatchCount):
                self.logger.warning(f"Reached cookies limit! Too many files downloaded ({i} > batchSize * maxBatchCount)")
            #successRate = "{:.2f}".format((downloadCount / len(urls)) * 100)
        self.logger.info(F"Finished downloading, success rate: {self._successRate * 100.0}% ({downloadCount}/{len(urls)})")
        return downloadCount

    async def download(self, url: str, session: ClientSession) -> bool:
        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    [name, ext] = self._getExt(url)
                    if name and ext:
                        #if DEBUG and ext != ".zip": return True
                        fileName = ""
                        if HASH_FILENAMES:
                            fileHash = hashlib.sha256(url.encode("utf-8")).hexdigest() + ext            
                            fileName = os.path.join(self.downloadFolderPath, fileHash)
                        else:
                            fileName = os.path.join(self.downloadFolderPath, name + ext)
                        if not os.path.exists(self.downloadFolderPath): 
                            self.logger.critical(f"Download folder '{self.downloadFolderPath}' does not exists")
                            return False
                        if os.path.exists(fileName):
                            self.logger.debug(f"{fileName} exists, not overwriting")
                            return True
                        # Create the file, write data into and close.
                        async with aiofiles.open(fileName, mode="xb") as fp:
                            dataSize = 0
                            while True:
                                [chunk, eof] = await resp.content.readchunk()
                                dataSize += await fp.write(chunk)
                                if eof or resp.content.at_eof(): break
                            self.logger.info(f"Downloaded {shortPrint(name + ext, 40)} ({dataSize} bytes)")
                        return True
        except Exception as ex:
            self.logger.critical(f"/!\\ Failed to download {url}")
            self.logger.error(ex)
            raise
        return False
    
    @property
    def successRate(self) -> float: return self._successRate    
    
    @property
    def downloadFolderPath(self) -> str: return self._download_folder_path

    @downloadFolderPath.setter
    def downloadFolderPath(self, value: str) -> None:
        self._download_folder_path = value

    def _getExt(self, url: str) -> tuple[str, str] | tuple[None, None]:
        index = 0
        for c in reversed(url):
            if c == '/':
                filePath = url[-index:]
                match = FILE_EXT_RE.search(filePath)
                if match:
                    ext = match[0]
                    fileName = filePath[:-len(ext)]
                    return (fileName, ext)
                break
            index += 1
        return (None, None)