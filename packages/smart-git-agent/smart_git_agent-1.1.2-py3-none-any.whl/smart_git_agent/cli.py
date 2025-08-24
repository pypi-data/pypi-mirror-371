import argparse
import logging
import time
import os
from watchdog.observers import Observer
from .smart_git_agent import SmartGitAgent
from .config_manager import load_config, create_default_config
from .file_utils import FileUtils
from git import Repo

try:
    import keyboard

    keyboard_available = True
except ImportError:
    keyboard_available = False
    logger = logging.getLogger(__name__)
    logger.warning("⚠️ Keyboard library not available. Manual commit triggering disabled.")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def setup_command(repo_path: str, config_path: str):
    """Create initial configuration file and ensure it's never tracked."""
    config_path = os.path.join(repo_path, config_path)
    if not os.path.exists(config_path):
        create_default_config(config_path)

        # Initialize FileUtils to ensure config file is ignored
        config = load_config(config_path)
        file_utils = FileUtils(repo_path, config)
        file_utils.ensure_config_file_ignored(config_path)

        # Create initial commit if repository is empty
        repo = Repo(repo_path)
        if file_utils.is_empty_repository(repo):
            file_utils.create_initial_commit(repo)
    else:
        logger.info(f"Configuration file already exists at {config_path}")


def run_agent(repo_path: str, config_path: str, dry_run: bool):
    """Run the smart git agent."""
    config_path = os.path.join(repo_path, config_path)
    config = load_config(config_path)
    if dry_run:
        config['dry_run'] = True

    if not config['openrouter_api_key'] or config['openrouter_api_key'] == 'YOUR_API_KEY_HERE':
        logger.error("❌ OpenRouter API key missing. Use --setup to create config file")
        return

    # Initialize FileUtils
    file_utils = FileUtils(repo_path, config)

    # Check for sensitive data in history
    if file_utils.check_for_sensitive_data_in_history():
        logger.error("🚨 Sensitive data detected in Git history. Please run clean_history.py to remove it.")
        return

    # Start agent
    event_handler = SmartGitAgent(repo_path, config)
    observer = Observer()
    observer.schedule(event_handler, repo_path, recursive=True)
    observer.start()

    logger.info(f"👀 🤖 Smart Git AI Agent active on {repo_path}")
    logger.info(f"🌍 Language: {config['language']} | 🚀 Model: {config['model']}")
    if keyboard_available:
        logger.info("Press 'p' to commit and push, or Ctrl+C to stop")
    else:
        logger.info("Running without keyboard input; relying on file system events")

    try:
        while True:
            if keyboard_available and keyboard.is_pressed('p'):
                logger.info("🛠️ Manual commit and push triggered by 'p' key")
                event_handler.commit_and_push()
                time.sleep(0.5)  # Debounce to prevent multiple rapid presses
            time.sleep(0.1)
    except KeyboardInterrupt:
        logger.info("🛑 Stopping agent...")
        observer.stop()
    observer.join()


def main():
    """Main entry point for the Smart Git Agent CLI."""
    parser = argparse.ArgumentParser(description="🤖 Smart Git AI Agent - Intelligent commits with emojis")
    parser.add_argument('--repo', default='.', help='Path to Git repository')
    parser.add_argument('--config', default='git-agent-config.ini', help='Configuration file path')
    parser.add_argument('--setup', action='store_true', help='Create default configuration file')
    parser.add_argument('--dry-run', action='store_true', help='Simulate commits without making changes')

    args = parser.parse_args()

    repo_path = os.path.abspath(args.repo)

    # Validate Git repository
    if not os.path.isdir(os.path.join(repo_path, '.git')):
        logger.error("❌ Specified path is not a Git repository")
        return

    if args.setup:
        setup_command(repo_path, args.config)
    else:
        config_path = os.path.join(repo_path, args.config)
        if not os.path.exists(config_path):
            logger.error("❌ Configuration file not found. Run with --setup to create one.")
            return
        run_agent(repo_path, args.config, args.dry_run)


if __name__ == "__main__":
    main()