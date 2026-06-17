from groq import Groq


class LLMService:

    def __init__(self, llm_model, GROQ_API_KEY):

        self.model = llm_model

        self.client = Groq(api_key=GROQ_API_KEY)


    def invoke(self, prompt, system_prompt=None, temperature=0.1):

        messages = []

        if system_prompt:

            messages.append(
                {
                    "role": "system",
                    "content": system_prompt
                }
            )

        messages.append(
            {
                "role": "user",
                "content": prompt
            }
        )

        response = (
            self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature
            )
        )

        return (
            response
            .choices[0]
            .message
            .content
        )


    def chat(self, messages, temperature=0.1):

        response = (
            self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature
            )
        )

        return (
            response
            .choices[0]
            .message
            .content
        )