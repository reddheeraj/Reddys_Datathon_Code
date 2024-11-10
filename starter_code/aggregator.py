# class Aggregator:
#     def __init__(self, blocks):
#         self.blocks = blocks

#     def resolve_groups(self, group_candidates, previous_guesses, strikes, is_one_away, correctGroups):
#         # Aggregate candidates from each block
#         candidate_groups = []
#         print("Group candidates:", group_candidates)
#         for group in group_candidates:
#                 if group not in previous_guesses and group not in correctGroups:
#                     candidate_groups.append(group)
        
#         # If "isOneAway", prioritize groups that differ slightly from previous guesses
#         if is_one_away:
#             candidate_groups.sort(key=lambda g: len(set(g) - set(previous_guesses[-1])), reverse=True)
        
#         # Return the top candidate that has not been guessed
#         return candidate_groups[0] if candidate_groups else previous_guesses[-1] if previous_guesses else []


class Aggregator:
    def __init__(self, blocks):
        self.blocks = blocks

    def resolve_groups(self, group_candidates, previous_guesses, strikes, is_one_away, correct_groups):
        candidate_groups = [group for group in group_candidates
                            if group not in previous_guesses and group not in correct_groups]
        
        if is_one_away:
            candidate_groups.sort(key=lambda g: len(set(g) - set(previous_guesses[-1])), reverse=True)
        
        return candidate_groups[0] if candidate_groups else previous_guesses[-1] if previous_guesses else []
