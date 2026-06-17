from .answer_generator import AnswerGenerator
from .source_generator import SourceGenerator


class Generator:

    def __init__(self, config, llm_service):
        self.config = config

        self.answer_generator = AnswerGenerator(config, llm_service)
        self.source_generator = SourceGenerator(config)


    def generate(self, context, chunks):

        answer = self.answer_generator.get_answer(context)

        sources = self.source_generator.get_sources(chunks)

        return {
            "answer": answer, 
            "sources": sources
        }