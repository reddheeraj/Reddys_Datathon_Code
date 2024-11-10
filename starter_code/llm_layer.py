from groq import Groq
import os
from dotenv import load_dotenv
load_dotenv()

class LLMLayer:
    def __init__(self):
        self.groq_api_key = "key"
        # self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.client = Groq(api_key=self.groq_api_key)

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
                model="llama3-8b-8192",
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
                model="llama3-8b-8192",
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
