from .nlp_layer import NLPLayer
from .llm_layer import LLMLayer

MAX_RETRIES = 6  # Maximum attempts for re-evaluation of groups

class GroupingManager:
    def __init__(self, words, isOneAway, previousGuesses, strikes, error, wasCorrect):
        self.words = words
        self.nlp_layer = NLPLayer()
        
        self.invalid_words = set()  # Track invalid words from flagged groups
        self.retries = 0  # Counter for re-evaluation attempts
        self.isOneAway = isOneAway
        self.wasCorrect = wasCorrect
        self.previousGuesses = previousGuesses
        self.strikes = strikes
        self.error = error
        self.llm_layer = LLMLayer()
    
    def get_best_group(self):
        """
        Generate and evaluate groups using the NLP and LLM layers. If the LLM layer detects an invalid group,
        it triggers re-evaluation with filtered candidate groups.
        """
        if self.isOneAway:
            return self.llm_layer.group_isOneAway(self.words, self.previousGuesses), False  # Return the one-away group, do not end turn
        initial_groups = self.llm_layer.generate_initial_groups(self.words, self.isOneAway, self.previousGuesses, self.strikes, self.error, self.wasCorrect)
        print("Initial groups:", initial_groups)
        refined_groups = self.nlp_layer.refine_groups(initial_groups)
        # print('------>',candidate_groups)

        # Fallback to highest scoring group if retries are exhausted
        scores = [self.llm_layer.score_group(group) for group in refined_groups]
        print("refined groups: ", refined_groups)
        print("scores: ", scores)
        best_group = refined_groups[scores.index(max(scores))]
        sorted_pairs = sorted(zip(scores, refined_groups), reverse=True)
        scores, refined_groups = zip(*sorted_pairs)
        for group in refined_groups:
            if self.retries >= MAX_RETRIES:
                break
            
            # Validate the group using LLM
            is_valid, validated_group = self.llm_layer.validate_group_with_llm(group)
            print("Validated group:", validated_group)
            print("is valid: ", is_valid)
            if is_valid:
                print("is valid: ", validated_group)
                return validated_group, False  # Return the validated group, do not end turn
            
                # Update invalid words and refine candidate groups
            # self.invalid_words.update(validated_group)
            # refined_groups = [g for g in refined_groups if not any(w in self.invalid_words for w in g)]
            self.retries += 1  # Increase re-evaluation count
        return best_group, False  # Return the best group, end turn

