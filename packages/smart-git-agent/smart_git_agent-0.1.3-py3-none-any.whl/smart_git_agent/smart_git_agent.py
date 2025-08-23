import time
import logging
import os
import re
from git import Repo
from watchdog.events import FileSystemEventHandler
from .commit_analyzer import CommitAnalyzer
from .file_utils import FileUtils
try:
    import keyboard
    keyboard_available = True
except ImportError:
    keyboard_available = False
    logger = logging.getLogger(__name__)
    logger.warning("⚠️ Keyboard library not available. Manual commit triggering disabled.")

logger = logging.getLogger(__name__)

class SmartGitAgent(FileSystemEventHandler):
    def __init__(self, repo_path: str, config: dict):
        self.repo_path = repo_path
        self.config = config
        self.repo = Repo(repo_path)
        self.last_commit_time = time.time()
        self.file_utils = FileUtils(repo_path, config)
        self.commit_analyzer = CommitAnalyzer(config, self.file_utils)
        self.dry_run = config.get('dry_run', False)

    def on_any_event(self, event):
        """Handle file system events."""
        if (event.is_directory or
                '.git' in event.src_path or
                self.file_utils.should_ignore_file(event.src_path)):
            return

        current_time = time.time()
        if current_time - self.last_commit_time < self.config.get('debounce_time', 10):
            return

        self.last_commit_time = current_time
        self.process_changes()

    def _check_index_lock(self, max_retries=3, delay=5):
        """Check for index.lock file and retry if it exists."""
        lock_file = os.path.join(self.repo_path, '.git', 'index.lock')
        for attempt in range(max_retries):
            if not os.path.exists(lock_file):
                return True
            logger.warning(
                f"⚠️ Git index.lock detected at '{lock_file}'. Retrying in {delay} seconds... (Attempt {attempt + 1}/{max_retries})")
            time.sleep(delay)
        logger.error(
            f"❌ Failed to obtain index lock after {max_retries} attempts. Please ensure no other Git processes are running and delete '{lock_file}' if stale.")
        return False

    def _contains_sensitive_data(self, file_path: str) -> bool:
        """Check if a file contains sensitive data like API keys or tokens and log matches for testing."""
        ignored_files = ["smart_git_agent.py"]

        if any(file_path.endswith(ignored) for ignored in ignored_files):
            return False

        sensitive_patterns = [
            # 🔑 Clés API et tokens génériques
            r'api[_-]?key\s*=\s*[\'"].+[\'"]',
            r'token\s*=\s*[\'"].+[\'"]',
            r'secret\s*=\s*[\'"].+[\'"]',
            r'password\s*=\s*[\'"].+[\'"]',
            r'passwd\s*=\s*[\'"].+[\'"]',
            r'pwd\s*=\s*[\'"].+[\'"]',
            r'auth[_-]?token\s*=\s*[\'"].+[\'"]',
            r'access[_-]?token\s*=\s*[\'"].+[\'"]',
            r'refresh[_-]?token\s*=\s*[\'"].+[\'"]',

            # 🔒 Variantes majuscules/minuscules
            r'API[_-]?KEY\s*=\s*[\'"].+[\'"]',
            r'API[_-]?TOKEN\s*=\s*[\'"].+[\'"]',
            r'AUTH[_-]?TOKEN\s*=\s*[\'"].+[\'"]',
            r'SECRET[_-]?KEY\s*=\s*[\'"].+[\'"]',
            r'CLIENT[_-]?SECRET\s*=\s*[\'"].+[\'"]',

            # ☁️ Fournisseurs cloud (AWS, Google, Azure…)
            r'AWS_ACCESS_KEY_ID\s*=\s*[\'"][A-Z0-9]{20}[\'"]',
            r'AWS_SECRET_ACCESS_KEY\s*=\s*[\'"][A-Za-z0-9/+=]{40}[\'"]',
            r'GOOGLE_API_KEY\s*=\s*[\'"].+[\'"]',
            r'AZURE_CLIENT_SECRET\s*=\s*[\'"].+[\'"]',
            r'OPENAI_API_KEY\s*=\s*[\'"].+[\'"]',
            r'OPENROUTER_API_KEY\s*=\s*[\'"].+[\'"]',

            # 📧 Identifiants sensibles (mails/mot de passe DB)
            r'DB[_-]?PASSWORD\s*=\s*[\'"].+[\'"]',
            r'DATABASE[_-]?URL\s*=\s*[\'"].+[\'"]',
            r'EMAIL[_-]?PASSWORD\s*=\s*[\'"].+[\'"]',

            # 🔐 Certificats / Clés privées (construits dynamiquement pour éviter faux positifs)
            r'-----BEGIN ' + r'PRIVATE KEY' + r'-----',
            r'-----BEGIN ' + r'RSA PRIVATE KEY' + r'-----',
            r'-----BEGIN ' + r'DSA PRIVATE KEY' + r'-----',
            r'-----BEGIN ' + r'EC PRIVATE KEY' + r'-----',
            r'-----BEGIN ' + r'OPENSSH PRIVATE KEY' + r'-----',
        ]

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.splitlines()
                found_sensitive = False
                for pattern in sensitive_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        found_sensitive = True
                        match_start = match.start()
                        line_number = content[:match_start].count('\n') + 1
                        line_content = lines[line_number - 1].strip()
                        logger.warning(f"🚫 Sensitive data detected in {file_path} at line {line_number}: {line_content} (Pattern: {pattern})")
                if found_sensitive:
                    return True
        except (OSError, IOError) as e:
            logger.debug(f"Could not read file {file_path} for sensitive data check: {e}")
        return False

    def commit_and_push(self):
        """Perform commit and push operations."""
        try:
            # Check for index.lock before proceeding
            if not self._check_index_lock():
                return

            branch_name = self.config.get('branch', 'main')

            if self.dry_run:
                logger.info("🧪 Dry-run mode: Simulating commit and push")
                analysis = self.commit_analyzer.analyze_changes(self.repo)
                commit_message = self.commit_analyzer.generate_smart_commit_message(analysis)
                logger.info(f"📝 Simulated commit message: {commit_message}")
                return

            # Check if branch exists, create if it doesn't
            try:
                if branch_name not in self.repo.heads:
                    logger.info(f"🌿 Branch '{branch_name}' does not exist. Creating it...")
                    # Use parent_branch from config if specified, otherwise use HEAD
                    parent_branch = self.config.get('parent_branch', 'HEAD')
                    self.repo.create_head(branch_name, parent_branch)
                    logger.info(f"✅ Created branch '{branch_name}' from '{parent_branch}'")
                # Checkout the branch
                self.repo.heads[branch_name].checkout()
            except Exception as e:
                logger.error(f"❌ Error creating or checking out branch '{branch_name}': {e}")
                return

            # Add non-ignored files
            sensitive_files = []
            for file_path in self.repo.untracked_files:
                full_path = os.path.join(self.repo_path, file_path)
                if not self.file_utils.should_ignore_file(full_path):
                    if self._contains_sensitive_data(full_path):
                        sensitive_files.append(file_path)
                    else:
                        self.repo.index.add([file_path])

            # Add modified files
            modified_files = [item.a_path for item in self.repo.index.diff(None)]
            for file_path in modified_files:
                full_path = os.path.join(self.repo_path, file_path)
                if not self.file_utils.should_ignore_file(full_path):
                    if self._contains_sensitive_data(full_path):
                        sensitive_files.append(file_path)
                    else:
                        self.repo.index.add([file_path])

            # Check for meaningful changes
            if not self.file_utils.has_meaningful_changes(self.repo):
                logger.info("ℹ️ No significant changes detected")
                return

            # Analyze and generate commit message
            analysis = self.commit_analyzer.analyze_changes(self.repo)
            commit_message = self.commit_analyzer.generate_smart_commit_message(analysis)

            # Commit
            self.repo.index.commit(commit_message)
            logger.info(f"✅ Commit: {commit_message}")

            # Update file hashes
            self.file_utils.update_file_hashes(self.repo)

            # Push if configured and no sensitive data
            if self.config.get('auto_push', True):
                if sensitive_files:
                    logger.warning(f"🚫 Push aborted: Sensitive data detected in {', '.join(sensitive_files)}")
                    return
                try:
                    origin = self.repo.remote(name='origin')
                    # Check if branch exists on remote
                    remote_branch = f"origin/{branch_name}"
                    if remote_branch not in [ref.name for ref in origin.refs]:
                        logger.info(f"🌍 Remote branch '{branch_name}' does not exist. Setting up tracking...")
                        origin.push(f"{branch_name}:{branch_name}")
                        self.repo.heads[branch_name].set_tracking_branch(origin.refs[branch_name])
                        logger.info(f"✅ Set up tracking for '{branch_name}' to '{remote_branch}'")
                    else:
                        origin.push(branch_name)
                    logger.info(f"📤 Pushed to {branch_name}")
                except Exception as e:
                    logger.error(f"Push error: {e}")

        except Exception as e:
            logger.error(f"Commit/push error: {e}")

    def process_changes(self):
        """Process detected changes."""
        self.commit_and_push()