import os


class Settings:
    app_name: str = os.getenv("APP_NAME", "Task Manager API")
    app_environment: str = os.getenv("APP_ENV", "development")
    instance_name: str = os.getenv("INSTANCE_NAME", "backend-local")

    database_host: str = os.getenv("DATABASE_HOST", "localhost")
    database_port: int = int(os.getenv("DATABASE_PORT", "5432"))
    database_name: str = os.getenv("DATABASE_NAME", "taskdb")
    database_user: str = os.getenv("DATABASE_USER", "taskuser")
    database_password: str = os.getenv(
        "DATABASE_PASSWORD",
        "taskpassword",
    )

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://"
            f"{self.database_user}:"
            f"{self.database_password}@"
            f"{self.database_host}:"
            f"{self.database_port}/"
            f"{self.database_name}"
        )


settings = Settings()
