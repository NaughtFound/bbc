# BBC Learning English – 6 Minute English Downloader

A Python script that downloads audio files, worksheets, and transcripts from the BBC Learning English **6 Minute English** series.

The script scrapes the latest episodes from the BBC website, extracts downloadable resources, and saves them locally while preserving the original publication date as the file modification timestamp.


## Features

* Fetches episode listings from BBC Learning English
* Downloads:

  * MP3 audio files
  * PDF worksheets
  * PDF transcripts
* Organizes files by episode title
* Skips already downloaded files
* Updates file timestamps to match episode publication dates
* Supports configurable cutoff dates
* Supports HTTP/HTTPS proxy configuration

## Requirements

* Python 3.10+
* Requests
* BeautifulSoup4

Install dependencies:

```bash
pip install requests beautifulsoup4
```

## Configuration

The following constants can be modified at the top of the script:

```python
URL = "https://www.bbc.co.uk/learningenglish/english/features/6-minute-english"
DOWNLOAD_ROOT = "./episodes"
CUTOFF = datetime(2025, 1, 1)
```

### Download Directory

Downloaded files will be stored under:

```text
episodes/
├── Episode Title 1/
│   ├── audio.mp3
│   ├── worksheet.pdf
│   └── transcript.pdf
├── Episode Title 2/
│   └── ...
```

### Proxy Settings

The script is configured to use a local proxy by default:

```python
proxies = {
    "http": "http://localhost:1081",
    "https": "http://localhost:1081",
}
```

If you do not need a proxy, set:

```python
proxies = {}
```

or remove the `proxies` argument from all `requests.get()` calls.

## Usage

Run the script:

```bash
python main.py
```

The script will:

1. Retrieve all available 6 Minute English episodes.
2. Stop processing once an episode is older than the configured cutoff date.
3. Extract download links from each episode page.
4. Download available resources.
5. Store them in episode-specific folders.

Example output:

```text
https://downloads.bbc.co.uk/learningenglish/features/6-minute-english/example.mp3
The psychology of habits Completed

https://downloads.bbc.co.uk/learningenglish/features/6-minute-english/example2.mp3
Can AI write poetry? Completed
```

## How It Works

### Episode Discovery

`get_feature_items()`

* Fetches the main 6 Minute English page.
* Extracts episode titles, URLs, and publication dates.
* Returns a list of `Episode` objects.

### Resource Extraction

`extract_downloads(url)`

* Visits an episode page.
* Finds downloadable resources.
* Identifies:

  * Audio files (`.mp3`)
  * Worksheets (`.pdf`)
  * Transcripts (`.pdf`)

Returns a `Downloadable` object.

### File Downloading

`download_file(downloadable, root, episode)`

* Creates an episode directory.
* Downloads missing files.
* Skips existing files.
* Sets file timestamps to the episode publication date.

## Data Models

### Episode

```python
@dataclass
class Episode:
    date: datetime
    title: str
    url: str
```

### Downloadable

```python
@dataclass
class Downloadable:
    worksheet: str | None = None
    audio: str | None = None
    transcript: str | None = None
```

## Notes

* The script depends on the current BBC Learning English page structure.
* If the BBC changes its HTML layout, selectors may need to be updated.
* Some episodes may not provide all resources (audio, worksheet, transcript).
* Existing files are not re-downloaded.

## Disclaimer

This project is an independent utility and is not affiliated with or endorsed by the BBC.

The downloaded audio files, transcripts, worksheets, and other educational materials remain the intellectual property of the BBC and their respective copyright holders. This repository only contains the downloader code; it does not distribute BBC content.

Users are responsible for ensuring their use of downloaded materials complies with the BBC's Terms of Use and applicable copyright laws.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
