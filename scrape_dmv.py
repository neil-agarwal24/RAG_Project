import requests
from bs4 import BeautifulSoup
import json
import time


urls = [
    "https://www.dmv.ca.gov/portal/handbook/california-driver-handbook/dmv-services/",
    "https://www.dmv.ca.gov/portal/handbook/california-driver-handbook/the-california-driver-license/",
    "https://www.dmv.ca.gov/portal/handbook/california-driver-handbook/getting-an-instruction-permit-and-drivers-license/",
    "https://www.dmv.ca.gov/portal/handbook/california-driver-handbook/the-testing-process/",
    "https://www.dmv.ca.gov/portal/handbook/california-driver-handbook/changing-replacing-and-renewing-your-drivers-license/",
    "https://www.dmv.ca.gov/portal/handbook/california-driver-handbook/introduction-to-driving/",
    "https://www.dmv.ca.gov/portal/handbook/california-driver-handbook/navigating-the-roads/",
    "https://www.dmv.ca.gov/portal/handbook/california-driver-handbook/navigating-the-roads-cont1/",
    "https://www.dmv.ca.gov/portal/handbook/california-driver-handbook/laws-and-rules-of-the-road/",
    "https://www.dmv.ca.gov/portal/handbook/california-driver-handbook/laws-and-rules-of-the-road-cont1/",
    "https://www.dmv.ca.gov/portal/handbook/california-driver-handbook/laws-and-rules-of-the-road-cont2/",
    "https://www.dmv.ca.gov/portal/handbook/california-driver-handbook/safe-driving/",
    "https://www.dmv.ca.gov/portal/handbook/california-driver-handbook/safe-driving-cont1/",
    "https://www.dmv.ca.gov/portal/handbook/california-driver-handbook/safe-driving-cont2/",
    "https://www.dmv.ca.gov/portal/handbook/california-driver-handbook/alcohol-and-drugs/",
    "https://www.dmv.ca.gov/portal/handbook/california-driver-handbook/financial-responsibility-insurance-requirements-and-collisions/",
    "https://www.dmv.ca.gov/portal/handbook/california-driver-handbook/vehicle-registration-requirements/",
    "https://www.dmv.ca.gov/portal/handbook/california-driver-handbook/driver-safety/",
    "https://www.dmv.ca.gov/portal/handbook/california-driver-handbook/seniors-and-driving/",
    "https://www.dmv.ca.gov/portal/handbook/california-driver-handbook/glossary/",

    "https://www.dmv.ca.gov/portal/driver-education-and-safety/educational-materials/",
    "https://www.dmv.ca.gov/portal/driver-education-and-safety/educational-materials/sample-driver-license-dl-knowledge-tests/",
    "https://www.dmv.ca.gov/portal/driver-education-and-safety/educational-materials/videos-2/",
    "https://www.dmv.ca.gov/portal/driver-education-and-safety/educational-materials/fast-facts/what-you-need-to-know-when-buying-a-vehicle-ffvr-26/",

    "https://www.dmv.ca.gov/portal/driver-education-and-safety/",
    "https://www.dmv.ca.gov/portal/driver-education-and-safety/dmv-safety-guidelines-actions/",
    "https://www.dmv.ca.gov/portal/driver-education-and-safety/driver-safety-offices/",
    "https://www.dmv.ca.gov/portal/driver-education-and-safety/driver-training-schools/",
    "https://www.dmv.ca.gov/portal/driver-education-and-safety/medical-conditions-and-driving/",
    "https://www.dmv.ca.gov/portal/driver-education-and-safety/online-learning-and-tests/",
    

    "https://www.dmv.ca.gov/portal/driver-education-and-safety/special-interest-driver-guides/",
    "https://www.dmv.ca.gov/portal/driver-education-and-safety/special-interest-driver-guides/bicyclists-pedestrians/",
    "https://www.dmv.ca.gov/portal/driver-education-and-safety/special-interest-driver-guides/boat-vessel-owners/",
    "https://www.dmv.ca.gov/portal/driver-education-and-safety/special-interest-driver-guides/motorcyclists-guide/",
    "https://www.dmv.ca.gov/portal/driver-education-and-safety/special-interest-driver-guides/moving-out-of-state/",
    "https://www.dmv.ca.gov/portal/driver-education-and-safety/special-interest-driver-guides/new-to-california/",
    "https://www.dmv.ca.gov/portal/driver-education-and-safety/special-interest-driver-guides/people-with-disabilities/",
    "https://www.dmv.ca.gov/portal/driver-education-and-safety/special-interest-driver-guides/senior-drivers/",
    "https://www.dmv.ca.gov/portal/driver-education-and-safety/special-interest-driver-guides/truck-drivers/",
    "https://www.dmv.ca.gov/portal/driver-education-and-safety/special-interest-driver-guides/veterans-and-active-duty-military/",
    "https://www.dmv.ca.gov/portal/driver-education-and-safety/special-interest-driver-guides/teen-drivers/",
    
    "https://www.dmv.ca.gov/portal/teen-drivers/",
]

all_data = []
chunk_id = 0

print("Starting scrape...")

for url in urls:
    print(f"Scraping: {url}")
    
    headers = {"User-Agent": "StudentRAGProject/1.0"}
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            
            # Find the main content area
            main_content = soup.find("main") or soup.find("article") or soup.find("div", class_="content")
            
            if main_content:
                # Get page title
                page_title = soup.find("h1")
                title_text = page_title.get_text().strip() if page_title else "Untitled"
                
                # Get intro text before first h2
                intro_elements = []
                for element in main_content.children:
                    if hasattr(element, 'name'):
                        if element.name == 'h2':
                            break
                        if element.name in ['p', 'ul', 'ol']:
                            text = element.get_text().strip()
                            if text:
                                intro_elements.append(text)

                if intro_elements:
                    intro_content = "\n".join(intro_elements)
                    if len(intro_content.split()) >= 20:  # Only if substantial
                        chunk_id += 1
                        all_data.append({
                            "chunk_id": chunk_id,
                            "url": url,
                            "page_title": title_text,
                            "section_title": "Introduction",
                            "content": intro_content,
                            "word_count": len(intro_content.split())
                        })

                # Find all sections (h2 + following content)
                sections = main_content.find_all("h2")
                
                for section in sections:
                    section_title = section.get_text().strip()
                    
                    # Skip "Additional Formats" sections
                    if section_title == "Additional Formats":
                        continue
                    
                    # Collect content with chunking
                    current_chunk = []
                    word_count = 0
                    
                    for sibling in section.find_next_siblings():
                        if sibling.name == "h2":
                            break
                        if sibling.name in ["p", "ul", "ol"]:
                            text = sibling.get_text().strip()
                            text_words = len(text.split())
                            
                            # If adding this would exceed 500 words, save current chunk
                            if word_count + text_words > 500 and current_chunk:
                                chunk_id += 1
                                all_data.append({
                                    "chunk_id": chunk_id,
                                    "url": url,
                                    "page_title": title_text,
                                    "section_title": section_title,
                                    "content": "\n".join(current_chunk),
                                    "word_count": word_count
                                })
                                current_chunk = []
                                word_count = 0
                            
                            current_chunk.append(text)
                            word_count += text_words

                    # Save any remaining content
                    if current_chunk:
                        chunk_id += 1
                        all_data.append({
                            "chunk_id": chunk_id,
                            "url": url,
                            "page_title": title_text,
                            "section_title": section_title,
                            "content": "\n".join(current_chunk),
                            "word_count": word_count
                        })
                
                print(f" -> Success: {len(sections)} sections found")
            else:
                print(" -> No main content found")
        else:
            print(f" -> Failed: Status {response.status_code}")
            
    except Exception as e:
        print(f" -> Error: {e}")
    
    time.sleep(2)

# Combine small chunks with previous chunk
improved_data = []
for i, chunk in enumerate(all_data):
    if chunk["word_count"] < 50 and improved_data:
        # Merge with previous chunk
        prev = improved_data[-1]
        if prev["url"] == chunk["url"] and prev["page_title"] == chunk["page_title"]:
            prev["content"] += "\n" + chunk["content"]
            prev["word_count"] += chunk["word_count"]
            continue
    improved_data.append(chunk)

all_data = improved_data

# Save to JSON
with open("dmv_handbook_data.json", "w", encoding="utf-8") as f:
    json.dump(all_data, f, indent=2, ensure_ascii=False)

print(f"\nDone! Scraped {len(all_data)} chunks from {len(urls)} pages")
print("Saved to: dmv_handbook_data.json")