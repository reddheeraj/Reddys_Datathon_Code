from .utils import log

def refine_guesses(current_guess, strikes, is_one_away, correct_groups, previous_guesses):
    """Refine guesses based on feedback from the game."""
    
    # Initialize refined_guess to current_guess
    refined_guess = current_guess[:]
    
    # 1. Process "One Word Away" Feedback
    if is_one_away:
        log("Previous guess was one word away from the correct answer.")
        refined_guess = refine_one_away_guess(refined_guess, correct_groups, previous_guesses)
    
    # 2. Process Strikes
    elif strikes > 0:
        log(f"Current guess incurred {strikes} strikes. Refining by adjusting guesses.")
        refined_guess = refine_based_on_strikes(refined_guess, previous_guesses)
    
    # 3. Final Refinement Based on Correct Groups
    refined_guess = ensure_no_overlap_with_correct_groups(refined_guess, correct_groups)
    
    log(f"Refined guess: {refined_guess}")
    return refined_guess


def refine_one_away_guess(guess, correct_groups, previous_guesses):
    """
    Modify a guess if it is "one word away" from being correct by replacing one word.
    """
    for i in range(len(guess)):
        modified_guess = guess[:i] + guess[i + 1:]  # Remove one word to test other replacements
        # Replace missing spot with words not yet in previous guesses
        for word in set(correct_groups) - set(modified_guess) - set(previous_guesses):
            new_guess = modified_guess + [word]
            if new_guess not in previous_guesses:
                log(f"Refining 'one away' guess by replacing with: {new_guess}")
                return new_guess
    return guess


def refine_based_on_strikes(guess, previous_guesses):
    """
    Adjust guess if it has incurred strikes, avoiding known incorrect groups.
    """
    refined_guess = [word for word in guess if word not in previous_guesses]
    if len(refined_guess) < len(guess):
        log("Removing previously guessed incorrect words.")
    return refined_guess


def ensure_no_overlap_with_correct_groups(guess, correct_groups):
    """
    Ensure the guess does not overlap with already confirmed correct groups.
    """
    refined_guess = [word for word in guess if word not in correct_groups]
    if len(refined_guess) < len(guess):
        log("Removing words that overlap with correct groups.")
    return refined_guess
