from typing import List, Optional, Dict
import requests
import json
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
LOCATION = {
    "Los Angeles": "los-angeles",
    "New York": "new-york",
    "San Francisco": "san-francisco",
    "Seattle": "seattle",
    "Boston": "boston",
    "Chicago": "chicago",
    "Denver": "denver",
    "Austin": "austin",
    "District of Columbia": "district-of-columbia",
}

TITLE = {
    "Software Engineer": "software-engineer",
    "Engineering Manager": "engineering-manager",
    "Artificial Intelligence Engineer": "artificial-intelligence-engineer",
    "Machine Learning Engineer": "machine-learning-engineer",
    "Backend Engineer": "backend-engineer",
    "Mobile Engineer": "mobile-engineer",
    "Product Designer": "product-designer",
    "Frontend Engineer": "frontend-engineer",
    "Data Scientist": "data-scientist",
    "Full Stack Engineer": "full-stack-engineer",
    "Product Manager": "product-manager",
    "Designer": "designer",
    "Software Architect": "software-architect",
    "DevOps Engineer": "devops-engineer",
}


def sanitize_string(input_string: str) -> str:
    # Replace Unicode escape sequences with their actual characters
    sanitized_string = input_string.encode('utf-8').decode('unicode_escape')

    # Remove any unwanted characters (e.g., non-printable characters)
    sanitized_string = re.sub(r'[^\x20-\x7E]', '', sanitized_string)

    # Replace multiple spaces with a single space
    sanitized_string = re.sub(r'\s+', ' ', sanitized_string).strip()

    return sanitized_string

def parse_relative_date(relative_date: str) -> str:
    today = datetime.today()
    if 'day' in relative_date:
        days = int(re.search(r'\d+', relative_date).group())
        return (today - timedelta(days=days)).strftime('%Y-%m-%d')
    elif 'week' in relative_date:
        weeks = int(re.search(r'\d+', relative_date).group())
        return (today - timedelta(weeks=weeks)).strftime('%Y-%m-%d')
    elif 'month' in relative_date:
        months = int(re.search(r'\d+', relative_date).group())
        return (today - timedelta(days=months*30)).strftime('%Y-%m-%d')
    elif 'year' in relative_date:
        years = int(re.search(r'\d+', relative_date).group())
        return (today - timedelta(days=years*365)).strftime('%Y-%m-%d')
    return today.strftime('%Y-%m-%d')

def parse_jobs(url: str) -> List[Dict[str, str]]:
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    job_listings = []

    job_elements = soup.find_all("div", class_="mb-6 w-full rounded border border-gray-400 bg-white")
    for job_element in job_elements:
        job = {}
        job['title'] = job_element.find("a",
                                        class_="mr-2 text-sm font-semibold text-brand-burgandy hover:underline").text.strip()
        job['type'] = job_element.find("span",
                                       class_="whitespace-nowrap rounded-lg bg-accent-yellow-100 px-2 py-1 text-[10px] font-semibold text-neutral-800").text.strip()
        job['salary'] = sanitize_string(job_element.find("div", class_="flex items-center text-neutral-500").find("span",
                                                                                                  class_="pl-1 text-xs").text.strip())
        job['company'] = job_element.find("h2", class_="inline text-md font-semibold").text.strip()
        company_image = job_element.find("img")['src']
        job["company_image"] = re.search(r'https://[^\s]+', company_image).group(0) if company_image else "N/A"
        relative_posted_date = job_element.find("span", class_="text-xs lowercase text-dark-a mr-2 hidden flex-wrap content-center md:flex").text.strip()
        job['posted_date'] = parse_relative_date(relative_posted_date)
        location_elements = job_element.find_all("div", class_="flex items-center text-neutral-500")
        if len(location_elements) > 1:
            job['location'] = sanitize_string(location_elements[1].find("span", class_="pl-1 text-xs").text.strip())
        else:
            job['location'] = 'N/A'
        posting_url = job_element.find("a", class_="mr-2 text-sm font-semibold text-brand-burgandy hover:underline")['href']
        job['posting_url'] = f"https://wellfound.com{posting_url}" if posting_url else "N/A"
        # if len(location_elements) > 2:
        #     job['experience'] = location_elements[2].find("span", class_="pl-1 text-xs").text.strip()
        # else:
        #     job['experience'] = 'N/A'


        job_listings.append(job)

    return job_listings


def search_jobs(job_title: str, job_location: Optional[str] = None) -> Optional[List[str]]:
    if not job_title:
        raise ValueError("Job title is required.")

    if job_location is None:
        URL = f"https://wellfound.com/role/{TITLE[job_title]}"
        print(URL)
        jobs = parse_jobs(URL)
        save_to_json(jobs, f"{job_title}_all_locations.json")
        return json.dumps(jobs, indent=4)

    if job_location not in LOCATION:
        print(f"Location '{job_location}' is not recognized.")
        return None
    if job_title not in TITLE:
        print(f"Job title '{job_title}' is not recognized.")
        return None

    URL = f"https://wellfound.com/role/l/{TITLE[job_title]}/{LOCATION[job_location]}"
    print(URL)

    jobs = parse_jobs(URL)
    save_to_json(jobs, f"{job_title}_{job_location}.json")

    return json.dumps(jobs, indent=4)


def save_to_json(data: List[Dict[str, str]], filename: str):
    with open(filename, 'w') as json_file:
        json.dump(data, json_file, indent=4)
        print(f"Saved results to {filename}")


if __name__ == '__main__':

    # results_all_locations = search_jobs("Software Engineer")
    results_all_locations = search_jobs("Software Engineer", "Los Angeles")
    if results_all_locations:
        print("Job Listings in All Locations:")
        print(results_all_locations)