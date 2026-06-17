from citation.citation_builder import CitationBuilder


class SourceGenerator:

    def __init__(self, config):
        self.config = config
        self.citation_builder = CitationBuilder(config)


    def get_sources(self, chunks):
        citations = self.citation_builder.build(chunks)

        return citations