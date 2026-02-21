#!/usr/bin/env python3
"""
Test script to verify OpenRouter integration
"""
import os
import sys
from pathlib import Path

# Add the AI_Employee_Vault to the path so we can import modules
sys.path.insert(0, str(Path(__file__).parent))

def test_openrouter_connection():
    """Test the OpenRouter API connection"""
    print("Testing OpenRouter API connection...")

    try:
        from AI_Employee_Vault.openrouter_config import OpenRouterAPI, chat_with_openrouter

        # Load API key from environment
        api_key = os.getenv('OPENROUTER_API_KEY')
        if not api_key:
            print("❌ Error: OPENROUTER_API_KEY not found in environment")
            return False

        print("✅ API key found in environment")

        # Initialize OpenRouter API
        try:
            client = OpenRouterAPI(api_key)
            print("✅ OpenRouter API client initialized successfully")
        except Exception as e:
            print(f"❌ Error initializing OpenRouter API: {e}")
            return False

        # Test a simple chat completion with the model from environment
        try:
            from AI_Employee_Vault.openrouter_config import OpenRouterAPI

            # Use the model from environment or fall back to a default
            model = os.getenv('OPENROUTER_MODEL', 'meta-llama/llama-3.1-8b-instruct')

            client = OpenRouterAPI(api_key)
            response = client.chat_completion(
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant."},
                    {"role": "user", "content": "Hello, this is a test. Please respond with 'Hello, this is OpenRouter.' Keep it short."}
                ],
                model=model,
                max_tokens=100  # Use very few tokens to avoid credit issues
            )

            response_text = response["choices"][0]["message"]["content"]
            print("✅ Chat completion successful")
            print(f"Response: {response_text[:100]}...")
            return True

        except Exception as e:
            print(f"❌ Error in chat completion: {e}")
            return False

    except ImportError as e:
        print(f"❌ Error importing OpenRouter modules: {e}")
        return False

def test_reasoning_module():
    """Test the OpenRouter reasoning module"""
    print("\nTesting OpenRouter reasoning module...")

    try:
        from AI_Employee_Vault.openrouter_reasoning import OpenRouterReasoning

        # Initialize reasoning module
        try:
            reasoning = OpenRouterReasoning(vault_path="./AI_Employee_Vault")
            print("✅ OpenRouter reasoning module initialized successfully")
        except Exception as e:
            print(f"❌ Error initializing reasoning module: {e}")
            return False

        # Test task analysis
        try:
            analysis = reasoning.analyze_task(
                task_description="Send a professional email to a client about project status",
                context="The client is asking about the status of their project that is 75% complete.",
                company_handbook="All client communications must be professional and timely."
            )

            if "error" not in analysis:
                print("✅ Task analysis successful")
            else:
                print(f"❌ Task analysis failed: {analysis.get('error')}")
                return False

        except Exception as e:
            print(f"❌ Error in task analysis: {e}")
            return False

        return True

    except ImportError as e:
        print(f"❌ Error importing reasoning module: {e}")
        return False

def main():
    print("OpenRouter Integration Test")
    print("=" * 50)

    # Test OpenRouter connection
    connection_ok = test_openrouter_connection()

    # Test reasoning module
    reasoning_ok = test_reasoning_module()

    print("\n" + "=" * 50)
    print("Test Results:")
    print(f"  OpenRouter Connection: {'✅ PASS' if connection_ok else '❌ FAIL'}")
    print(f"  Reasoning Module:      {'✅ PASS' if reasoning_ok else '❌ FAIL'}")

    if connection_ok and reasoning_ok:
        print("\n🎉 All tests passed! OpenRouter integration is working correctly.")
        print("\nTo start the AI Employee with OpenRouter, run:")
        print("  python -m AI_Employee_Vault.openrouter_orchestrator")
        return True
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)