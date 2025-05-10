import os
import sys
import requests

def test_gemini_api():
    """Test if the Gemini API key is working."""
    print("Testing Gemini API key...")
    
    # Get the API key from environment variables
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ Error: GEMINI_API_KEY environment variable is not set")
        sys.exit(1)
    
    try:
        # Make a simple API call
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
        headers = {'Content-Type': 'application/json'}
        data = {
            "contents": [{
                "parts": [{"text": "Write a haiku about programming."}]
            }]
        }
        
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        # Print the response
        result = response.json()
        print("API Response:", result['candidates'][0]['content']['parts'][0]['text'])
        print("✅ API key is working!")
        
    except Exception as e:
        print(f"❌ Error testing API key: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    test_gemini_api() 