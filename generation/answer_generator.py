from .prompt_builder import PromptBuilder

class AnswerGenerator:

    def __init__(self, config, llm_service):

        self.prompt_builder = PromptBuilder(config)

        self.llm_service = llm_service


    def get_answer(self, context):

        prompt = self.prompt_builder.build(
            retrieval_context=context["retrieval_context"],
            query=context["query"],
            history=context["history"],
        )

        answer =  self.llm_service.invoke(prompt)

        return answer