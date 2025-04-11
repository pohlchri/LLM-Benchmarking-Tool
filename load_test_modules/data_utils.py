"""Utilities for processing and analyzing test results."""

import csv
import statistics
import os
from load_test_modules.config import RESULTS_DIR

def save_results_to_csv(results, filename):
    """Save test results to a CSV file"""
    fieldnames = ["timestamp", "concurrency", "success", "status_code", "response_time", 
                  "tokens_generated", "tokens_input", "total_tokens", 
                  "tokens_per_second", "total_tokens_per_second", "test_duration",
                  "repetition", "endpoint_type"]
    
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            # Filter only the fields we want to save
            filtered_result = {k: result.get(k) for k in fieldnames if k in result}
            writer.writerow(filtered_result)
    
    print(f"Results saved to {filename}")

def analyze_results(results):
    """Analyze and print the results of the load test"""
    # Extract metrics from successful and failed requests
    successful_requests = [r for r in results if r.get("success", False)]
    failed_requests = [r for r in results if not r.get("success", False)]
    
    # Calculate response times for successful requests
    response_times = [r.get("response_time", 0) for r in successful_requests if "response_time" in r]
    valid_response_times = [rt for rt in response_times if rt > 0]
    
    print(f"DEBUG: All response times: {response_times}")
    print(f"DEBUG: Valid response times: {valid_response_times}")
    
    # Extract timestamps for throughput calculation
    if successful_requests:
        # Calculate start and end time from timestamps
        request_timestamps = [(r.get("timestamp", 0) - r.get("response_time", 0)) 
                              for r in successful_requests 
                              if "timestamp" in r and "response_time" in r]
        response_timestamps = [r.get("timestamp", 0) 
                              for r in successful_requests 
                              if "timestamp" in r]
        
        if request_timestamps and response_timestamps:
            start_time = min(request_timestamps)
            end_time = max(response_timestamps)
            total_duration = end_time - start_time
        else:
            # Fallback to sum of response times if timestamps aren't reliable
            total_duration = sum(valid_response_times)
            
        print(f"DEBUG: Total test duration: {total_duration:.4f} seconds")
        throughput = len(successful_requests) / total_duration if total_duration > 0 else 0
    else:
        total_duration = 0
        throughput = 0
    
    # Calculate system-wide token metrics
    total_tokens_generated = sum([r.get("tokens_generated", 0) for r in successful_requests])
    total_tokens_input = sum([r.get("tokens_input", 0) for r in successful_requests])
    total_all_tokens = total_tokens_generated + total_tokens_input
    
    # Calculate system token throughput metrics
    system_output_token_throughput = total_tokens_generated / total_duration if total_duration > 0 else 0
    system_combined_token_throughput = total_all_tokens / total_duration if total_duration > 0 else 0
    
    print("\n=== TEST RESULTS ===")
    print(f"Total requests: {len(results)}")
    print(f"Successful requests: {len(successful_requests)}")
    print(f"Failed requests: {len(failed_requests)}")
    print(f"Success rate: {len(successful_requests) / len(results) * 100:.2f}%")
    
    # Calculate mean response time
    mean_response_time = 0
    if valid_response_times:
        mean_response_time = sum(valid_response_times) / len(valid_response_times)
        min_response_time = min(valid_response_times)
        max_response_time = max(valid_response_times)
        
        print(f"\nResponse Time (seconds):")
        print(f"  Mean: {mean_response_time:.4f}")
        print(f"  Min: {min_response_time:.4f}")
        print(f"  Max: {max_response_time:.4f}")
        if len(valid_response_times) > 1:
            std_dev = statistics.stdev(valid_response_times)
            print(f"  Std Dev: {std_dev:.4f}")
    else:
        print("\nWarning: No valid response times found.")
    
    print(f"\nThroughput:")
    print(f"  Requests/second: {throughput:.4f}")
    print(f"  Test duration: {total_duration:.4f} seconds")
    
    # Add token throughput metrics
    if successful_requests:
        print(f"\nSystem Token Throughput:")
        print(f"  Output tokens generated: {total_tokens_generated}")
        print(f"  Input tokens processed: {total_tokens_input}")
        print(f"  Total tokens (input+output): {total_all_tokens}")
        print(f"  Output tokens/second: {system_output_token_throughput:.2f}")
        print(f"  Combined tokens/second (input+output): {system_combined_token_throughput:.2f}")
    
    if failed_requests:
        error_counts = {}
        for r in failed_requests:
            error = r.get("error", "Unknown error")
            error_counts[error] = error_counts.get(error, 0) + 1
        
        print("\nError distribution:")
        for error, count in error_counts.items():
            print(f"  {error}: {count}")
    
    return {
        "success_rate": len(successful_requests) / len(results) if results else 0,
        "mean_response_time": mean_response_time,
        "throughput": throughput,
        "system_output_token_throughput": system_output_token_throughput,
        "system_combined_token_throughput": system_combined_token_throughput,
        "total_tokens_generated": total_tokens_generated,
        "total_tokens_input": total_tokens_input,
        "total_all_tokens": total_all_tokens,
        "test_duration": total_duration
    }