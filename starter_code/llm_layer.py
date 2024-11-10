from groq import Groq
import os
from dotenv import load_dotenv
import re
import itertools
import requests
import ollama
load_dotenv()

class LLMLayer:
    def __init__(self):
        self.groq_api_key = "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"
        # self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.client = Groq(api_key=self.groq_api_key)

    def generate_initial_groups(self, words, isOneAway, previousGuesses, strikes, error, wasCorrect):
        """
        Generate initial groups using LLM suggestions based on associations.
        """
        initial_groups = []
        
        print("initial words: ", words, "len: ", len(words))
        # Call LLM to suggest associations and groupings
        prompt = f"Cluster the following {len(words)} words into {len(words)//4} groups where each group contains 4 words: {words}\nConsider semantic, complex, homophones, palindromes etc type of reasoning."
        if len(previousGuesses) > 0:
            previousGuess = previousGuesses[-1]
            previousGuess = ','.join(previousGuess)
            prompt +=f"\nThis was your previous guess:{previousGuess}. "
            if isOneAway:
                prompt += "\nYour previous guess was are one word away from the correct answer. Change one word in your previous guess to get the correct answer."
            if wasCorrect == 1:
                prompt += "\nYour previous guess was correct."
            elif wasCorrect == -1:
                prompt += "\nYour previous guess was wrong."
            previousGuesses = [', '.join(guess) for guess in previousGuesses]
            previousGuesses = '\n'.join(previousGuesses)
            print(previousGuesses)
            prompt += f"\nThese are your previous guesses: \n{previousGuesses}. Do not repeat these combinations in your output.\n"
        prompt +=f"""
            ONLY OUTPUT THE WORDS. DO NOT SAY intro sentences like "here are the words". You should ONLY respond in lines and each line should contain 4 words(not more or not less) separated by a comma and a whitespace. 
            VERY IMPORTANT: You should output ONLY the {len(words)} words into groups. DO NOT USE any other words.
            Your output should contain EXACTLY {len(words)//4} lines.
            (Example format for input and output):
            INPUT:
            ['TWISTED', 'EXPONENT', 'THRONE', 'REST', 'WARPED', 'TRACE', 'BENT', 'OUNCE', 'ROOT', 'GNARLY', 'RADICAL', 'POWDER', 'SHRED', 'LICK', 'POWER', 'BATH']

            OUTPUT:
            TWISTED, WARPED, BENT, GNARLY
            EXPONENT, ROOT, POWER, RADICAL
            THRONE, REST, BATH, POWDER
            OUNCE, TRACE, LICK, SHRED
        """
        prompt = str(prompt)
        while True:
            try:
                
                response = ollama.chat(model = 'llama3.1', messages=[{'role': 'user', 'content': prompt}])
                if 'message' in response.keys():
                    if 'content' in response['message'].keys():
                        response = response['message']['content']
                else:
                    continue
                print("response: ", response)
                # Parse response to form groups
                initial_groups, check = self.parse_response_to_groups(response, len(words))
                if check == True:
                    
                    return initial_groups
                else:
                    continue
            except Exception as e:
                print("Error during initial group generation:", e)
        return initial_groups

    def parse_response_to_groups(self, response, length):
        """
        Parse the response to extract groups of 4 words.
        """
        # Parse groups based on expected format in response
        # Example parsing logic:
        try:
            lines = response.strip().splitlines()
            lines = [line.strip() for line in lines if line and not line.startswith("Here")]
            words = [word for line in lines for word in re.split(r',\s*', line.strip(", "))]
            # words = set(words)
            print("words: ", words)
            if len(words) !=length:
                return [], False
            return [words[i:i + 4] for i in range(0, len(words), 4)], True
        except Exception as e:
            print("Error parsing response to groups:", e)
            return [], False
        
        # return [group.split(', ') for group in response.splitlines() if len(group.split()) == 4]

    def validate_group_with_llm(self, group):
        """
        Send a group of words to the LLM for validation through the Groq API.
        Returns whether the LLM validates this group as correct.
        """

        # Format the group as a prompt for LLM validation
        prompt = f"Are the following words a logically grouped set? Consider semantic, complex, homophones, palindromes etc type of reasoning. {group}.VERY IMPORTANT: Respond with ONLY a 'Yes' or a 'No'. Do not include any other information in your response."
        # global client
        try:
            response = ollama.chat(model = 'llama3.1', messages=[{'role': 'user', 'content': prompt}])
            if 'message' in response.keys():
                    if 'content' in response['message'].keys():
                        response = response['message']['content']
            print('validation: ', response)
            is_valid = "yes" in response or "Yes" in response # Check if LLM responded positively
            return is_valid, group
        except Exception as e:
            print("Error during LLM validation:", e)
            return False, group

    def score_group(self, group):
        """
        Assigns a confidence score to a group by querying the LLM to determine the association strength.
        """

        # Format the group as a prompt for scoring based on similarity or thematic strength
        prompt = f"On a scale from 1 to 10, how well do these words belong together? Consider semantic, complex, homophones, palindromes etc type of reasoning. VERY IMPORTANT: Output only the score without any other information. Group : {group}"
        try:
            # print(self.groq_api_key)
            response = ollama.chat(model = 'llama3.1', messages=[{'role': 'user', 'content': prompt}])
            if 'message' in response.keys():
                    if 'content' in response['message'].keys():
                        response = response['message']['content']
            print('score: ', response)
            try:
                score = int(response)
            except ValueError:
                print("Error parsing score; received response:", response)
                score = 0  # Default to 0 if parsing fails
            return score
        except Exception as e:
            print("Error during LLM scoring:", e)
            return 0  # Return a low score on error