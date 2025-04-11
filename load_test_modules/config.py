"""Configuration settings for load tests."""

import os

# API Configuration
# API endpoint URL - change this to your LLM API endpoint works for /v1/chat/completions or /score
API_URL = ""
# Authentication token for the API
AUTH_TOKEN = ""
# Model identifier (for OpenAI-format-compatible endpoints)
MODEL = "meta-llama/Llama-3.3-70B-Instruct" # Change this to your model name

# Results directory
RESULTS_DIR = "load_test_results_llama_70B_500_in_64_MAAP_out" # Change this to your desired results directory
os.makedirs(RESULTS_DIR, exist_ok=True)

# Number of repetitions for each test to calculate averages and standard deviation
DEFAULT_REPETITIONS = 3

# Number of warm-up requests to perform before testing
DEFAULT_WARMUP = 5

# Break time (in seconds) between test runs
DEFAULT_BREAK_TIME = 5

# Maximum tokens to generate in each response
DEFAULT_MAX_TOKENS = 64

# Temperature setting for the LLM
DEFAULT_TEMPERATURE = 0.7

# Concurrency levels to test
# This is the most important setting - define the levels you want to test
# For a single level test, use just one value, e.g., [5]
# For testing multiple levels, add more values, e.g., [1, 2, 4, 8, 16]
CONCURRENCY_LEVELS = [2, 4, 8, 16, 32]
