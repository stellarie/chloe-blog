# Setting Up Automatic Blog Updates with systemd

This guide sets up hourly automatic updates of Chloe's blog from her diary entries.

## Files Included

- `update_blog.sh` — Script that copies new diary entries and regenerates the blog
- `chloe-blog.service` — systemd service unit
- `chloe-blog.timer` — systemd timer unit (hourly trigger)

## Installation

### 1. Make the update script executable

```bash
chmod +x /home/stella/chloe-blog/update_blog.sh
```

### 2. Install the systemd files (user level)

```bash
mkdir -p ~/.config/systemd/user
cp /home/stella/chloe-blog/chloe-blog.service ~/.config/systemd/user/
cp /home/stella/chloe-blog/chloe-blog.timer ~/.config/systemd/user/
```

### 3. Reload systemd and enable the timer

```bash
systemctl --user daemon-reload
systemctl --user enable chloe-blog.timer
systemctl --user start chloe-blog.timer
```

### 4. Check status

```bash
# Timer status
systemctl --user status chloe-blog.timer

# Service logs
journalctl --user -u chloe-blog.service -f
```

## How It Works

**Hourly (every hour):**
1. Timer triggers the service
2. Service runs `update_blog.sh`
3. Script:
   - Copies new diary entries from `/var/home/stella/notes/dev/Chloe/` to `source/`
   - Runs `generate_blog.py` to regenerate blog
   - Commits changes to git if any files changed
   - Pushes to Github

**Git Setup Requirement:**
- The script uses SSH to push (not HTTPS)
- Ensure your SSH key is set up and authenticated:
  ```bash
  eval $(ssh-agent -s)
  ssh-add ~/.ssh/id_rsa  # or your key
  ```

## Manual Trigger

To run the update manually:

```bash
/bin/bash /home/stella/chloe-blog/update_blog.sh
```

## Logs

View update logs:

```bash
journalctl --user -u chloe-blog.service
journalctl --user -u chloe-blog.timer
```

## Customizing the Schedule

Edit `chloe-blog.timer`:

```ini
[Timer]
# Change OnCalendar to run at different times:
OnCalendar=*-*-* 00:00:00   # Daily at midnight
OnCalendar=*-*-* *:00:00     # Every hour (current)
OnCalendar=*-*-* *:30:00     # Every hour at :30
OnCalendar=Mon..Fri 09:00    # Weekdays at 9am
```

Then reload:

```bash
systemctl --user daemon-reload
systemctl --user restart chloe-blog.timer
```

## Stopping/Disabling

```bash
systemctl --user stop chloe-blog.timer
systemctl --user disable chloe-blog.timer
```

## Troubleshooting

**Push fails with authentication errors:**
- Ensure SSH key is available: `ssh-add -l`
- Add to ssh-agent: `ssh-add ~/.ssh/id_rsa`

**No changes being committed:**
- Check diary directory exists: `ls /var/home/stella/notes/dev/Chloe/`
- Run script manually to see output: `/bin/bash /home/stella/chloe-blog/update_blog.sh`

**Timer not running:**
- Check: `systemctl --user status chloe-blog.timer`
- Enable: `systemctl --user enable chloe-blog.timer`
- Start: `systemctl --user start chloe-blog.timer`

## Notes

- Updates only happen if there are new diary entries
- Excludes `*memory*.md` files (too private)
- Randomized delay of up to 2 minutes to avoid network spikes
- Runs as user (not system-wide)
- Logs all activity to systemd journal
