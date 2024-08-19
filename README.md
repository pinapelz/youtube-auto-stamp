# YouTube Auto Stamp
A CLI program that tracks the speed of a YouTube live chat and records down moments of high chat activity. It can also count income via Superchats + find keywords in chat as a side task.

```
YouTube Live Chat Message Rate Tracker

positional arguments:
  video_id              The ID of the YouTube video for the live chat

options:
  -h, --help            show this help message and exit
  --show-chat           Show the live chat in the terminal window
  --superchats          Log superchat messages and amounts
  --threshold THRESHOLD
                        Log timestamps when the message rate exceeds this value (msg/s)
  --keywords KEYWORDS   Log timestamps when a message contains any of these keywords. Enter keywords separated by commas
  --cooldown COOLDOWN   Minimum time that must pass before another notable moment is logged (in seconds)

Example:
python yt_livechat_stats.py OoNndQzHMlI --show-chat --superchats --threshold 15 --cooldown 30
```
