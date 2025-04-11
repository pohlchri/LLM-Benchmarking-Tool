# LLM Load Testing Tool for Azure MaaP, Azure OpenAI Endpoints and Machine Learning Online Endpoints that follow the OpenAI API Inference standard🚀

A comprehensive performance benchmarking tool for Large Language Model API endpoints. This tool helps evaluate and analyze LLM inference performance under various load conditions, with a focus on throughput, latency, and scaling characteristics.

## Purpose 🎯

This tool is designed to:

- Benchmark LLM API endpoints under different concurrency levels
- Measure and analyze key performance metrics (response time, throughput, token throughput)
- Visualize performance scaling characteristics 
- Compare performance across different models or infrastructure setups
- Identify optimal concurrency levels and performance bottlenecks

## Features ✨

- Customizable concurrency levels for comprehensive performance testing
- Warm-up requests to initialize the model before testing
- Comprehensive metrics collection:
  - Average response time ⏱️
  - Request throughput (requests/second) 🔄
  - Output token throughput (tokens/second) 📝
  - Combined token throughput (input+output tokens/second) 📊
  - Success rate ✅
- Detailed visualizations of test results 📈
- Statistical analysis with mean and standard deviation across test repetitions 📉

## Usage 🖥️

Basic usage:
In the command line:
python load_test.py

## Configuration ⚙️

All configuration options are in `config.py`.

### Customizing Prompts 💬

The tool uses random UUIDs to generate unique prompts. If you want to customize the prompts:
- Modify the `generate_prompts_with_uuid` function in `prompt_manager.py` 
- Adjust the `prompt_template.py` to the required token length

## Understanding Results 📊

After running a test, the tool will:

1. Save detailed results to CSV files in the specified results directory 📁
2. Generate visualizations showing: 📈
   - Response time vs. concurrency
   - Throughput vs. concurrency
   - Output token throughput vs. concurrency
   - Combined token throughput vs. concurrency
3. Print a summary table with key metrics 📋

### Performance Interpretation 🔍

- **Response Time vs. Concurrency**: Shows how latency increases with concurrency ⏱️
- **System Throughput vs. Concurrency**: Shows overall throughput scaling (requests/second) 🔄
- **Token Throughput**: Shows how efficiently the system processes tokens with increasing load 📝

The ideal system shows linear scaling of throughput up to a certain point, with minimal increase in response time. ✅


