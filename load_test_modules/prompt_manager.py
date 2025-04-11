"""Manages prompt generation for load tests."""

import uuid
from load_test_modules.prompt_template import BASE_PROMPT

def generate_prompts_with_uuid(count=1000, base_prompt=None):
    """Generate multiple prompts with unique UUIDs"""
    if base_prompt is None:
        base_prompt = BASE_PROMPT
    return [f"{uuid.uuid4()} {base_prompt}" for _ in range(count)]