class FinalAnswerTool:
    description = "Use this to return your final answer to the user and stop reasoning."

    def __call__(self, input_text: str) -> str:
        return input_text