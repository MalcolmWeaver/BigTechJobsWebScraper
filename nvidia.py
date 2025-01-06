import requests
from datetime import datetime
import os

url = "https://nvidia.wd5.myworkdayjobs.com/wday/cxs/nvidia/NVIDIAExternalCareerSite/jobs"

def get_postings():

    all_postings = set()
    offset = 0
    limit = 20

    while True:

        headers = {
            "content-type": "application/json"
        }

        payload = {
            "appliedFacets": {
                "locations": [
                    "91336993fab910af6d702fae0bb4c2e8",
                    "91336993fab910af6d716528e9d4c406",
                    "91336993fab910af6d7169a81124c410",
                    "91336993fab910af6d702939a7fcc2d9",
                    "91336993fab910af6d702b631b94c2de",
                    "91336993fab910af6d701e82d004c2c0",
                    "d2088e737cbb01d5e2be9e52ce01926f"
                ],
                "jobFamilyGroup": ["0c40f6bd1d8f10ae43ffaefd46dc7e78"]
            },
            "limit": limit,
            "offset": offset,
            "searchText": ""
        }

        print(f"Getting postings from {offset} to {offset + limit}")
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            data = response.json()
            if not data.get('jobPostings'):  # If no more job postings
                break

            l = len(all_postings)
            all_postings.update([posting['externalPath'] for posting in data['jobPostings']])
            if len(all_postings) == l:
                break
            offset += limit


        else:
            print(f"Error: {response.status_code}")
            break

    return all_postings

def get_description(posting_slug):
    url = f"https://nvidia.wd5.myworkdayjobs.com/wday/cxs/nvidia/NVIDIAExternalCareerSite/{posting_slug}"
    response = requests.get(url)
    return response.text

def filter_posting(posting_description):
    # title, years of experience
    return True

def get_all_postings_to_apply():
    all_postings_to_apply = []
    all_postings = get_postings()

    # Create output directory if it doesn't exist
    output_dir = "nvidia_postings"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Generate filename with current date
    current_date = datetime.now().strftime("%Y-%m-%d")
    output_file = os.path.join(output_dir, f"nvidia_filtered_postings_{current_date}.txt")

    # Open file in append mode
    with open(output_file, "a") as f:
        for posting_slug in list(all_postings)[:10]:
            posting_description = get_description(posting_slug)
            if filter_posting(posting_description):
                all_postings_to_apply.append(posting_slug)
                f.write(f"https://nvidia.wd5.myworkdayjobs.com/en-US/NVIDIAExternalCareerSite{posting_slug}\n")

    return all_postings_to_apply


# TODO: auto apply (login, apply)
if __name__ == "__main__":
    # all_postings = get_postings()
    # print(all_postings)
    # print(len(all_postings))
    # posting_slug = "/job/US-CA-Santa-Clara/Senior-Software-Architect--Advanced-Development_JR1990924"
    # print(get_description(posting_slug))

    get_all_postings_to_apply()