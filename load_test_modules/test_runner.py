"""Manages the execution of load tests."""

import time
import random
import concurrent.futures
from tqdm import tqdm

from load_test_modules.api_client import send_request
from load_test_modules.prompt_manager import generate_prompts_with_uuid

def perform_warmup(num_requests=5):
    """
    Perform warm-up requests to initialize the GPU and inference pipeline
    before the actual load test begins.
    """
    print(f"\nPerforming {num_requests} warm-up requests...")
    warmup_results = []
    
    # Use distinct prompts for warm-up to avoid any caching effects
    warmup_prompts = generate_prompts_with_uuid(num_requests, base_prompt="This is a warm-up request to initialize the GPU.")
    
    # Send the warm-up requests serially
    for i, prompt in enumerate(warmup_prompts):
        result = send_request(prompt)
        warmup_results.append(result)
        status = "✓" if result["success"] else "✗"
        print(f"  Warm-up request {i+1}/{num_requests}: {status} ({result['response_time']:.2f}s)")
    
    success_count = sum(1 for r in warmup_results if r["success"])
    print(f"Warm-up complete: {success_count}/{num_requests} successful requests\n")
    
    # Optional: add a small delay to ensure everything is ready
    time.sleep(1)
    
    return warmup_results

def run_load_test(concurrency, num_requests, prompts, repetition=1):
    """Run a load test with the specified concurrency level and number of requests"""
    print(f"\nRunning load test with {concurrency} concurrent requests, {num_requests} total requests (Repetition {repetition}/{3})")
    
    results = []
    start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        # Submit all tasks
        futures = []
        for _ in range(num_requests):
            prompt = random.choice(prompts)
            futures.append(executor.submit(send_request, prompt))
            
        # Process results as they complete
        for future in tqdm(concurrent.futures.as_completed(futures), total=num_requests):
            results.append(future.result())
    
    total_duration = time.time() - start_time
    
    # Add test metadata to each result
    for result in results:
        result["test_duration"] = total_duration
        result["concurrency"] = concurrency
        result["repetition"] = repetition
        
        # Debug response times
        if "response_time" in result:
            print(f"DEBUG - Response time in result: {result['response_time']}")
    
    return results