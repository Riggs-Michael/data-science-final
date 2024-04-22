import openai
import pandas as pd
from dotenv import load_dotenv
from ratelimiter import RateLimiter as rl

gpt_model = "gpt-4-turbo-2024-04-09"
prompt = '''
You are a community moderator for the game Dota 2. You are analyzing chat logs from matches to determine the level
of toxicity in the match and classifying them into one of five categories. The five categories are: No Toxicity, 
Low Toxicity, Mild Toxicity, Moderate Toxicity, Extreme Toxicity. If you are unable to determine a toxicity level, 
say Undetermined. Only respond with one of the categories or Undetermined.'''

match_template = '''
Match Id: %s  
Chat Log: %s

The classification is:
'''
brackets = ["herald", "guardian", "crusader", "archon", "legend", "ancient", "divine", "immortal"]

load_dotenv()
client = openai.OpenAI()
limiter = rl(max_calls=500, period=60)


def classify_chat_log_toxicity(match_id, log):
    match_prompt = match_template % (match_id, log)
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": match_prompt}]
    with limiter:
        response = openai.chat.completions.create(
            messages=messages,
            temperature=0,
            max_tokens=5,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            model=gpt_model,
            seed=42)
        result = response.choices[0].message.content.replace('\n', '')
        return result


def get_classification_ranking(classification):
    value = 0
    if classification == 'No Toxicity':
        value = 1
    elif classification == 'Low Toxicity':
        value = 2
    elif classification == 'Mild Toxicity':
        value = 3
    elif classification == 'Moderate Toxicity':
        value = 4
    elif classification == 'Extreme Toxicity':
        value = 5
    return value


if __name__ == '__main__':
    for bracket in brackets:
        labeled_data = []
        df = pd.read_csv(f'{bracket}_match_transcripts.csv')
        for item in df.iterrows():
            match = item[1]
            classification = classify_chat_log_toxicity(match['match_id'], match['transcript'])
            classification_ranking = get_classification_ranking(classification)
            labeled_data.append([match['match_id'], match['transcript'], classification, classification_ranking])
        output = pd.DataFrame.from_records(data=labeled_data,
                                           columns=['Match Id', 'Transcript', 'Toxicity', 'Toxicity Ranking'])
        output.to_csv(f'labeled_{bracket}_match_transcripts.csv', index=False)
