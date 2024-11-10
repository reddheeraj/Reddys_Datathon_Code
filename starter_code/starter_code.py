# from .grouping_manager import GroupingManager
from .aggregator import Aggregator
from .block import Block
import os
import ast
from .grouping_manager import GroupingManager
from dotenv import load_dotenv


load_dotenv()


def model(words, strikes, isOneAway, correctGroups, previousGuesses, error):
	"""
	_______________________________________________________
	Parameters:
	words - 1D Array with 16 shuffled words
	strikes - Integer with number of strikes
	isOneAway - Boolean if your previous guess is one word away from the correct answer
	correctGroups - 2D Array with groups previously guessed correctly
	previousGuesses - 2D Array with previous guesses
	error - String with error message (0 if no error)

	Returns:
	guess - 1D Array with 4 words
	endTurn - Boolean if you want to end the puzzle
	_______________________________________________________
	"""

	# Your Code here
	# Good Luck!
	words = ast.literal_eval(words)

	grouping_manager = GroupingManager(words)

    # Create a Block to handle NLP and LLM processing
	block = Block()

	# Use the Aggregator to resolve groups
	aggregator = Aggregator([block])

	# Get the best candidate groups from the GroupingManager
	best_group, endTurn = grouping_manager.get_best_group()

	# If we have a valid best group, start processing the next guess
	if best_group:
		guess = best_group
	else:
		guess = []
	# print("Guess before model:", guess)
	# print("best_group:", best_group)
	# Aggregator resolves and selects the best group based on current conditions
	resolved_group = aggregator.resolve_groups([best_group], previousGuesses, strikes, isOneAway, correctGroups)

	# If a valid group is resolved, return it
	if resolved_group:
		guess = resolved_group
	print("Guess inside model:", guess)
	return guess, endTurn
