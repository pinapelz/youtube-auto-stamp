import pytchat
import time
import argparse
from currencies import CurrencyConv
import curses
import os


class StreamEndedError(Exception):
    pass

def main(stdscr, video_id: str, args: argparse.Namespace):
    curses.curs_set(0)
    height, width = stdscr.getmaxyx()
    max_num_messages = -(height-4) if args.max_messages is None else args.max_messages
    stdscr.nodelay(True)
    chat_window = curses.newwin(height - 4, width, 8, 0) 

    chat = pytchat.create(video_id=video_id)

    message_count = 0
    current_earnings_superchat_usd = 0.0
    membership_count = 0
    superchat_messages = []
    start_time = time.time()
    start_time_const = time.time()
    if args.earnings:
        currency_converter = CurrencyConv()

    try:
        while chat.is_alive():
            for chat_data in chat.get().sync_items():
                key = stdscr.getch()
                if key == ord('q'):
                    raise Exception("User ended data collection")
                if args.earnings and chat_data.amountValue != 0.0:
                    current_earnings_superchat_usd += currency_converter.convert(chat_data.amountValue, chat_data.currency, "USD")
                    superchat_messages.append((chat_data.author.name, chat_data.amountString, chat_data.message))

                if args.earnings and "Welcome New Member!" in chat_data.message:
                    superchat_messages.append((chat_data.author.name, "Membership", chat_data.message))
                    membership_count += 1
                
                message_count += 1

                elapsed_time = time.time() - start_time
                if elapsed_time >= 1:
                    stdscr.erase()
                    messages_per_second = message_count / elapsed_time
                    if args.track_moments > 0 and messages_per_second > args.track_moments:
                        stdscr.addstr(1, 0, "Message rate exceeded " + str(args.track_moments) + " at " + str(time.time()), curses.A_BLINK)
                        if not os.path.exists(f"{video_id}-moments.txt"):
                            open(f"{video_id}-moments.txt", "w").close()
                        with open(f"{video_id}-moments.txt", "a") as f:
                            timestamp = chat_data.timestamp
                            if args.start_time > 0:
                                timestamp = timestamp - args.start_time
                                timestamp = time.strftime("%H:%M:%S", time.gmtime(timestamp))
                                
                            f.write(f"Message rate exceeded {args.track_moments} per second at {chat_data.timestamp}\n")
                    messages_per_second_text = f"Messages per second: {messages_per_second:.2f}"
                    timestamp_since_start = time.strftime("%H:%M:%S", time.gmtime(time.time() - start_time_const))
                    info_msg = "Now collecting data for " + video_id + " Elapsed time: " + timestamp_since_start + " seconds (Press q to quit)"
                    chat_window_seperator_txt = "-" * width
                    stdscr.addstr(0, 0, info_msg, curses.A_BOLD)
                    stdscr.addstr(2, 0, messages_per_second_text)
                    stdscr.addstr(6, 0, chat_window_seperator_txt)

                    if args.earnings:
                        current_earnings_usd = current_earnings_superchat_usd + membership_count * args.membership
                        earnings_text = f"Current earnings (USD): {current_earnings_usd:.2f}"
                        membership_count_text = f"New/Renewing Members: {membership_count}"
                        stdscr.addstr(3, 0, earnings_text)
                        stdscr.addstr(4, 0, membership_count_text)

                    stdscr.refresh()
                    message_count = 0
                    start_time = time.time()

                # Update chat window
                chat_window.erase()
                for i, message in enumerate(superchat_messages[max_num_messages:]): 
                    chat_window.addstr(i, 0, f"{message[0]}: {message[1]} - {message[2]}")
                chat_window.refresh()

    except Exception as e:
        with open(f"{video_id}.txt", "w") as f:
            f.write(f"Data collection ended due to: {str(e)}\n")
            f.write(f"Messages per second: {messages_per_second:.2f}\n")
            if args.earnings:
                f.write(f"Current earnings (USD): {current_earnings_usd:.2f}\n")
                f.write(f"New/Renewing Members: {membership_count}\n")
                f.write("--- Logged Superchats ---\n")
                for message in superchat_messages:
                    f.write(f"{message[0]}: {message[1]} - {message[2]}\n")
        print("Saving data collected so far to " + f"{video_id}.txt")
        print(e)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='YouTube Live Chat Message Rate Tracker')
    parser.add_argument('video_id', help='The ID of the YouTube video for the live chat')
    parser.add_argument('--earnings', action='store_true', help='Show earnings through Superchats, Super Stickers, and Memberships')
    parser.add_argument('--membership', type=float, default=4.99, help='The amount of money a membership is worth')
    parser.add_argument('--track-moments', type=int, default=0, help='Log timestamps when the message rate exceeds this value')
    parser.add_argument('--max-messages', type=int, default=None, help="The maximum number of messages to collect")
    parser.add_argument('-start-time', type=int, default=0, help='The known UNIX timestamp of when the stream started (for calculating timestamps')
    args = parser.parse_args()
    curses.wrapper(main, args.video_id, args)
