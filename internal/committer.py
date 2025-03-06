import logging
import subprocess
from pathlib import Path
from internal.config import TildaConfig
from datetime import datetime

logger = logging.getLogger(__name__)


class Committer:
    def __init__(self, config: TildaConfig):
        self.config = config
        self.repo_path = Path('./' + config.base_path)

        self._init_repository()
        self._configure_credentials()
        self._set_remote()

    def _configure_credentials(self):
        """Настройка аутентификации для HTTPS"""
        if self.config.git_username and self.config.git_password:
            self._set_credential_helper()
            self._store_credentials()

    def _set_credential_helper(self):
        """Включаем сохранение учетных данных"""
        self._run_git_command(
            "config", "--global", "credential.helper", "store"
        )

    def _store_credentials(self):
        """Сохраняем учетные данные в файл"""
        credentials = f"https://{self.config.git_username}:{self.config.git_password}@{self._extract_domain()}"

        creds_file = Path.home() / ".git-credentials"
        with open(creds_file, "a") as f:
            f.write(credentials + "\n")

        # Устанавливаем безопасные права доступа
        creds_file.chmod(0o600)

    def _extract_domain(self):
        """Извлекаем домен из URL репозитория"""
        from urllib.parse import urlparse
        parsed = urlparse(self.config.git_remote_url)
        return parsed.netloc

    def _set_remote(self):
        """Обновленная логика добавления remote"""
        try:
            # Проверяем существует ли уже remote
            result = subprocess.run(
                ["git", "-C", str(self.repo_path.absolute()), "remote"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            remotes = result.stdout.strip().split('\n')
            
            if "export" in remotes:
                # Если remote существует, просто обновляем URL
                self._run_git_command("remote", "set-url", "export", self.config.git_remote_url)
            else:
                # Если remote не существует, добавляем его
                self._run_git_command("remote", "add", "export", self.config.git_remote_url)
        except subprocess.CalledProcessError as e:
            logger.error(f"Ошибка при настройке remote: {e.stderr}")
            raise

    def _init_repository(self):
        """Инициализирует репозиторий если он отсутствует и настраивает параметры Git"""
        try:
            git_dir = self.repo_path / ".git"
            if not git_dir.exists():
                logger.info(f"Initializing new Git repository in {self.repo_path}")
                self._run_git_command("init")
                # Создаем начальный коммит
                self._run_git_command("add", "-A")
                self._run_git_command("commit", "-m", "Initial commit", "--allow-empty")
            
            # Всегда настраиваем локальные параметры Git, даже если репозиторий уже существует
            logger.info(f"Configuring Git user settings for {self.config.git_config_name}")
            self._run_git_command("config", "user.name", self.config.git_config_name)
            self._run_git_command("config", "user.email", self.config.git_config_email)
        except subprocess.CalledProcessError as e:
            stderr_str = e.stderr
            if isinstance(e.stderr, bytes):
                stderr_str = e.stderr.decode('utf-8', errors='replace')
            logger.error(f"Ошибка при инициализации репозитория: {stderr_str}")
            raise

    def commit_changes(self, message: str = "Auto-commit from Tilda exporter"):
        """Выполняет полный цикл коммита и пуша"""
        try:
            # Добавляем текущую дату и время к сообщению коммита
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            commit_message = f"{message} [{timestamp}]"
            
            self._git_add()
            self._git_commit(commit_message)
            self._git_push()
            logger.info(f"Successfully committed changes to {self.repo_path}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Git operation failed: {e.stderr}")
            raise RuntimeError("Git command failed") from e

    def _git_add(self):
        """Добавляет все изменения в указанной базовой директории"""
        self._run_git_command("add", "-A")

    def _git_commit(self, message: str):
        """Создает коммит с указанным сообщением"""
        try:
            self._run_git_command("commit", "-m", message, "--allow-empty")
        except subprocess.CalledProcessError as e:
            # Проверяем, содержит ли сообщение об ошибке "nothing to commit"
            # Преобразуем stderr в строку, если это байты
            stderr_str = e.stderr
            if isinstance(e.stderr, bytes):
                stderr_str = e.stderr.decode('utf-8', errors='replace')
                
            if "nothing to commit" not in stderr_str:
                logger.error(f"Git command failed: {stderr_str}")
                raise

    def _git_push(self):
        """Отправляет изменения в удаленный репозиторий"""
        try:
            self._run_git_command("push", "-u", "export", "HEAD")
        except subprocess.CalledProcessError as e:
            stderr_str = e.stderr
            if isinstance(e.stderr, bytes):
                stderr_str = e.stderr.decode('utf-8', errors='replace')
            logger.error(f"Ошибка при выполнении git push: {stderr_str}")
            raise

    def _run_git_command(self, *args):
        """Универсальный метод выполнения Git команд"""
        cmd = ["git", "-C", str(self.repo_path.absolute()), *args]
        try:
            result = subprocess.run(
                cmd,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            logger.debug(f"Executed: {' '.join(cmd)}")
            logger.debug(f"Output: {result.stdout}")
            return result
        except subprocess.CalledProcessError as e:
            stderr_str = e.stderr
            if isinstance(e.stderr, bytes):
                stderr_str = e.stderr.decode('utf-8', errors='replace')
            logger.error(f"Git command failed: {stderr_str}")
            raise


#cfg = TildaConfig()
#committer = Committer(cfg)
#committer.commit_changes("Test3")