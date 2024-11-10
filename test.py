from groq import Groq

from dotenv import load_dotenv
import os
load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
res = client.chat.completions.create(
    messages=[
        {"role": "system", "content": "You are an assistant that validates word groupings."},
        {"role": "user", "content": "Are the following words a logically grouped set? ['apple', 'banana', 'cherry']. Respond with 'Yes' or 'No'."}
    ],
    model="llama3-8b-8192",
    temperature=0.5,
    max_tokens=10,
    top_p=1
)
res2 = client.chat.completions.create(
    messages=[
        {"role": "system", "content": "You are an assistant that scores the thematic coherence of word groups."},
        {"role": "user", "content": "On a scale from 1 to 10, how well do these words belong together? Only give the score. group=['apple', 'banana', 'cherry']"}
    ],
    model="llama3-8b-8192",
    temperature=0.5,
    max_tokens=10,
    top_p=1
)
print("res1 = ", res.choices[0].message.content.strip().lower())
print("res2 = ", res2.choices[0].message.content.strip())