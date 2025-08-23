# Anime Birthdays Dataset

Anime birthday dataset from https://bd.fan-web.jp

## Use as a Python Package

First install the package via pip:

```bash
pip install bdfan
```

Then, you can use it in your Python code as follows:

```python
import bdfan

# Load data for a specific day
month = 1
day = 1
print(bdfan.load_date(month, day))

# Or if you want to query in batch
bdata = bdfan.load_mapping()
print(bdata[month][day])
```

## Data Structure [bdfan_with_hearts.json](bdfan/bdfan_with_hearts.json)

This file contains the primary scraped data for every day of the year. It is a JSON array where each object represents a single day.

### Structure

The root element is a `List[Dict]`. Each dictionary object within the list has the following keys:

-   `month`: **Integer** The month of the year (1-12).
-   `day`: **Integer** The day of the month (1-31).
-   `note`: **String** A general note or description for the day.
-   `birthdays`: **List[List]** A list of anime characters whose birthday falls on this day. `[<pid>, <name>, <anime>, <hearts>]`.
    -   `pid` (Integer): A unique identifier for the character on the source website.
    -   `name` (String): The character's name.
    -   `anime` (String): The title of the anime or manga the character is from.
    -   `hearts` (Integer): The number of hearts/likes
-   `events`: **List[String]** A list of events, holidays, or special observances for the day (e.g., "兄の日," "世界難民の日").
-   `history`: **List[List]** A list of notable historical events that occurred on this day. Each inner list has the format: `[<year>, <description>]`.
    -   `year` (Integer): The year the event took place.
    -   `description` (String): A brief description of the event.
-   `people`: **List[List]** A list of famous people (celebrities, voice actors, etc.) born on this day. `[<year>, <name>, <profession>]`.
    -   `year` (Integer): The person's birth year.
    -   `name` (String): The person's name.
    -   `profession` (String): The person's profession or a brief note.

### Example Entry

```json
[
  {
    "month": 1,
    "day": 1,
    "note": "元日\n1年の最初の日。年のはじめを祝う国民の祝日。",
    "birthdays": [
      [10419, "ポートガス・D・エース", "ONE PIECE", 2530],
      [13364, "東峰 旭", "ハイキュー!!", 1890],
      [14561, "道明寺 司", "花より男子", 542]
    ],
    "events": [
      "元日",
      "初詣",
      "年賀"
    ],
    "history": [
      [1873, "太陽暦が導入され、明治5年12月3日が明治6年1月1日になる。"],
      [1959, "キューバ革命: バティスタ将軍が亡命しカストロが勝利。"]
    ],
    "people": [
      [1919, "J・D・サリンジャー", "作家"],
      [1964, "増田順一", "ゲームクリエイター"],
      [1975, "尾田栄一郎", "漫画家"]
    ]
  }
]
```
