from .nlp_layer import NLPLayer
from .llm_layer import LLMLayer

MAX_RETRIES = 6  # Maximum attempts for re-evaluation of groups

class GroupingManager:
    def __init__(self, words):
        self.words = words
        self.nlp_layer = NLPLayer()
        self.llm_layer = LLMLayer()
        self.client = self.llm_layer.create_client()  # Create client once for reuse

        self.invalid_words = set()  # Track invalid words from flagged groups
        self.retries = 5  # Counter for re-evaluation attempts
    
    def get_best_group(self):
        """
        Generate and evaluate groups using the NLP and LLM layers. If the LLM layer detects an invalid group,
        it triggers re-evaluation with filtered candidate groups.
        """
        candidate_groups = self.nlp_layer.get_initial_groups(self.words)
        # print('------>',candidate_groups)
        for group in candidate_groups:
            if self.retries >= MAX_RETRIES:
                break
            
            # Validate the group using LLM
            is_valid, validated_group = self.llm_layer.validate_group_with_llm(group)
            print("Validated group:", validated_group)
            
            if is_valid:
                return validated_group, False  # Return the validated group, do not end turn
            else:
                # Update invalid words and refine candidate groups
                self.invalid_words.update(validated_group)
                candidate_groups = self.nlp_layer.get_initial_groups(self.words)
                candidate_groups = [g for g in candidate_groups if not any(w in self.invalid_words for w in g)]
                self.retries += 1  # Increase re-evaluation count

        # Fallback to highest scoring group if retries are exhausted
        scores = []
        # print("Candidate groups:????", candidate_groups)
        for group in candidate_groups:
            # print("Group====:", group)
            score = self.llm_layer.score_group(group)
            scores.append(score)
        # best_group = max(candidate_groups, key=lambda x: self.llm_layer.score_group(x))
        best_group = candidate_groups[scores.index(max(scores))]
        return best_group, True  # End turn if retries were exceeded
