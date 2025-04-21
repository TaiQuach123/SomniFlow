import re


def remove_think_tokens(text: str) -> str:
    return re.sub(re.compile(r"<think>.*?</think>", re.DOTALL), "", text)


def process_instruction(instruction: str) -> str:
    instruction = remove_think_tokens(instruction).strip()
    instruction = "Instruction from Reasoning Agent:\n\n" + instruction
    return instruction
