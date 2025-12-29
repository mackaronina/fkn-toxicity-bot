from pathlib import Path

from pydantic import SecretStr, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class ConfigBase(BaseSettings):
    model_config = SettingsConfigDict(env_file=f'{BASE_DIR}/.env', env_file_encoding='utf-8', extra='ignore',
                                      case_sensitive=False)


class StickersSettings(ConfigBase):
    model_config = SettingsConfigDict(env_prefix='STICKER_')
    SBU_FILE_ID: str = 'CAACAgIAAxkBAAEKWrBlDPH3Ok1hxuoEndURzstMhckAAWYAAm8sAAIZOLlLPx0MDd1u460wBA'
    POROHOBOT_FILE_ID: str = 'CAACAgIAAxkBAAEK-splffs7OZYtr8wzINEw4lxbvwywoAACXSoAAg2JiEoB98dw3NQ3FjME'
    ZELEBOT_FILE_ID: str = 'CAACAgIAAxkBAAELGOplmDc9SkF-ZnVsdNl4vhvzZEo7BQAC5SwAAkrDgEr_AVwN_RkClDQE'
    NIGHT_FILE_ID: str = 'CAACAgIAAxkBAAEKWq5lDOyAX1vNodaWsT5amK0vGQe_ggACHCkAAspLuUtESxXfKFwfWTAE'


class PostgresSettings(ConfigBase):
    model_config = SettingsConfigDict(env_prefix='POSTGRES_')
    USER: str
    PASSWORD: SecretStr
    HOST: str
    PORT: int
    NAME: str

    def get_url(self) -> str:
        return (f'postgresql+asyncpg://{self.USER}:{self.PASSWORD.get_secret_value()}'
                f'@{self.HOST}:{self.PORT}/{self.NAME}')


class ToxicitySettings(ConfigBase):
    model_config = SettingsConfigDict(env_prefix='TOXIC_')
    API_KEY: SecretStr
    API_URL: str = 'https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze'
    THRESHOLD: float = 0.6
    REACTION: str = '😈'
    LEVEL_TEXTS: dict[int, str] = {
        10: 'Добрый чел позитивный',
        40: 'Норм чел',
        100: 'С гнильцой человек',
        200: 'Неадекват ебаный',
        400: 'Опасен для общества, изолируйте нахуй',
        900: 'Представляет прямую угрозу национальной безопасности Украины. Все сообщения переданы в СБУ',
        1500: 'Подлежит устранению согласно решению Собвеза ООН',
        999999: 'Классифицирован как SCP-███'
    }


class Settings(ConfigBase):
    BOT_TOKEN: SecretStr
    WEBHOOK_DOMAIN: str
    USE_POLLING: bool = False
    USE_SQLITE: bool = False
    SQLITE_URL: str = 'sqlite+aiosqlite:///db.sqlite3'
    HOST: str = '0.0.0.0'
    PORT: int = 80
    REPORT_CHAT_ID: int
    PAINT_WEB_APP_URL: str
    TIME_ZONE: str = 'UTC'
    TOXIC: ToxicitySettings = Field(default_factory=ToxicitySettings)
    POSTGRES: PostgresSettings = Field(default_factory=PostgresSettings)
    STICKERS: StickersSettings = Field(default_factory=StickersSettings)


SETTINGS = Settings()
