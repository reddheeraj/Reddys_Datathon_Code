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
                prompt += "\nYour previous guess was are one word away from the correct answer. Change EXACTLY ONE word(no more or less) in your previous guess to get a correct group."
            if wasCorrect == 1:
                prompt += "\nYour previous guess was correct."
            elif wasCorrect == -1:
                prompt += "\nYour previous guess was wrong."
            previousGuesses = [', '.join(guess) for guess in previousGuesses]
            previousGuesses = '\n'.join(previousGuesses)
            print(previousGuesses)
            prompt += f"\nThese are your previous guesses: \n{previousGuesses}. DO NOT consider these combinations.\n"
        prompt +=f"""
            VERY IMPORTANT:Instructions for the output:
                1. Output only the given words, grouped into lines.
                2. Each line should contain exactly four words, separated by a comma and a space.
                3. Do not include any introductory sentences or additional words.
                4. Use all the provided words; do not add or omit any.
                5. The output should contain exactly {len(words) // 4} lines.
                6. Do not include any other text. This is the MOST IMPORTANT INSTRUCTION.
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
                initial_groups, check = self.parse_response_to_groups(response, words)
                if check == True:
                    
                    return initial_groups
                else:
                    continue
            except Exception as e:
                print("Error during initial group generation:", e)
        return initial_groups

    def parse_response_to_groups(self, response, words):
        """
        Parse the response to extract groups of 4 words.
        """
        # Parse groups based on expected format in response
        # Example parsing logic:
        try:
            lines = response.strip().splitlines()
            lines = [line.strip() for line in lines if line and not line.startswith("Here")]
            response_words = [word.strip() for line in lines for word in re.split(r',', line.strip(", "))]
            # words = set(words)
            
            if len(response_words) < len(words):
                omitted_words = [word for word in words if word not in response_words]
                # append only len(words) - len(response_words) words
                response_words += omitted_words[:len(words) - len(response_words)]
                # return [response_words[i:i + 4] for i in range(0, len(response_words), 4)], True
            elif len(response_words) > len(words):
                return [], False
            print("words: ", response_words)
            return [response_words[i:i + 4] for i in range(0, len(response_words), 4)], True
        except Exception as e:
            print("Error parsing response to groups:", e)
            return [], False
        
        # return [group.split(', ') for group in response.splitlines() if len(group.split()) == 4]

    def group_isOneAway(self, words, previousGuesses):
        previousGuess = previousGuesses[-1]
        previousGuess = ','.join(previousGuess)
        remaining_words = [word for word in words if word not in previousGuess]
        prompt =f"You are one word away from the correct answer! Your previous guess was {previousGuess}. Identify exactly ONE WORD in the remaining list: {remaining_words} and in the previous guess to swap to get the correct group with some complex reasoning. Consider semantic, complex, homophones, palindromes, rhyming etc type of reasoning." 
        previousGuesses = [', '.join(guess) for guess in previousGuesses]
        previousGuesses = '\n'.join(previousGuesses)
        prompt += f"\nThese are your previous guesses: \n{previousGuesses}. DO NOT consider these combinations.\n"
        prompt +=f"""
            OUTPUT INSTRUCTIONS:
            1. Output a single line with 4 words separated by a comma and a space.
            2. Do not include any introductory sentences or additional words.
            3. Do not include any other text. This is the MOST IMPORTANT INSTRUCTION.

            Example Output:
            TWISTED, WARPED, BENT, GNARLY
        """
        while(True):
            try:
                response = ollama.chat(model = 'llama3.1', messages=[{'role': 'user', 'content': prompt}])
                if 'message' in response.keys():
                    if 'content' in response['message'].keys():
                        response = response['message']['content']
                else:
                    continue
                print("response: ", response)
                # Parse response to form groups
                lines = response.strip().splitlines()
                lines = [line.strip() for line in lines if line and not line.startswith("Here")]
                response_words = [word.strip() for line in lines for word in re.split(r',', line.strip(", "))]
                if len(response_words) != 4:
                    continue
                else:
                    return response_words
            except Exception as e:
                print("Error parsing response to groups:", e)
                return []

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