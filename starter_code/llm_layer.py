from groq import Groq
import os
from dotenv import load_dotenv
import re
import itertools
load_dotenv()

class LLMLayer:
    def __init__(self):
        self.groq_api_key = "key"
        # self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.client = Groq(api_key=self.groq_api_key)

    def generate_initial_groups(self, words, isOneAway, previousGuesses, strikes, error):
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
            else:
                prompt += "\nYour previous guess was wrong."
            # previousGuesses = [', '.join(guess) for guess in previousGuesses]
            # previousGuesses = '\n'.join(previousGuesses)
            # print(previousGuesses)
            # prompt += f"\nThese are your previous guesses: \n{previousGuesses}. Do not repeat these combinations in your output.\n"
        prompt +="""
            ONLY OUTPUT THE WORDS. DO NOT SAY intro sentences like "here are the words". Just present the words in groups. You should ONLY respond in lines and each line should contain 4 words(not more or not less) separated by a comma and a whitespace. 
            Do not include a comma at the end of the line.\n VERY IMPORTANT: You should output ALL the words into groups.
            VERY IMPORTANT (Example format for input and output):
            INPUT:
            ['TWISTED', 'EXPONENT', 'THRONE', 'REST', 'WARPED', 'TRACE', 'BENT', 'OUNCE', 'ROOT', 'GNARLY', 'RADICAL', 'POWDER', 'SHRED', 'LICK', 'POWER', 'BATH']

            OUTPUT:
            TWISTED, WARPED, BENT, GNARLY
            EXPONENT, ROOT, POWER, RADICAL
            THRONE, REST, BATH, POWDER
            OUNCE, TRACE, LICK, SHRED
        """
        while True:
            try:
                chat_completion = self.client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama3-70b-8192",
                    temperature=0.5,
                    max_tokens=50
                )
                response = chat_completion.choices[0].message.content
                print("response: ", response)
                # Parse response to form groups
                initial_groups, check = self.parse_response_to_groups(response, len(words))
                if check == True:
                    break
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
        prompt = f"Are the following words a logically grouped set? {group}. Respond with 'Yes' or 'No'."
        # global client
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are an assistant that validates word groupings."},
                    {"role": "user", "content": prompt}
                ],
                model="llama3-70b-8192",
                temperature=0.5,
                max_tokens=10,
                top_p=1
            )
            # Get the response from LLM
            response = chat_completion.choices[0].message.content.strip().lower()
            print('validation: ', response)
            is_valid = "yes" in response  # Check if LLM responded positively
            return is_valid, group
        except Exception as e:
            print("Error during LLM validation:", e)
            return False, group

    def score_group(self, group):
        """
        Assigns a confidence score to a group by querying the LLM to determine the association strength.
        """

        # Format the group as a prompt for scoring based on similarity or thematic strength
        prompt = f"On a scale from 1 to 10, how well do these words belong together? Only give the score. group : {group}"
        try:
            # print(self.groq_api_key)
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are an assistant that scores the thematic coherence of word groups."},
                    {"role": "user", "content": prompt}
                ],
                model="llama3-70b-8192",
                temperature=0.5,
                max_tokens=10,
                top_p=1
            )
            # Parse the score from the LLM response
            response = chat_completion.choices[0].message.content.strip()
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