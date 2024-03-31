
import openai

def test_openai_api():
    openai.api_key = ' '

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "You are a helpful assistant."},
                      {"role": "user", "content": "What is the capital of France?"}]
        )
        print("API Response:", response['choices'][0]['message']['content'])
    except Exception as e:
        print(f"Error accessing OpenAI API: {e}")

test_openai_api()
