from pydantic import BaseModel


class StartLimitedModel(BaseModel):
    status: bool = False
    message: str = (
        "Достигнуто ограничение количества одновременных запусков. "
        "Дождитесь завершения выполнения одной из запущщеых задач."
    )
