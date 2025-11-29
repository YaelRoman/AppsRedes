# pip install requests
import json
import requests
from typing import Dict, Any, List

BASE_URL = "https://swapi.dev/api/starships/"

def get_starships_page(page: int = 1) -> Dict[str, Any]:
    """
    GET one page from SWAPI starships.
    Returns a Python dict with keys like: count, next, previous, results.
    """
    resp = requests.get(
        BASE_URL,
        params={"page": page},
        headers={"Accept": "application/json", "User-Agent": "requests-example"},
        timeout=10
    )
    resp.raise_for_status()       # raises if HTTP error
    return resp.json()            # <-- dict (already parsed from JSON)

def get_all_starships() -> List[Dict[str, Any]]:
    """
    Walks pagination until 'next' is None and returns a list of starship dicts.
    """
    url = BASE_URL
    all_ships: List[Dict[str, Any]] = []
    while url:
        resp = requests.get(url, headers={"Accept": "application/json"}, timeout=10)
        resp.raise_for_status()
        data = resp.json()        # dict
        all_ships.extend(data.get("results", []))
        url = data.get("next")    # next page URL (or None)
    return all_ships

if __name__ == "__main__":
    # --- As Python dictionary ---
    page1_dict = get_starships_page(page=1)
    print("Type:", type(page1_dict))
    print("Keys:", list(page1_dict.keys()))  # e.g., ['count', 'next', 'previous', 'results']

    # --- As JSON string (pretty) ---
    page1_json_str = json.dumps(page1_dict, indent=2, ensure_ascii=False)
    print(page1_json_str)

    # --- (Optional) Fetch ALL starships across pages ---
    all_starships = get_all_starships()
    print(f"Total starships fetched: {len(all_starships)}")
    print("Example names:", [s["name"] for s in all_starships[:5]])
