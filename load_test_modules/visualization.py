"""Create visualizations from test results."""

import matplotlib.pyplot as plt
import pandas as pd
import statistics

def create_visualizations(results_file, output_prefix):
    """Create visualizations from the test results"""
    df = pd.read_csv(results_file)
    
    # Success rate pie chart
    plt.figure(figsize=(10, 6))
    success_counts = df['success'].value_counts()
    
    # Create labels dynamically based on the actual data
    labels = []
    for idx in success_counts.index:
        if idx == True:
            labels.append('Success')
        elif idx == False:
            labels.append('Failure')
        else:
            labels.append(f'Unknown ({idx})')
    
    colors = []
    for idx in success_counts.index:
        if idx == True:
            colors.append('#4CAF50')  # Green for success
        elif idx == False:
            colors.append('#F44336')  # Red for failure
        else:
            colors.append('#9E9E9E')  # Gray for unknown
    
    plt.pie(success_counts, labels=labels, autopct='%1.1f%%', colors=colors)
    plt.title('Request Success Rate')
    plt.savefig(f"{output_prefix}_success_rate.png")
    plt.close()
    
    # Response time histogram
    plt.figure(figsize=(12, 6))
    successful_df = df[df['success'] == True]
    if not successful_df.empty:
        plt.hist(successful_df['response_time'], bins=min(20, len(successful_df)), color='#2196F3', alpha=0.7)
        plt.axvline(successful_df['response_time'].mean(), color='red', linestyle='dashed', linewidth=2, 
                    label=f"Mean: {successful_df['response_time'].mean():.2f}s")
        plt.axvline(successful_df['response_time'].median(), color='green', linestyle='dashed', linewidth=2, 
                    label=f"Median: {successful_df['response_time'].median():.2f}s")
        plt.xlabel('Response Time (seconds)')
        plt.ylabel('Frequency')
        plt.title('Response Time Distribution (Successful Requests)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.savefig(f"{output_prefix}_response_times.png")
    plt.close()
    
    # Tokens per second distribution (if available)
    if 'tokens_per_second' in df.columns and not df['tokens_per_second'].isna().all():
        valid_tokens = df['tokens_per_second'].dropna()
        if not valid_tokens.empty:
            plt.figure(figsize=(12, 6))
            plt.hist(valid_tokens, bins=min(20, len(valid_tokens)), color='#9C27B0', alpha=0.7)
            plt.axvline(valid_tokens.mean(), color='red', linestyle='dashed', linewidth=2, 
                        label=f"Mean: {valid_tokens.mean():.2f} tokens/s")
            plt.xlabel('Tokens per Second')
            plt.ylabel('Frequency')
            plt.title('Token Generation Speed')
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.savefig(f"{output_prefix}_token_speed.png")
    plt.close()
    
    # Additional visualization: Concurrency vs Response Time (for scaling tests)
    if 'concurrency' in df.columns and len(df['concurrency'].unique()) > 1:
        plt.figure(figsize=(12, 6))
        
        # Group by concurrency and repetition to show all runs
        concurrency_rep_groups = df.groupby(['concurrency', 'repetition'])
        
        # For the average line
        concurrency_groups = df.groupby('concurrency')
        
        # Plot individual repetitions
        for (concurrency, repetition), group in concurrency_rep_groups:
            successful_group = group[group['success'] == True]
            if not successful_group.empty:
                mean_rt = successful_group['response_time'].mean()
                plt.scatter(concurrency, mean_rt, alpha=0.5, color='#2196F3', 
                           label=f"Rep {repetition}" if repetition == 1 else "")
        
        # Plot average line
        concurrency_levels = []
        mean_response_times = []
        std_response_times = []
        
        for concurrency, group in concurrency_groups:
            successful_group = group[group['success'] == True]
            if not successful_group.empty:
                concurrency_levels.append(concurrency)
                mean_response_times.append(successful_group['response_time'].mean())
                std_response_times.append(successful_group['response_time'].std())
        
        if concurrency_levels and mean_response_times:
            plt.errorbar(concurrency_levels, mean_response_times, yerr=std_response_times,
                       fmt='o-', color='#FF5722', linewidth=2, markersize=8,
                       label='Average with std dev')
            
        plt.xlabel('Concurrency Level')
        plt.ylabel('Mean Response Time (s)')
        plt.title('Response Time vs. Concurrency (Across All Repetitions)')
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.savefig(f"{output_prefix}_concurrency_response.png")
    plt.close()
    
    # Additional visualization: Average throughput by concurrency
    if 'concurrency' in df.columns and 'test_duration' in df.columns and len(df['concurrency'].unique()) > 1:
        plt.figure(figsize=(12, 6))
        
        # Group by concurrency and repetition
        concurrency_rep_groups = df.groupby(['concurrency', 'repetition'])
        concurrency_groups = df.groupby('concurrency')
        
        # For calculating average throughput
        throughputs_by_concurrency = {}
        
        # Plot individual repetition throughputs
        for (concurrency, repetition), group in concurrency_rep_groups:
            successful_group = group[group['success'] == True]
            if not successful_group.empty:
                throughput = len(successful_group) / successful_group['test_duration'].iloc[0]
                if concurrency not in throughputs_by_concurrency:
                    throughputs_by_concurrency[concurrency] = []
                throughputs_by_concurrency[concurrency].append(throughput)
                plt.scatter(concurrency, throughput, alpha=0.5, color='#4CAF50',
                           label=f"Rep {repetition}" if repetition == 1 else "")
        
        # Plot average line with error bars
        concurrency_levels = []
        mean_throughputs = []
        std_throughputs = []
        
        for concurrency in sorted(throughputs_by_concurrency.keys()):
            throughputs = throughputs_by_concurrency[concurrency]
            concurrency_levels.append(concurrency)
            mean_throughputs.append(statistics.mean(throughputs))
            if len(throughputs) > 1:
                std_throughputs.append(statistics.stdev(throughputs))
            else:
                std_throughputs.append(0)
        
        plt.errorbar(concurrency_levels, mean_throughputs, yerr=std_throughputs,
                   fmt='o-', color='#FF5722', linewidth=2, markersize=8,
                   label='Average with std dev')
            
        plt.xlabel('Concurrency Level')
        plt.ylabel('Throughput (req/s)')
        plt.title('Average Throughput vs. Concurrency (Across All Repetitions)')
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.savefig(f"{output_prefix}_concurrency_throughput.png")
    plt.close()

    # Total tokens per second distribution (if available)
    if 'total_tokens_per_second' in df.columns and not df['total_tokens_per_second'].isna().all():
        valid_tokens = df['total_tokens_per_second'].dropna()
        if not valid_tokens.empty:
            plt.figure(figsize=(12, 6))
            plt.hist(valid_tokens, bins=min(20, len(valid_tokens)), color='#FF9800', alpha=0.7)
            plt.axvline(valid_tokens.mean(), color='red', linestyle='dashed', linewidth=2, 
                        label=f"Mean: {valid_tokens.mean():.2f} total tokens/s")
            plt.xlabel('Total Tokens per Second (Input + Output)')
            plt.ylabel('Frequency')
            plt.title('Total Token Processing Speed')
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.savefig(f"{output_prefix}_total_token_speed.png")
    plt.close()
    
    return [f"{output_prefix}_success_rate.png", 
            f"{output_prefix}_response_times.png", 
            f"{output_prefix}_token_speed.png",
            f"{output_prefix}_total_token_speed.png",
            f"{output_prefix}_concurrency_response.png",
            f"{output_prefix}_concurrency_throughput.png"]

def create_scaling_visualization(summary_data, output_file):
    """Create visualization for scaling test results"""
    import pandas as pd
    import matplotlib.pyplot as plt
    from matplotlib.ticker import MaxNLocator
    
    df = pd.DataFrame(summary_data)
    
    # Print available columns for debugging
    print(f"Available columns for visualization: {df.columns.tolist()}")
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    
    x = df['concurrency']
    
    # Plot response time vs concurrency
    response_time_col = 'mean_response_time' if 'mean_response_time' in df.columns else 'response_time'
    stdev_response_time_col = 'stdev_response_time' if 'stdev_response_time' in df.columns else None
    
    if response_time_col in df.columns:
        if stdev_response_time_col and stdev_response_time_col in df.columns:
            ax1.errorbar(x, df[response_time_col], yerr=df[stdev_response_time_col], 
                        fmt='o-', color='blue', linewidth=2, markersize=8, capsize=5)
        else:
            ax1.plot(x, df[response_time_col], 'o-', color='blue', linewidth=2, markersize=8)
        
        ax1.set_xlabel('Concurrency Level')
        ax1.set_ylabel('Mean Response Time (seconds)')
        ax1.set_title('Response Time vs. Concurrency')
        ax1.grid(True, alpha=0.3)
        ax1.xaxis.set_major_locator(MaxNLocator(integer=True))
    else:
        ax1.text(0.5, 0.5, 'No response time data available', 
                horizontalalignment='center', verticalalignment='center')
    
    # Plot throughput vs concurrency
    throughput_col = 'mean_throughput' if 'mean_throughput' in df.columns else 'throughput'
    stdev_throughput_col = 'stdev_throughput' if 'stdev_throughput' in df.columns else None
    
    if throughput_col in df.columns:
        if stdev_throughput_col and stdev_throughput_col in df.columns:
            ax2.errorbar(x, df[throughput_col], yerr=df[stdev_throughput_col],
                        fmt='o-', color='green', linewidth=2, markersize=8, capsize=5)
        else:
            ax2.plot(x, df[throughput_col], 'o-', color='green', linewidth=2, markersize=8)
        
        ax2.set_xlabel('Concurrency Level')
        ax2.set_ylabel('Throughput (requests/second)')
        ax2.set_title('System Throughput vs. Concurrency')
        ax2.grid(True, alpha=0.3)
        ax2.xaxis.set_major_locator(MaxNLocator(integer=True))
    else:
        ax2.text(0.5, 0.5, 'No throughput data available', 
                horizontalalignment='center', verticalalignment='center')
    
    # Plot output token throughput vs concurrency
    output_token_col = 'mean_system_output_token_throughput' if 'mean_system_output_token_throughput' in df.columns else 'system_output_token_throughput'
    stdev_output_token_col = 'stdev_system_output_token_throughput' if 'stdev_system_output_token_throughput' in df.columns else None
    
    if output_token_col in df.columns:
        if stdev_output_token_col and stdev_output_token_col in df.columns:
            ax3.errorbar(x, df[output_token_col], yerr=df[stdev_output_token_col],
                        fmt='o-', color='purple', linewidth=2, markersize=8, capsize=5)
        else:
            ax3.plot(x, df[output_token_col], 'o-', color='purple', linewidth=2, markersize=8)
        
        ax3.set_xlabel('Concurrency Level')
        ax3.set_ylabel('Output Token Throughput (tokens/s)')
        ax3.set_title('System Output Token Throughput vs. Concurrency')
        ax3.grid(True, alpha=0.3)
        ax3.xaxis.set_major_locator(MaxNLocator(integer=True))
    else:
        ax3.text(0.5, 0.5, 'No output token throughput data available', 
                horizontalalignment='center', verticalalignment='center')
    
    # Plot combined token throughput vs concurrency
    combined_token_col = 'mean_system_combined_token_throughput' if 'mean_system_combined_token_throughput' in df.columns else 'system_combined_token_throughput'
    stdev_combined_token_col = 'stdev_system_combined_token_throughput' if 'stdev_system_combined_token_throughput' in df.columns else None
    
    if combined_token_col in df.columns:
        if stdev_combined_token_col and stdev_combined_token_col in df.columns:
            ax4.errorbar(x, df[combined_token_col], yerr=df[stdev_combined_token_col],
                        fmt='o-', color='orange', linewidth=2, markersize=8, capsize=5)
        else:
            ax4.plot(x, df[combined_token_col], 'o-', color='orange', linewidth=2, markersize=8)
        
        ax4.set_xlabel('Concurrency Level')
        ax4.set_ylabel('Combined Token Throughput (tokens/s)')
        ax4.set_title('System Combined Token Throughput vs. Concurrency')
        ax4.grid(True, alpha=0.3)
        ax4.xaxis.set_major_locator(MaxNLocator(integer=True))
    else:
        ax4.text(0.5, 0.5, 'No combined token throughput data available', 
                horizontalalignment='center', verticalalignment='center')
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300)
    plt.close()

    return output_file