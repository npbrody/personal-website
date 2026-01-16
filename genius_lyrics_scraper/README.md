# Genius Lyrics Scraper

A Python command-line tool to automatically fetch song lyrics from Genius and add them to your CSV files.

## Features

- Reads CSV files with artist and song information
- Automatically retrieves lyrics from Genius API
- Handles rate limiting with configurable delays
- Comprehensive error handling and progress tracking
- Cleans song titles (removes "feat.", brackets, etc.)
- Detects instrumental/unavailable lyrics
- Saves results back to the CSV file

## Setup

### 1. Install Python Dependencies

```bash
cd genius_lyrics_scraper
pip install -r requirements.txt
```

### 2. Get Your Genius API Token

Your Genius API token doesn't expire, so you only need to get it once and save it.

1. Go to [https://genius.com/api-clients](https://genius.com/api-clients)
2. Sign in to your Genius account (create one if needed)
3. Click "New API Client"
4. Fill in the app details:
   - **App Name**: Something like "My Lyrics Scraper"
   - **App Website URL**: You can use your personal website or just `http://localhost`
5. Click "Save"
6. On the next page, click "Generate Access Token"
7. Copy the access token (it will look like a long string of random characters)

### 3. Configure the API Token

Copy the example environment file and add your token:

```bash
cp .env.example .env
```

Then edit `.env` and replace `your_genius_api_token_here` with your actual token:

```
GENIUS_API_TOKEN=your_actual_token_goes_here
```

**Important**: The `.env` file is already in `.gitignore` so your token won't be committed to git.

## Usage

### Prepare Your CSV File

Your CSV file should have at least two columns:
- `Artist` (or `artist`, `Artists`)
- `Song` (or `song`, `Title`, `Song Title`, `Track`)

Example CSV:

```csv
Artist,Song
Taylor Swift,Anti-Hero
The Beatles,Hey Jude
Radiohead,Creep
```

### Run the Scraper

Basic usage:

```bash
python scraper.py path/to/your/songs.csv
```

With custom delay (in seconds) between requests:

```bash
python scraper.py path/to/your/songs.csv 5.0
```

The script will:
1. Read your CSV file
2. For each song, search Genius for lyrics
3. Add a new `Lyrics` column with the results
4. Save the updated CSV back to the same file

### Example Output

```
Attempting to load CSV file: songs.csv
CSV loaded successfully. Shape: (3, 2)
Using columns: Artist='Artist', Song='Song'
Initializing Genius API client...
Genius client initialized.
Added 'Lyrics' column to dataframe.

Starting to process 3 songs...

Processing row 0: 'Taylor Swift' - 'Anti-Hero'
Searching for: 'Anti-Hero' by 'Taylor Swift'
Found lyrics for 'Anti-Hero' by 'Taylor Swift'
Waiting for 10.0 seconds before next request...

Processing row 1: 'The Beatles' - 'Hey Jude'
Searching for: 'Hey Jude' by 'The Beatles'
Found lyrics for 'Hey Jude' by 'The Beatles'
Waiting for 10.0 seconds before next request...

...

Saving CSV file...
Successfully processed and saved file: songs.csv
Summary: Processed=3, Errors/Not Found=0, Skipped=0
```

## Configuration

### Rate Limiting

The default delay between API requests is 10 seconds to respect Genius's rate limits. You can adjust this:

```bash
# Use 5 second delay (faster, but more likely to hit rate limits)
python scraper.py songs.csv 5.0

# Use 15 second delay (slower but safer)
python scraper.py songs.csv 15.0
```

## Troubleshooting

### "GENIUS_API_TOKEN not found"

Make sure you created the `.env` file in the `genius_lyrics_scraper` directory and added your token.

### "Lyrics Not Found/Error"

This can happen if:
- The song/artist name doesn't match Genius's database
- The song is too new or obscure
- There was a network error

Try checking the exact song name on Genius.com manually.

### Rate Limiting Errors

If you see errors about rate limiting, increase the delay between requests:

```bash
python scraper.py songs.csv 15.0
```

## Tips

- **Exact Names**: Use the exact artist and song names as they appear on Genius for best results
- **Batch Processing**: The scraper saves progress after each song, so you can stop and resume
- **Large Datasets**: For large CSV files, consider running overnight with a 10-15 second delay
- **Backup**: Always keep a backup of your original CSV file before running the scraper

## What's Different from the Excel Version?

- Uses CSV instead of Excel (simpler, easier to version control)
- API token stored in `.env` file (more secure, reusable)
- Command-line arguments for file path and delay
- Pandas instead of openpyxl (more flexible for data manipulation)
- Better column name detection (case-insensitive)

## License

Free to use for personal projects.
