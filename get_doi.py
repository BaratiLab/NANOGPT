import requests

def get_doi_from_title(title):
    url = "https://api.crossref.org/works"
    params = {
        "query.title": title,
        "rows": 1
    }

    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        if data['message']['items']:
            doi = data['message']['items'][0]['DOI']
            return doi
        else:
            return "DOI not found."
    else:
        return f"Error: {response.status_code}"
