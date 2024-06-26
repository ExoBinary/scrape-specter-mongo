# Scrape Specter

![Scrape Specter Logo](https://raw.githubusercontent.com/ExoBinary/scrape-specter/main/media/logo.webp)

This project integrates FastAPI with Scrapy to create a web scraping API. Users can initiate scraping tasks via an API endpoint, and the results are stored in a PostgreSQL database.

## Features

- **FastAPI Endpoint**: Initiate scraping tasks by sending requests to a FastAPI endpoint.
- **Scrapy Spider**: Leverages Scrapy's PyppeteerSpider to scrape web pages asynchronously.
- **Concurrency Control**: Ensures that the same domain is not scraped concurrently by different users.
- **Database Storage**: Stores the scraped data and domain statuses in a PostgreSQL database.

## Setup

### Prerequisites

- Python 3.8+
- PostgreSQL
- pipenv or virtualenv (optional but recommended for package management)

### Installation

1. Clone the repository:

```
git clone https://github.com/ExoBinary/scrape-specter.git
```

2. Navigate to the project directory:

```
cd scrape-specter
```

3. Install the required Python packages:

```
pip install -r requirements.txt
```

4. Set up the Mongo DB database and update the `.env` file with your `MONGODB_URL`, for example:

```
MONGODB_URL=mongodb://localhost:27017
```

5. Initialize the database tables:

```
python

from modules.database import create_tables
create_tables()
```

### Running the Application

To start the FastAPI application, run:

```
uvicorn main:app --reload
```

The API will be available at `http://localhost:8039`.

### Using the API

To initiate a scraping task, send a POST request to the `/crawl/` endpoint with the target URL:

```
curl -X 'POST'
'http://localhost:8039/crawl/'
-H 'accept: application/json'
-H 'Content-Type: application/json'
-d '{"url": "https://example.com"}'
```

## Project Structure

- `main.py`: The FastAPI application.
- `modules/spider.py`: Contains the PyppeteerSpider used for scraping.
- `modules/database.py`: Database models and session management.
- `.env`: Environment variables, including the database connection string.

## License

This work is licensed under the Creative Commons Attribution-NonCommercial 4.0 International License. To view a copy of this license, visit http://creativecommons.org/licenses/by-nc/4.0/ or send a letter to Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.

You are free to:

- **Share** — copy and redistribute the material in any medium or format
- **Adapt** — remix, transform, and build upon the material

Under the following terms:

- **Attribution** — You must give appropriate credit, provide a link to the license, and indicate if changes were made. You may do so in any reasonable manner, but not in any way that suggests the licensor endorses you or your use.
- **NonCommercial** — You may not use the material for commercial purposes.

No additional restrictions — You may not apply legal terms or technological measures that legally restrict others from doing anything the license permits.

## Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
