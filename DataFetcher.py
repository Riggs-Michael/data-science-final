import requests
import pandas as pd

public_matches_endpoint = 'https://api.opendota.com/api/publicMatches'
matches_endpoint = 'https://api.opendota.com/api/matches'

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
    # TODO: Need to include the less_than_match_id parameter, and specify a match id from sometime far enough back
    # that matches returned will be guaranteed to have been parsed. Without specifying, we can get matches that
    # haven't yet been parsed and thus will not have the chat in the details.
    request_params = {
        "min_rank": rank_range_parameters[f'{bracket}_min'],
        "max_rank": rank_range_parameters[f'{bracket}_max']
    }
    response = requests.get(public_matches_endpoint, params=request_params)
    results = response.json()
    return results


def fetch_all_brackets_sample_matches():
    for bracket in brackets:
        df = pd.DataFrame({'match_id': [], 'transcript': []})
        public_matches = fetch_public_matches_by_bracket(bracket)
        for match in public_matches:
            match_id = match['match_id']
            match_details = fetch_match_details(match_id)
            transcript = match_details['chat']
            df.append({'match_id': match_id, 'transcript': transcript}, ignore_index=True)
        df.to_excel(f'{bracket}_match_transcripts')


def fetch_match_details(match_id: int):
    response = requests.get(f'{matches_endpoint}/{match_id}')
    results = response.json()
    return results


if __name__ == '__main__':
    fetch_all_brackets_sample_matches()
