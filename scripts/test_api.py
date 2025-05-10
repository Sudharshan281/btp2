import os
import sys
from openai import OpenAI

def test_openai_api():
    """Test if the OpenAI API key is working."""
    print("Testing OpenAI API key...")
    
    # Initialize the OpenAI client
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    print(client, "client")
    
    try:
        # Make a simple API call
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Write a haiku about programming."}
            ]
        )
        
        # Print the response
        print("API Response:", response.choices[0].message.content)
        print("✅ API key is working!")
        
    except Exception as e:
        print(f"❌ Error testing API key: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    test_openai_api() 