import os
import json
from collections import defaultdict
from datetime import datetime

LIVE_CHAT_RENDERERS = ["liveChatViewerEngagementMessageRenderer", "liveChatTextMessageRenderer"]

class VodParser:
    def __init__(self, video_id: str, data_writer, theshold: int = 1, cooldown: float = 5, keywords: list = [], start_unix_time: int = 0):
        self.video_id = video_id
        self._chat_file = f"{self.video_id}.live_chat.json"
        self._threshold = theshold
        self._cooldown = cooldown
        self._keywords = keywords
        self._start_unix_time = start_unix_time
        self.data_writer = data_writer

    def download_live_chat(self):
        if os.path.exists(f"{self.video_id}.live_chat.json"):
            os.remove(f"{self.video_id}.live_chat.json")
        os.system(f"yt-dlp {self.video_id} --skip-download -o '%(id)s' --write-sub --")
        self._chat_file = f"{self.video_id}.live_chat.json"
    
    def clean_up(self):
        os.remove(f"{self.video_id}.live_chat.json")
    
    
    def parse_chat(self):
        message_count_buffer = 0
        last_refresh_time = 0
        with open(self._chat_file, "r") as ndjson_file:
            for line in ndjson_file:
                chat_data = json.loads(line)
                for renderer in LIVE_CHAT_RENDERERS:
                    try:
                        timestamp_usec = chat_data["replayChatItemAction"]["actions"][0]["addChatItemAction"]["item"][renderer]["timestampUsec"]
                        unix_timestamp = int(timestamp_usec) / 1000000

                        if last_refresh_time == 0 or unix_timestamp < last_refresh_time:
                            last_refresh_time = unix_timestamp
                            message_count_buffer += 1
                            continue
                            
                        if unix_timestamp - last_refresh_time > self._cooldown:
                            message_rate = message_count_buffer / (unix_timestamp - last_refresh_time)
                            if message_rate > self._threshold:
                                print(f"Message rate exceeded threshold: {message_rate} messages per second")
                                seconds_since_start_of_stream = unix_timestamp - self._start_unix_time
                                youtube_timestamp = datetime.utcfromtimestamp(seconds_since_start_of_stream).strftime('%H:%M:%S')
                                print(f"Timestamp: {youtube_timestamp}")
                                self.data_writer.write(f"Notable moment found at {youtube_timestamp}\n")


                            message_count_buffer = 0
                            last_refresh_time = unix_timestamp
                        message_count_buffer += 1
                        
                    except KeyError:
                        continue


if __name__ == "__main__":
    parser = VodParser("RsYA5heZSk8")
    parser.parse_chat()
