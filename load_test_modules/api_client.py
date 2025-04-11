"""API client for sending requests to model endpoints."""

import time
import requests
from load_test_modules.config import API_URL, AUTH_TOKEN, MODEL, DEFAULT_MAX_TOKENS, DEFAULT_TEMPERATURE

def send_request(prompt):
    """Send a single request to the API and return metrics"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {AUTH_TOKEN}"
    }
    
    # Dynamically determine request format based on the endpoint
    if "/score" in API_URL:
        # Format for Azure ML Managed Online Endpoint (/score)
        data = {
            "input_data": {
                "input_string": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "parameters": {
                    "temperature": DEFAULT_TEMPERATURE,
                    "max_tokens": DEFAULT_MAX_TOKENS
                }
            }
        }
    else:
        # Format for OpenAI-compatible endpoint (/v1/chat/completions)
        data = {
            "model": MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": DEFAULT_MAX_TOKENS,
            "temperature": DEFAULT_TEMPERATURE
        }
    
    print(f"DEBUG: Sending request to {API_URL}")
    start_time = time.time()
    try:
        response = requests.post(API_URL, headers=headers, json=data)
        elapsed = time.time() - start_time
        print(f"DEBUG: Request completed in {elapsed:.4f} seconds with status {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                
                # Extract tokens based on endpoint type
                if "/score" in API_URL:
                    # Parse response from /score endpoint
                    generated_text = result.get('output', '')
                    tokens_generated = result.get('token_count', {}).get('completion_tokens', 0)
                    tokens_input = result.get('token_count', {}).get('prompt_tokens', 0)
                else:
                    # Parse response from /v1/chat/completions endpoint
                    generated_text = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                    tokens_generated = result.get('usage', {}).get('completion_tokens', 0)
                    tokens_input = result.get('usage', {}).get('prompt_tokens', 0)
                
                # If token counts weren't provided, estimate them
                if not tokens_generated:
                    tokens_generated = len(generated_text.split()) if generated_text else 0
                    tokens_input = len(prompt.split())
                
                total_tokens = tokens_generated + tokens_input
                
                return_data = {
                    "success": True,
                    "status_code": response.status_code,
                    "response_time": elapsed,
                    "tokens_generated": tokens_generated,
                    "tokens_input": tokens_input,
                    "total_tokens": total_tokens,
                    "tokens_per_second": tokens_generated / elapsed if elapsed > 0 else 0,
                    "total_tokens_per_second": total_tokens / elapsed if elapsed > 0 else 0,
                    "timestamp": time.time(),
                    "endpoint_type": "/score" if "/score" in API_URL else "/v1/chat/completions"
                }
                print(f"DEBUG: Successful response with response_time={elapsed:.4f}")
                return return_data
                
            except Exception as e:
                print(f"DEBUG: Parsing error: {str(e)}")
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "response_time": elapsed,
                    "tokens_generated": None,
                    "tokens_input": None,
                    "total_tokens": None,
                    "tokens_per_second": None,
                    "total_tokens_per_second": None,
                    "timestamp": time.time(),
                    "parsing_error": str(e),
                    "endpoint_type": "/score" if "/score" in API_URL else "/v1/chat/completions"
                }
        else:
            print(f"DEBUG: Failed response with status {response.status_code}")
            return {
                "success": False,
                "status_code": response.status_code,
                "error": response.text,
                "response_time": elapsed,
                "timestamp": time.time(),
                "endpoint_type": "/score" if "/score" in API_URL else "/v1/chat/completions"
            }
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"DEBUG: Exception during request: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "response_time": elapsed,
            "timestamp": time.time(),
            "endpoint_type": "/score" if "/score" in API_URL else "/v1/chat/completions"
        }