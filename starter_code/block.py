# from .nlp_layer import NLPLayer
# from .llm_layer import LLMLayer

# class Block:
#     def __init__(self):
#         self.nlp_layer = NLPLayer()
#         self.llm_layer = LLMLayer()

#     def process(self, words):
#         # NLP Layer identifies potential groups
#         nlp_groups = self.nlp_layer.get_initial_groups(words)
        
#         # LLM Layer validates these groups
#         validated_groups = []
#         for group in nlp_groups:
#             is_valid, validated_group = self.llm_layer.validate_group_with_llm(group)
#             if is_valid:
#                 validated_groups.append(validated_group)
#         return validated_groups


from .nlp_layer import NLPLayer
from .llm_layer import LLMLayer

class Block:
    def __init__(self):
        self.nlp_layer = NLPLayer()
        self.llm_layer = LLMLayer()

    def process(self, words):
        initial_groups = self.llm_layer.generate_initial_groups(words)
        nlp_validated_groups = self.nlp_layer.refine_groups(initial_groups)
        
        validated_groups = []
        for group in nlp_validated_groups:
            is_valid, validated_group = self.llm_layer.validate_group_with_llm(group)
            if is_valid:
                validated_groups.append(validated_group)
        return validated_groups
