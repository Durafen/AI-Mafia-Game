#!/usr/bin/env python3
"""Test script to verify all OpenRouter models are working"""

import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# OpenRouter models from config.py
OPENROUTER_MODELS = [
    {"name": "Mimo", "model": "xiaomi/mimo-v2-flash:free"},
    {"name": "Olmo", "model": "allenai/olmo-3.1-32b-think:free"},
    {"name": "Chimera", "model": "tngtech/deepseek-r1t2-chimera:free"},
    {"name": "Deepseek", "model": "nex-agi/deepseek-v3.1-nex-n1:free"},
    {"name": "Devstral", "model": "mistralai/devstral-2512:free"},
    {"name": "Oss", "model": "openai/gpt-oss-120b:free"},
]

def test_openrouter_model(client, model_name, model_id):
    """Test a single OpenRouter model"""
    test_prompt = 'Respond with valid JSON only: {"status": "working", "message": "Hello from AI"}'
    
    try:
        print(f"\n🔄 Testing {model_name} ({model_id})...")
        response = client.chat.completions.create(
            model=model_id,
            messages=[
                {"role": "user", "content": test_prompt}
            ],
            max_tokens=100
        )
        
        result = response.choices[0].message.content
        print(f"✅ {model_name}: SUCCESS")
        print(f"   Response: {result[:100]}...")
        return True
        
    except Exception as e:
        print(f"❌ {model_name}: FAILED")
        print(f"   Error: {str(e)}")
        return False

def main():
    # Check for API key
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ OPENROUTER_API_KEY not found in environment variables")
        print("   Please set it in your .env file")
        return
    
    print("=" * 60)
    print("OpenRouter Models Test".center(60))
    print("=" * 60)
    
    # Initialize OpenRouter client
    client = OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
    )
    
    # Test each model
    results = {}
    for model in OPENROUTER_MODELS:
        success = test_openrouter_model(client, model["name"], model["model"])
        results[model["name"]] = success
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary".center(60))
    print("=" * 60)
    
    working = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"\n✅ Working: {working}/{total}")
    print(f"❌ Failed: {total - working}/{total}")
    
    print("\nDetailed Results:")
    for name, success in results.items():
        status = "✅ Working" if success else "❌ Failed"
        print(f"  {name:15} {status}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
