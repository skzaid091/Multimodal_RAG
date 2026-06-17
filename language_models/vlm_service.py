import base64

from groq import Groq


class VLM_Service:
    """
    Wrapper around a Vision-Language Model (VLM)
    hosted through Groq.

    Responsibilities:
    - Encode images
    - Send multimodal requests
    - Return generated responses

    This service is intentionally generic so it
    can be reused beyond figure captioning.
    """

    def __init__(self, vlm_model, GROQ_API_KEY):
        """
        Initialize Groq client and model.
        """

        self.model = vlm_model

        self.client = Groq(api_key=GROQ_API_KEY)


    def _encode_image(self, image_path):
        """
        Convert an image file into a Base64 string.

        Required because the Groq vision API
        accepts image content through a data URL.
        """

        with open(image_path, "rb") as f:

            return (
                base64
                .b64encode(f.read())
                .decode("utf-8")
            )


    def generate(self, image_path, prompt):
        """
        Generate a response from the vision model.

        Args:
            image_path:
                Path to the image.

            prompt:
                Instruction sent to the model.

        Returns:
            str:
                Generated response content.
        """

        image_b64 = self._encode_image(image_path)

        response = (
            self.client.chat.completions.create(
                model=self.model,

                messages=[
                    {
                        "role": "user",

                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",

                                "image_url": {
                                    "url":
                                    f"data:image/png;base64,{image_b64}"
                                }
                            }
                        ]
                    }
                ]
            )
        )

        return (
            response
            .choices[0]
            .message
            .content
        )