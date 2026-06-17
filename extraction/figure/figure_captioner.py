import re
import json

from data_models.models import FigureData

class FigureCaptioner:

    def __init__(self, config, vlm_service):

        self.config = config

        self.vlm_service = vlm_service


    def _build_prompt(self):

        return """
        Analyze the image.

        Return ONLY valid JSON.

        {
            "figure_type": "chart|diagram|flowchart|screenshot|photo|signature|stamp|logo|other",
            "caption": "short caption", 
            "summary": "brief summary"
        }

        Do not return markdown.
        Do not return explanations.
        Return JSON only.
        """
    

    def extract_json(self, response):

        if not response:
            raise ValueError("Empty response received.")

        response = response.strip()

        try:
            return json.loads(response)

        except Exception:
            pass

        # JSON Array
        match = re.search(r"\[.*\]", response, re.DOTALL)

        if match:
            return json.loads(match.group())

        # JSON Object
        match = re.search(r"\{.*\}", response, re.DOTALL)

        if match:
            return json.loads(match.group())

        raise ValueError(f"No JSON found:\n{response}")


    def caption(self, image_path):

        try:
            response = self.vlm_service.generate(
                image_path,
                self._build_prompt()
            )
            data = self.extract_json(response)

            return FigureData(
                caption=data.get("caption", ""),
                summary=data.get("summary", ""),
                figure_type=data.get("figure_type", "unknown"),
                image_path=image_path
            )

        except Exception as e:

            return FigureData(
                caption=f"Caption generation failed: {e}",
                figure_type="unknown",
                image_path=image_path,
                error=f"error: {str(e)}"
            )