import pytchat
import time
import argparse
import curses
from text_renderer import TextRenderer
from data_writer import DataWriter
from vod_parser import VodParser
import yt_dlp
import os


class StreamEndedError(Exception):
    pass


def get_message_rate(message_count: int, last_refresh_time: time.time) -> tuple:
    if time.time() - last_refresh_time < 1:
        return "", None
    time_elapsed = time.time() - last_refresh_time
    last_refresh_time = time.time()
    message_rate_text = f"Messages per second: {message_count/time_elapsed:.5f}"
    message_data = message_rate_text, message_count/time_elapsed
    return message_data


def check_for_superchats(chat_data, data_writer: DataWriter):
    if chat_data.amountValue:
        data_writer.write(
            f"Superchat: {chat_data.amountValue} from {chat_data.author.name}\n")
        data_writer.write(f"Message: {chat_data.message}\n\n")


def get_video_info(video_id: str) -> dict:
    with yt_dlp.YoutubeDL() as ydl:
        info = ydl.extract_info(video_id, download=False)
        return info


def main(stdscr, video_id: str, args: argparse.Namespace):
    chat = pytchat.create(video_id=video_id)
    text_renderer = TextRenderer(stdscr)
    data_writer = DataWriter(f"{video_id}-analytics.txt")
    video_info = get_video_info(video_id)
    stream_start_unix_time = video_info["release_timestamp"]
    if not bool(video_info["is_live"]):
        vod_parser = VodParser(video_id, data_writer,
                               start_unix_time=stream_start_unix_time,
                               theshold=args.threshold,
                               cooldown=args.cooldown,
                               keywords=args.keywords)
        vod_parser.download_live_chat()
        vod_parser.parse_chat()
        vod_parser.clean_up()
        exit()
    if args.keywords:
        keywords = [keyword.strip() for keyword in args.keywords.split(",")]
    message_count = 0
    on_cooldown = False
    cooldown_start_time = time.time()
    start_time_const = time.time()
    last_refresh_time = time.time()

    try:
        while chat.is_alive():
            for chat_data in chat.get().sync_items():
                key = stdscr.getch()
                if key == ord('q'):
                    raise Exception("User ended data collection")
                timestamp_since_start = time.strftime(
                    "%H:%M:%S", time.gmtime(time.time() - start_time_const))
                info_msg = "Now collecting data for " + video_id + " Elapsed time: " + \
                    timestamp_since_start + " seconds (Press q to quit)"
                vid_info = f"Title: {video_info['title']} Channel: {video_info['uploader']} \nUnix Start Time: {stream_start_unix_time}"
                text_renderer.render(info_msg, y_pos=0)
                text_renderer.render(vid_info, y_pos=1)

                if on_cooldown and time.time() - cooldown_start_time > args.cooldown:
                    on_cooldown = False

                # Message Rate Related Features
                if time.time() - last_refresh_time > 1 and not on_cooldown:
                    message_rate_text, message_rate = get_message_rate(
                        message_count, last_refresh_time)
                    text_renderer.render(message_rate_text, y_pos=4)
                    last_refresh_time = time.time()
                    if message_rate > args.threshold:
                        diff_time_seconds = time.time() - stream_start_unix_time
                        youtube_timestamp = time.strftime(
                            "%H:%M:%S", time.gmtime(diff_time_seconds))
                        data_writer.write(
                            f"Notable moment found at {youtube_timestamp} measured at {message_rate}\n")
                        text_renderer.render(
                            f"Latest notable moment found at {youtube_timestamp} measured at {message_rate} - on cooldown until {time.time() + args.cooldown}\n", y_pos=5)
                        on_cooldown = True
                    message_count = 0
                else:
                    message_count += 1

                # Keyword related features
                if args.keywords:
                    for keyword in keywords:
                        if keyword.lower() in chat_data.message.lower():
                            diff_time_seconds = time.time() - stream_start_unix_time
                            youtube_timestamp = time.strftime(
                                "%H:%M:%S", time.gmtime(diff_time_seconds))
                            data_writer.write(
                                f"Keyword {keyword} found at {youtube_timestamp}\n")
                            text_renderer.render(
                                f"Keyword {keyword} found at {youtube_timestamp}\n", y_pos=6)
                            on_cooldown = True
                            cooldown_start_time = time.time()

                # Superchat Related Features (TODO)
                # if args.superchats:
                #    check_for_superchats(chat_data, data_writer)

                text_renderer.render(get_message_rate(
                    message_count, last_refresh_time)[0], y_pos=2)
                if args.show_chat:
                    text_renderer.log_message(
                        "[Chat]" + chat_data.author.name + ": " + chat_data.message)
                text_renderer.refresh()

    except Exception as e:
        data_writer.write(
            f"Data collection ended at {time.strftime('%H:%M:%S', time.gmtime(time.time() - stream_start_unix_time))} due to {e}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='YouTube Live Chat Message Rate Tracker')
    parser.add_argument(
        'video_id', help='The ID of the YouTube video for the live chat')
    parser.add_argument('--show-chat', action='store_true',
                        help='Show the live chat in the terminal window')
    parser.add_argument('--superchats', action='store_true',
                        help='Log superchat messages and amounts')
    parser.add_argument('--threshold', type=int, default=5,
                        help='Log timestamps when the message rate exceeds this value (msg/s)')
    parser.add_argument('--keywords', type=str,
                        help='Log timestamps when a message contains any of these keywords. Enter keywords separated by commas')
    parser.add_argument('--cooldown', type=int, default=20,
                        help='Minimum time that must pass before another notable moment is logged (in seconds)')
    args = parser.parse_args()
    if os.path.exists(f"{args.video_id}-analytics.txt"):
        if input(f"File {args.video_id}-analytics.txt already exists. Overwrite? (y/n): ").lower() != "y":
            print("Exiting...")
            exit()
    curses.wrapper(main, args.video_id, args)
