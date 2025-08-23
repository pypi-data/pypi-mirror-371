import click
import time
import os
import platform
import json
import re

# We use a try-except block because this module only exists on Windows
try:
    import winsound
except ImportError:
    winsound = None

# --- Global Variables ---
log_file = "pomo_log.json"

# --- Helper Functions ---

def parse_duration(duration_str):
    """Parses a duration string (e.g., '30', '15s', '22m30s') into seconds."""
    if duration_str.isdigit():
        return int(duration_str) * 60

    parts = re.findall(r'(\d+)([ms])', duration_str)
    if not parts:
        click.echo(f"Warning: Invalid duration format '{duration_str}'. Defaulting to 25 minutes.")
        return 25 * 60

    total_seconds = 0
    for value, unit in parts:
        value = int(value)
        if unit == 'm':
            total_seconds += value * 60
        elif unit == 's':
            total_seconds += value
    return total_seconds

def play_alert_sound():
    """Plays a sound based on the user's operating system."""
    sound_file = 'ding.mp3'
    if not os.path.exists(sound_file):
        click.echo(f"\nWarning: Sound file '{sound_file}' not found. Place a sound file here for alerts.")
        return
    system = platform.system()
    try:
        if system == 'Darwin':
            os.system(f'afplay {sound_file} &')
        elif system == 'Windows':
            if winsound:
                winsound.PlaySound(sound_file, winsound.SND_FILENAME)
        elif system == 'Linux':
            os.system(f'aplay -q {sound_file} &')
    except Exception as e:
        click.echo(f"\nWarning: Could not play sound. Error: {e}")

def log_session(duration_seconds, description, tags):
    """Appends a completed session to the JSON log file."""
    logs = []
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            try:
                logs = json.load(f)
            except json.JSONDecodeError:
                logs = []
    logs.append({
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'duration_seconds': duration_seconds,
        'description': description,
        'tags': tags
    })
    with open(log_file, 'w') as f:
        json.dump(logs, f, indent=4)


# --- Main CLI Group ---
@click.group()
def cli():
    """A simple Pomodoro timer CLI."""
    pass


# --- CLI Commands ---

@cli.command()
@click.argument('description', required=False, default="Work")
@click.option('--duration', '-d', default="25", type=str, help='Duration in format like "30", "15s", "22m30s".')
@click.option('--tags', '-t', default="", help='Comma-separated tags for the session.')
def start(duration, description, tags):
    """Starts a new Pomodoro session."""
    duration_seconds = parse_duration(duration)
    
    click.echo(f"Starting session: '{description}' 🧘")

    end_time = time.time() + duration_seconds
    
    while time.time() < end_time:
        remaining_seconds = int(end_time - time.time())
        remaining_seconds = max(0, remaining_seconds)

        progress_percentage = (duration_seconds - remaining_seconds) / duration_seconds
        bar_length = 20
        filled_length = int(bar_length * progress_percentage)
        bar = '🍅' * filled_length + '─' * (bar_length - filled_length)

        mins, secs = divmod(remaining_seconds, 60)
        time_string = f"{mins:02d}:{secs:02d}"
        
        display_line = f"  ⏳ {time_string} [{bar}]"
        click.echo(f"\r{display_line}   ", nl=False)
        
        time.sleep(0.2)
    
    final_bar = '🍅' * 20
    click.echo(f"\r  ⏳ 00:00 [{final_bar}]   ")

    final_message = f"\n🎉 Session '{description}' finished! Time for a short break. 🎉"
    click.echo(final_message)
    play_alert_sound()
    log_session(duration_seconds, description, tags)


@cli.command(name='break')
@click.option('--duration', '-d', default="5m", type=str, help='Duration in format like "15m", "5m", "30s".')
def break_timer(duration):
    """Starts a break session."""
    duration_seconds = parse_duration(duration)
    
    click.echo(f"Starting break. Time to relax! ☕")
    
    end_time = time.time() + duration_seconds
    
    while time.time() < end_time:
        remaining_seconds = int(end_time - time.time())
        remaining_seconds = max(0, remaining_seconds)
        
        # --- NEW: Progress bar logic for the break command ---
        progress_percentage = (duration_seconds - remaining_seconds) / duration_seconds
        bar_length = 20
        filled_length = int(bar_length * progress_percentage)
        bar = '☕' * filled_length + '─' * (bar_length - filled_length)
        
        mins, secs = divmod(remaining_seconds, 60)
        time_string = f"{mins:02d}:{secs:02d}"
        
        display_line = f"  ⏳ {time_string} [{bar}]"
        click.echo(f"\r{display_line}   ", nl=False)
        
        time.sleep(0.2)
        
    final_bar = '☕' * 20
    click.echo(f"\r  ⏳ 00:00 [{final_bar}]   ")
    
    final_message = "\n🎉 Break is over! Time to get back to it. 🎉"
    click.echo(final_message)
    play_alert_sound()


@cli.command()
@click.argument('query')
@click.pass_context
def repeat(ctx, query):
    """Repeats the last session matching the query in description or tags."""
    if not os.path.exists(log_file):
        click.echo("Log file not found. No sessions to repeat.")
        return
    with open(log_file, 'r') as f:
        try:
            logs = json.load(f)
        except json.JSONDecodeError:
            logs = []
    
    for session in reversed(logs):
        if query.lower() in session.get('description', '').lower() or \
           query.lower() in session.get('tags', '').lower():
            
            click.echo(f"Found last session: '{session['description']}' with tags '{session['tags']}'. Repeating.")
            seconds = session['duration_seconds']
            duration_str = f"{seconds}s"
            
            ctx.invoke(
                start,
                duration=duration_str,
                description=session['description'],
                tags=session['tags']
            )
            return

    click.echo(f"No past session found matching '{query}'.")

@cli.command()
def path():
    """Displays the path to the log file."""
    click.echo("Your log file is located at:")
    click.echo(os.path.abspath(log_file))

@cli.command()
@click.option('--all', '-a', is_flag=True, help="Show all log entries instead of the default last 10.")
@click.option('--number', '-n', default=10, type=int, help="Number of recent entries to show.")
def log(all, number):
    """Shows the pomodoro session history."""
    if not os.path.exists(log_file):
        click.echo("Log file not found. No history to show.")
        return
    with open(log_file, 'r') as f:
        try:
            logs = json.load(f)
        except json.JSONDecodeError:
            click.echo("Log file is empty or corrupt.")
            return
    if not logs:
        click.echo("No sessions logged yet.")
        return
    if not all:
        logs_to_show = logs[-number:]
    else:
        logs_to_show = logs
    click.echo(f"{'Timestamp':<20} {'Duration (sec)':<15} {'Description':<30} {'Tags'}")
    click.echo("-" * 80)
    for session in reversed(logs_to_show):
        timestamp = session.get('timestamp', 'N/A')
        duration_sec = session.get('duration_seconds', 0)
        description = session.get('description', 'N/A')
        tags = session.get('tags', '')
        click.echo(f"{timestamp:<20} {str(duration_sec):<15} {description:<30} {tags}")


if __name__ == '__main__':
    cli()