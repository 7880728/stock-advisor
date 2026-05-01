"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./data/stock_advisor.db"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Push
    wechat_push_token: str = ""       # Server酱 SendKey
    pushplus_token: str = ""          # PushPlus Token

    # Scheduling
    eod_scan_time: str = "15:30"      # 日终扫描时间
    intraday_interval: int = 5        # 盘中监控间隔（分钟）

    # Analysis
    selected_pool_size: int = 50      # 精选池大小

    model_config = {"env_prefix": "SA_", "env_file": ".env"}


settings = Settings()
