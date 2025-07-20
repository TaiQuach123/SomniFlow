from typing import Any


class BaseAgent:
    def run_sync(self, user_prompt: str, deps: Any):
        raise NotImplementedError

    async def run(self, user_prompt: str, deps: Any):
        raise NotImplementedError
