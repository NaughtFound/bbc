from datetime import datetime
import os
import time

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pathlib import Path
from dataclasses import dataclass, asdict

URL = "https://www.bbc.co.uk/learningenglish/english/features/6-minute-english"
BASE = "https://www.bbc.co.uk"
DOWNLOAD_ROOT = "./episodes"
CUTOFF = datetime(2025, 1, 1)

headers = {"User-Agent": "Mozilla/5.0"}

proxies = {
    "http": "http://localhost:1081",
    "https": "http://localhost:1081",
}


@dataclass
class Episode:
    date: datetime
    title: str
    url: str


@dataclass
class Downloadable:
    worksheet: str | None = None
    audio: str | None = None
    transcript: str | None = None


def get_feature_items() -> list[Episode]:
    res = requests.get(URL, headers=headers, proxies=proxies, timeout=15)
    soup = BeautifulSoup(res.text, "html.parser")

    items = []

    for el in soup.select("[data-feature-item]"):
        a = el.parent.select_one("div.text").find("a", href=True)
        d = el.parent.select_one("div.details h3")

        raw_date = d.get_text().split("/")[1].strip()
        dt = datetime.strptime(raw_date, "%d %b %Y")

        if a:
            items.append(
                Episode(
                    date=dt,
                    title=a.get_text(strip=True),
                    url=urljoin(BASE, a["href"]),
                )
            )

    return items


def extract_downloads(url: str) -> Downloadable:
    res = requests.get(url, headers=headers, proxies=proxies, timeout=15)
    soup = BeautifulSoup(res.text, "html.parser")

    downloadable = Downloadable()

    widget = soup.select_one("div.widget-pagelink-download")

    if not widget:
        return downloadable

    for a in widget.select("a.download"):
        href = a.get("href", "")
        text = a.get_text(strip=True).lower()

        if "audio" in text or href.endswith(".mp3"):
            downloadable.audio = href

        elif "worksheet" in href and href.endswith(".pdf"):
            downloadable.worksheet = href

        elif "transcript" in href or href.endswith(".pdf"):
            downloadable.transcript = href

    if not downloadable.transcript or not downloadable.worksheet:
        for a in soup.select("div.widget-richtext a[href]"):
            href = a["href"].lower()

            if "worksheet" in href and href.endswith(".pdf"):
                downloadable.worksheet = href

            elif "transcript" in href or href.endswith(".pdf"):
                downloadable.transcript = href

    return downloadable


def download_file(downloadable: Downloadable, root: Path, episode: Episode):
    urls = asdict(downloadable).values()
    episode_path = root / Path(episode.title)
    ts = time.mktime(episode.date.timetuple())
    episode_path.mkdir(parents=True, exist_ok=True)

    for url in urls:
        if not url:
            continue
        filepath = Path(episode_path / url.split("/")[-1])

        if filepath.exists():
            os.utime(filepath, (ts, ts))
            continue

        print(url)

        with requests.get(
            url,
            stream=True,
            headers=headers,
            proxies=proxies,
            timeout=15,
        ) as r:
            r.raise_for_status()
            with open(filepath, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        os.utime(filepath, (ts, ts))


if __name__ == "__main__":
    data = get_feature_items()
    root = Path(DOWNLOAD_ROOT)

    for episode in data:
        if episode.date < CUTOFF:
            break

        downloadable = extract_downloads(episode.url)
        download_file(downloadable, root, episode)
        print(f"{episode.title} Completed")
