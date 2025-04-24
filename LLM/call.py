from openai import OpenAI

def call(api, base_url, model, prompt, query): 

    client = OpenAI(api_key=api, base_url=base_url)

    response = client.chat.completions.create(
        model= model,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": query},
        ],
        stream=False
    )

    return response.choices[0].message.content