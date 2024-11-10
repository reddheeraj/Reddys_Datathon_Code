# from .grouping_manager import GroupingManager
from .aggregator import Aggregator
from .block import Block
import os
import ast
from .grouping_manager import GroupingManager
from dotenv import load_dotenv


load_dotenv()
prev_len = 0

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
	global prev_len
	# Your Code here
	# Good Luck!
	print("correctGroups in starter_code.py:", correctGroups)
	words = ast.literal_eval(words)
	wasCorrect = -1
	if len(correctGroups)>prev_len:
		wasCorrect = 1
	elif len(correctGroups) == 0 and len(previousGuesses) == 0:
		wasCorrect = 0
	if len(correctGroups) > 0:
		# remove corrected groups from words
		wasCorrect = 1
		for group in correctGroups:
			for word in group:
				if word in words:
					words.remove(word)
	prev_len = len(correctGroups)
	if len(words) == 4:
		return words, True
	
	
	grouping_manager = GroupingManager(words, isOneAway, previousGuesses,strikes, error, wasCorrect)

    # Create a Block to handle NLP and LLM processing
	block = Block()

	# Use the Aggregator to resolve groups
	aggregator = Aggregator([block])

	# Get the best candidate groups from the GroupingManager
	best_group, endTurn = grouping_manager.get_best_group()
	print("Best group in starter_code.py:", best_group)
	# If we have a valid best group, start processing the next guess
	if best_group:
		guess = best_group
	else:
		guess = []
	# print("Guess before model:", guess)
	# print("best_group:", best_group)
	# Aggregator resolves and selects the best group based on current conditions
	resolved_group = aggregator.resolve_groups([best_group], previousGuesses, strikes, isOneAway, correctGroups)
	for i in range(len(resolved_group)):
		resolved_group[i] = resolved_group[i].replace(',','').strip()

	# If a valid group is resolved, return it
	if resolved_group:
		guess = resolved_group
	print("Guess inside model:", guess)
	return guess, endTurn

