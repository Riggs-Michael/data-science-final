import requests
import pandas as pd
import os
import time

from dotenv import load_dotenv
from ratelimiter import RateLimiter as rl
from json.decoder import JSONDecodeError


class ExpenseException(Exception):
    pass


load_dotenv()
base_api_url = 'https://api.opendota.com/api'
public_matches_endpoint = f'{base_api_url}/publicMatches'
matches_endpoint = f'{base_api_url}/matches'
parsed_matches_endpoint = f'{base_api_url}/parsedMatches'
live_matches_endpoint = f'{base_api_url}/live'
api_key = os.getenv('OPEN_DOTA_API_KEY')
limiter = rl(max_calls=1200, period=60) if api_key is not None else rl(max_calls=60, period=60)
global total_calls
total_calls = 0

brackets = ["herald", "guardian", "crusader", "archon", "legend", "ancient", "divine", "immortal"]

rank_range_parameters = {
    "herald_min": 10,
    "herald_max": 15,
    "guardian_min": 20,
    "guardian_max": 25,
    "crusader_min": 30,
    "crusader_max": 35,
    "archon_min": 40,
    "archon_max":45,
    "legend_min": 50,
    "legend_max": 55,
    "ancient_min": 60,
    "ancient_max": 65,
    "divine_min": 70,
    "divine_max": 75,
    "immortal_min": 80,
    "immortal_max": 85
}


def fetch_public_matches_by_bracket(bracket: str):
    request_params = {
        "min_rank": rank_range_parameters[f'{bracket}_min'],
        "max_rank": rank_range_parameters[f'{bracket}_max'],
        "api_key": api_key
    }
    with limiter:
        api_call_safety_net()
        response = requests.get(public_matches_endpoint, params=request_params)
    results = response.json()
    return results


def fetch_all_brackets_sample_matches():
    match_id = None
    fetch_count = 0
    duplicate_count = 0
    parsed_match_ids = pd.read_csv('parsed_match_ids.csv')
    for bracket in brackets:
        data = {
            "match_id": [],
            "transcript": []
        }
        try:
            while len(data['match_id']) < 1000:
                if fetch_count > 0:
                    time.sleep(61)
                try:
                    public_matches = fetch_public_matches_by_bracket(bracket)
                except JSONDecodeError:
                    print('Skipping empty response.')
                    continue
                fetch_count += 1
                if match_id == public_matches[-1]['match_id']:
                    print(match_id)
                    duplicate_count += 1
                    print(f'{duplicate_count} duplicate public match fetches out of {fetch_count} total')
                    time.sleep(61)
                    continue
                for match in public_matches:
                    match_id = match['match_id']
                    if match_id not in parsed_match_ids['match_id'].values:
                        continue
                    try:
                        match_details = fetch_match_details(match_id)
                    except JSONDecodeError:
                        print('Skipping empty response.')
                        continue
                    if 'chat' in match_details:
                        transcript = match_details['chat']
                    else:
                        continue
                    parsed_transcript = ''
                    for entry in transcript:
                        if entry['type'] == 'chat':
                            player_slot = f'player_slot {entry["player_slot"]}: '
                            message = f'{entry["key"]}\n'
                            parsed_transcript = ''.join([parsed_transcript, player_slot, message])
                    data['match_id'].append(match_id)
                    data['transcript'].append(parsed_transcript)
        finally:
            df = pd.DataFrame(data)
            df.to_excel(f'{bracket}_match_transcripts.xlsx')


def fetch_match_details(match_id: int):
    request_params = {'api_key': api_key}
    with limiter:
        api_call_safety_net()
        response = requests.get(f'{matches_endpoint}/{match_id}', params=request_params)
    results = response.json()
    return results


def fetch_parsed_match_ids(start_before: int):
    if start_before is None:
        with limiter:
            api_call_safety_net()
            response = requests.get(live_matches_endpoint, params={'api_key': api_key})
        results = response.json()
        start_before = results[0]['match_id']
    iterations = 0
    data = {
        "match_id": []
    }
    while start_before is not None and iterations < 246000:
        iterations += 1
        request_params = {
            'less_than_match_id': start_before,
            'api_key': api_key
        }
        with limiter:
            try:
                api_call_safety_net()
            except ExpenseException:
                df = pd.DataFrame(data)
                return df
            response = requests.get(parsed_matches_endpoint, params=request_params)
        results = response.json()
        if len(results) == 0:
            start_before = None
        else:
            for result in results:
                data['match_id'].append(result['match_id'])
            start_before = results[-1]['match_id']
    df = pd.DataFrame(data)
    return df


def api_call_safety_net():
    if api_key is None:
        return
    global total_calls
    total_calls += 1
    if total_calls >= 50000:
        raise ExpenseException('These calls cost money you know!')


if __name__ == '__main__':
    # if os.path.isfile('parsed_match_ids.xlsx'):
    #     spmi = pd.read_excel('parsed_match_ids.xlsx')
    #     starting_match_id = spmi.iloc[-1][0]
    # else:
    #     spmi = pd.DataFrame({"match_id": []})
    #     starting_match_id = None
    # fpmi = fetch_parsed_match_ids(starting_match_id)
    # pmi = pd.concat([spmi, fpmi])
    # pmi.to_csv('parsed_match_ids.csv', index=False)
    fetch_all_brackets_sample_matches()
