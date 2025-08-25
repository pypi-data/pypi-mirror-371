import asyncio
import logging
import time
from collections import deque
from typing import Optional

import click
import colorlog
import numpy as np
import sounddevice as sd

from xiaozhi_sdk import XiaoZhiWebsocket
from xiaozhi_sdk.config import INPUT_SERVER_AUDIO_SAMPLE_RATE

# 定义自定义日志级别
INFO1 = 21
INFO2 = 22
INFO3 = 23

# 添加自定义日志级别到logging模块
logging.addLevelName(INFO1, "INFO1")
logging.addLevelName(INFO2, "INFO2")
logging.addLevelName(INFO3, "INFO3")

# 为logger添加自定义方法
def info1(self, message, *args, **kwargs):
    if self.isEnabledFor(INFO1):
        self._log(INFO1, message, args, **kwargs)

def info2(self, message, *args, **kwargs):
    if self.isEnabledFor(INFO2):
        self._log(INFO2, message, args, **kwargs)

def info3(self, message, *args, **kwargs):
    if self.isEnabledFor(INFO3):
        self._log(INFO3, message, args, **kwargs)

# 将自定义方法添加到Logger类
logging.Logger.info1 = info1
logging.Logger.info2 = info2
logging.Logger.info3 = info3

# 配置彩色logging
handler = colorlog.StreamHandler()
handler.setFormatter(
    colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        log_colors={
            "DEBUG": "white",
            "INFO": "green",
            "INFO1": "green",
            "INFO2": "cyan",
            "INFO3": "blue",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red,bg_white",
        },
    )
)

logger = logging.getLogger("xiaozhi_sdk")
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

# 全局状态
input_audio_buffer: deque[bytes] = deque()
is_playing_audio = False
is_end = False


async def handle_message(message):
    """处理接收到的消息"""
    global is_end
    if message["type"] == "stt":
        logger.info1("message received: %s", message)
    elif message["type"] == "tts":
        logger.info2("message received: %s", message)
    elif message["type"] == "llm":
        logger.info3("message received: %s", message)
    else:
        logger.info("message received: %s", message)

    if message["type"] == "websocket" and message["state"] == "close":
        is_end = True


async def play_assistant_audio(audio_queue: deque[bytes], enable_audio):
    """播放音频流"""
    global is_playing_audio

    stream = None
    if enable_audio:
        stream = sd.OutputStream(samplerate=INPUT_SERVER_AUDIO_SAMPLE_RATE, channels=1, dtype=np.int16)
        stream.start()
    last_audio_time = None

    while True:
        if is_end:
            return

        if not audio_queue:
            await asyncio.sleep(0.01)
            if last_audio_time and time.time() - last_audio_time > 1:
                is_playing_audio = False
            continue

        is_playing_audio = True
        pcm_data = audio_queue.popleft()
        if stream:
            stream.write(pcm_data)
        last_audio_time = time.time()


class XiaoZhiClient:
    """小智客户端类"""

    def __init__(
        self,
        url: Optional[str] = None,
        ota_url: Optional[str] = None,
    ):
        self.xiaozhi: Optional[XiaoZhiWebsocket] = None
        self.url = url
        self.ota_url = ota_url
        self.mac_address = ""

    async def start(self, mac_address: str, serial_number: str, license_key: str, enable_audio):
        """启动客户端连接"""
        self.mac_address = mac_address
        self.xiaozhi = XiaoZhiWebsocket(handle_message, url=self.url, ota_url=self.ota_url, send_wake=True)

        await self.xiaozhi.init_connection(
            self.mac_address, aec=False, serial_number=serial_number, license_key=license_key
        )

        asyncio.create_task(play_assistant_audio(self.xiaozhi.output_audio_queue, enable_audio))

    def audio_callback(self, indata, frames, time, status):
        """音频输入回调函数"""
        pcm_data = (indata.flatten() * 32767).astype(np.int16).tobytes()
        input_audio_buffer.append(pcm_data)

    async def process_audio_input(self):
        """处理音频输入"""
        while True:

            if is_end:
                return

            if not input_audio_buffer:
                await asyncio.sleep(0.02)
                continue

            pcm_data = input_audio_buffer.popleft()
            if not is_playing_audio:
                await self.xiaozhi.send_audio(pcm_data)


async def run_client(mac_address: str, url: str, ota_url: str, serial_number: str, license_key: str, enable_audio: bool):
    """运行客户端的异步函数"""
    logger.debug("Recording... Press Ctrl+C to stop.")
    client = XiaoZhiClient(url, ota_url)
    await client.start(mac_address, serial_number, license_key, enable_audio)

    with sd.InputStream(callback=client.audio_callback, channels=1, samplerate=16000, blocksize=960):
        await client.process_audio_input()


@click.command()
@click.argument("mac_address")
@click.option("--url", help="服务端websocket地址")
@click.option("--ota_url", help="OTA地址")
@click.option("--serial_number", default="", help="设备的序列号")
@click.option("--license_key", default="", help="设备的授权密钥")
@click.option("--enable_audio", default=True, help="是否开启音频播放")
def main(mac_address: str, url: str, ota_url: str, serial_number: str, license_key: str, enable_audio: bool):
    """小智SDK客户端

    MAC_ADDRESS: 设备的MAC地址 (格式: XX:XX:XX:XX:XX:XX)
    """
    asyncio.run(run_client(mac_address, url, ota_url, serial_number, license_key, enable_audio))
