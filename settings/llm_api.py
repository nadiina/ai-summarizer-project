import openai


def call_llm_api(prompt: str, model: str = "gpt-4o-mini", temperature: float = 0.7) -> str:
    response = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature
    )
    return response["choices"][0]["message"]["content"].strip()
