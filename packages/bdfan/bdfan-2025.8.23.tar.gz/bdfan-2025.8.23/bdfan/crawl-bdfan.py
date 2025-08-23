import json
import re
from bs4 import BeautifulSoup
from typing import Dict, List, Any, Optional
from hypy_utils.tqdm_utils import tmap
from pathlib import Path
import requests

r_html_birthday = re.compile(r'data-pid="(\d+)".*?<b>(.+)?</b>.*?_blank">(.+)?</a>')
r_html_history = re.compile(r'(\d+)年.*?>(.+)?[\n <]')
r_html_people = re.compile(r'(\d+)年　(.+)?（(.+)?）')


def parse_birthday_page(html_string: str) -> Dict[str, Any]:
    soup = BeautifulSoup(html_string, 'html.parser')

    form = soup.find('form')

    # day note: second h2
    h2s = form.find_all('h2')
    for br in h2s[1].find_all("br"):
        br.replace_with("\n")
    day_note = '\n'.join([line.strip() for line in h2s[1].get_text().splitlines()])

    # birthdays, first h6
    h6s = form.find_all('h6')
    html = h6s[0].decode_contents()
    matches = r_html_birthday.findall(html)
    birthdays = [[int(pid), name.strip(), anime.strip()] for pid, name, anime in matches]

    # 何の日・行事, second h6, font tags
    events = [tag.get_text(strip=True) for tag in h6s[1].find_all('font')]

    # 歴史・出来事, third h6
    html = h6s[2].decode_contents()
    matches = r_html_history.findall(html)
    history = [[int(year), event.strip()] for year, event in matches]

    # 有名人及び声優, fourth h6
    html = h6s[3].decode_contents()
    matches = r_html_people.findall(html)
    people = [[int(year), name.strip(), profession.strip()] for year, name, profession in matches]

    return {
        'note': day_note,
        'birthdays': birthdays,
        'events': events,
        'history': history,
        'people': people
    }


def crawl_page(month: int, day: int) -> str:
    cache = Path(__file__).parent / "cache" / f"{month:02d}-{day:02d}.html"
    if not cache.exists():
        url = f"https://bd.fan-web.jp/sayhappy_sp.cgi?month={month}&day={day}"
        req = requests.get(url)
        if req.status_code != 200:
            raise Exception(f"Failed to fetch page: {req.status_code}")

        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(req.text.encode('latin-1').decode('utf-8'), encoding='utf-8')

    return cache.read_text(encoding='utf-8')


def crawl_page_util(t: tuple[int, int]) -> dict:
    month, day = t
    return parse_birthday_page(crawl_page(month, day))


def crawl_all_pages() -> list:
    cache = (Path(__file__).parent / 'bdfan.json')
    if cache.exists():
        print(f"Loading cached data from {cache}")
        return json.loads(cache.read_text(encoding='utf-8'))

    inputs = [(month, day) for month in range(1, 13) for day in range(1, 32)]
    results = tmap(crawl_page_util, inputs, desc="Crawling BDFan Pages", max_workers=8)
    results = [{'month': month, 'day': day, **data} for (month, day), data in zip(inputs, results)]

    cache.write_text(json.dumps(results, ensure_ascii=False), encoding='utf-8')
    return results


def crawl_all_pages_with_hearts() -> list:
    results = crawl_all_pages()

    # Add hearts data
    pids = [pid for page in results for pid, _, _ in page['birthdays']]
    print(f"Found {len(pids)} unique PIDs for hearts data.")
    hearts = get_hearts(pids)
    (Path(__file__).parent / 'bdfan_hearts.json').write_text(json.dumps(hearts), encoding='utf-8')
    for page in results:
        for birthday in page['birthdays']:
            pid = birthday[0]
            birthday.append(hearts.get(pid, 0))
    # Save the results with hearts
    (Path(__file__).parent / 'bdfan_with_hearts.json').write_text(json.dumps(results, ensure_ascii=False), encoding='utf-8')
    return results


def get_hearts_raw(pids: List[int]) -> Dict[int, int]:
    url = 'https://bd.fan-web.jp/iine/cn/server.php'
    headers = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    }
    data = {'requ': json.dumps({
        "cmd": "init", "cnt_load": 1, "b_css_reset": 1,
        "pollx": [{"wid": i + 1, "pid": str(pid), "tid": "tpl-sb-heart-s"} for i, pid in enumerate(pids)],
    })}
    resp = requests.post(url, headers=headers, data=data)
    resp.raise_for_status()
    return {int(pid): details['b1'] for pid, details in resp.json().get('vcntsx', {}).items()}


def get_hearts(pids: List[int]) -> Dict[int, int]:
    pids = list(set(pids))  # Remove duplicates
    # Paginate requests
    page_size = 5000
    results = {}
    for i in range(0, len(pids), page_size):
        batch = pids[i:i + page_size]
        print(f"Fetching hearts for PIDs {i + 1} to {i + len(batch)}...")
        batch_results = get_hearts_raw(batch)
        results.update(batch_results)
    return results


if __name__ == '__main__':
    crawl_all_pages_with_hearts()
