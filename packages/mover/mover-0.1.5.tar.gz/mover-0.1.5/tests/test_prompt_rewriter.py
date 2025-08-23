## test prompt rewriter

from mover.synthesizers.prompt_rewriter import PromptRewriter


def test_prompt_rewriter():
    prompt_rewriter = PromptRewriter()
    chat_history = [
        prompt_rewriter.compose_sys_msg(),
        prompt_rewriter.compose_initial_user_prompt("Move the square to the right", 10)
    ]
    response, error_msg = prompt_rewriter.generate(chat_history, "test_prompt_rewriter.json")
    print(response)
    print(error_msg)


if __name__ == "__main__":
    test_prompt_rewriter()