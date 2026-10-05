from typing import Any


class AIProvider:
    """
    Interface for AI providers used by BizLens.
    """

    def explain(
        self,
        diagnosis: dict[str, Any],
    ) -> dict[str, Any]:
        raise NotImplementedError
    def ask(
        self,
        question: str,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        raise NotImplementedError
