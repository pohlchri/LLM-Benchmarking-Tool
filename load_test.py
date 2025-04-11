"""
LLM Load Testing Tool

This script performs load testing on LLM API endpoints with various concurrency
levels and collects performance metrics.
"""

import argparse
import datetime
import os
import statistics
import time

# Import modules
from load_test_modules.config import (
    RESULTS_DIR, DEFAULT_REPETITIONS, DEFAULT_WARMUP, DEFAULT_BREAK_TIME,
    CONCURRENCY_LEVELS
)
from load_test_modules.prompt_manager import generate_prompts_with_uuid
from load_test_modules.test_runner import perform_warmup, run_load_test
from load_test_modules.data_utils import save_results_to_csv, analyze_results
from load_test_modules.visualization import create_visualizations, create_scaling_visualization

def run_test(args):
    """Run load testing with specified parameters"""
    all_results = []
    
    # Generate prompts
    prompts = generate_prompts_with_uuid(1000)
    
    # Generate timestamp for this test run
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Use custom concurrency levels if provided, otherwise use config
    concurrency_levels = args.concurrency_levels if args.concurrency_levels else CONCURRENCY_LEVELS
    
    # Determine if this is effectively a scaling test (multiple levels)
    is_scaling_test = len(concurrency_levels) > 1
    test_type = "scaling" if is_scaling_test else "standard"
    
    # Generate output basename
    if is_scaling_test:
        output_basename = f"scaling_test_{timestamp}"
    else:
        output_basename = f"load_test_{timestamp}_c{concurrency_levels[0]}"
    
    print(f"Testing with concurrency levels: {concurrency_levels}")
    
    # Store metrics for all concurrency levels
    summary = []
    concurrency_metrics = {}
    
    for concurrency in concurrency_levels:
        print(f"\n===== Testing concurrency level: {concurrency} =====")
        
        concurrency_metrics[concurrency] = {
            "response_times": [],
            "throughputs": [],
            "success_rates": [],
            "system_output_token_throughputs": [],
            "system_combined_token_throughputs": [],
        }
        
        # Always set number of requests equal to concurrency
        num_requests = concurrency
        
        # For each concurrency level, run multiple repetitions
        for repetition in range(1, args.repetitions + 1):
            print(f"\nRunning batch {repetition}/{args.repetitions} with {concurrency} concurrent requests")
            
            # Run the load test with the specified concurrency
            results = run_load_test(concurrency, num_requests, prompts, repetition)
            
            # Debug the raw response times
            print(f"DEBUG - Raw response times: {[r.get('response_time', 0) for r in results if r.get('success', False)]}")
            
            metrics = analyze_results(results)
            print(f"DEBUG - Mean response time from metrics: {metrics.get('mean_response_time', 'N/A')}")
            
            all_results.extend(results)
            
            # Store metrics for each repetition
            for metric_key in concurrency_metrics[concurrency]:
                metric_name = metric_key.rstrip('s')  # Convert plural to singular
                
                if metric_name == "response_time":
                    value = metrics.get('mean_response_time', 0)
                else:
                    value = metrics.get(metric_name, 0)
                    
                print(f"DEBUG - Adding {metric_name}: {value}")
                concurrency_metrics[concurrency][metric_key].append(value)
        
        # Calculate statistics for this concurrency level
        summary_entry = {"concurrency": concurrency, "requests": num_requests}
        
        # Calculate mean and standard deviation for all metrics
        for metric_key, values in concurrency_metrics[concurrency].items():
            metric_name = metric_key.rstrip('s')  # Convert plural to singular
            print(f"DEBUG - Calculating mean for {metric_name} from values: {values}")
            
            # Make sure we only average non-zero values for response_time
            if metric_key == "response_times":
                non_zero_values = [v for v in values if v > 0]
                if non_zero_values:
                    summary_entry[f"mean_{metric_name}"] = statistics.mean(non_zero_values)
                    if len(non_zero_values) > 1:
                        summary_entry[f"stdev_{metric_name}"] = statistics.stdev(non_zero_values)
                    else:
                        summary_entry[f"stdev_{metric_name}"] = 0
                else:
                    summary_entry[f"mean_{metric_name}"] = 0
                    summary_entry[f"stdev_{metric_name}"] = 0
            else:
                # For other metrics
                if values:
                    summary_entry[f"mean_{metric_name}"] = statistics.mean(values)
                    if len(values) > 1:
                        summary_entry[f"stdev_{metric_name}"] = statistics.stdev(values)
                    else:
                        summary_entry[f"stdev_{metric_name}"] = 0
                else:
                    summary_entry[f"mean_{metric_name}"] = 0
                    summary_entry[f"stdev_{metric_name}"] = 0
        
        summary.append(summary_entry)
        
        # Break between concurrency levels if not the last one
        if concurrency_levels.index(concurrency) < len(concurrency_levels) - 1:
            print(f"Taking a {args.break_time} second break between concurrency levels...")
            time.sleep(args.break_time)
    
    # Print summary table
    print(f"\n===== {test_type.upper()} TEST SUMMARY (AVERAGED ACROSS REPETITIONS) =====")
    print("Concurrency | Success Rate | Mean Response Time (s) | Throughput (req/s)")
    print("-----------|----------|-------------|----------------------|------------------")
    for data in summary:
        print(f"{data['concurrency']:11d} | {data['mean_success_rate']*100:11.2f}% | "
              f"{data['mean_response_time']:20.2f} ± {data['stdev_response_time']:5.2f} | "
              f"{data['mean_throughput']:8.2f} ± {data['stdev_throughput']:5.2f}")
    
    # Save all results to CSV
    csv_file = os.path.join(RESULTS_DIR, f"{output_basename}.csv")
    viz_prefix = os.path.join(RESULTS_DIR, output_basename)
    save_results_to_csv(all_results, csv_file)
    
    # Create visualizations (common for both test types)
    viz_files = create_visualizations(csv_file, viz_prefix)
    
    # Add scaling visualization only if multiple concurrency levels
    if is_scaling_test:
        scaling_viz_file = os.path.join(RESULTS_DIR, f"scaling_performance_{timestamp}.png")
        create_scaling_visualization(summary, scaling_viz_file)
        viz_files.append(scaling_viz_file)
    
    print(f"\nResult visualizations saved to:")
    for f in viz_files:
        if os.path.exists(f):
            print(f"  - {f}")
    
    return all_results

def main():
    """Main function to run the load testing tool"""
    parser = argparse.ArgumentParser(description="Load test for LLM API endpoints")
    parser.add_argument("--repetitions", type=int, default=DEFAULT_REPETITIONS,
                        help="Number of times to repeat each test for averaging")
    parser.add_argument("--warmup", type=int, default=DEFAULT_WARMUP,
                        help="Number of warm-up requests to perform before testing")
    parser.add_argument("--break-time", type=int, default=DEFAULT_BREAK_TIME,
                        help="Number of seconds to wait between test runs")
    parser.add_argument("--concurrency-levels", nargs='+', type=int, 
                        help="Custom concurrency levels to test (overrides config)")
    args = parser.parse_args()
    
    # Perform warm-up requests only once
    if args.warmup > 0:
        perform_warmup(args.warmup)
    
    # Run the test with configured or custom concurrency levels
    run_test(args)

if __name__ == "__main__":
    main()