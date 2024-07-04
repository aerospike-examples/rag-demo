# Aerospike Vector Search RAG Implementation

This repository houdse a RAG demo using Aerospike Vector Search (AVS). Use the following instructions for deployment.

>**Optional** 
>
>Customize the web scraper to fit your needs. See [Scrapy documentation](https://docs.scrapy.org/en/latest/) for details. Scraper code can be found in `/server/scraper/`

1. Replace the `config/aerospike/features.replace.conf` and `config/vector/features.replace.conf` with a valid Aerospike feature key file.
    >**Note**
    >
    >The feature key file must have a line item for `vector-service`
2. Edit the `/config/config.env` file with your information, or use the `-e` flag when building the containers to override.
   
   Configuration items:

   | Key              | Default value                          | Description                                                 |
   |------------------|----------------------------------------|-------------------------------------------------------------|
   | AVS_INDEX_NAME   | document-idx                           | Name of AVS index for vector search                         | 
   | AVS_SET_NAME     | docs                                   | Name of the set to store the document records               |
   | OPEN_AI_MODEL    | gpt-4o                                 | OpenAI model to use for LLM                                 |
   | OPEN_AI_API_KEY  | none                                   | Your OpenAI API key (Required for OpenAI usage)             |
   | SCRAPER_SITE_MAP | https://aerospike.com/docs/sitemap.xml | Sitemap to use in scraping for vector embeddings and search | 

    >**Note**
    >
    >This is set up to use an OpenAI API key, though could be modified to work with a local LLM.
3. Build and deploy the containers:
    ```bash
    DOCKER_BUILDKIT=0 docker-compose up -d # using docker-compose standalone
    ```
    or
    ```bash
    DOCKER_BUILDKIT=0 docker compose up -d # using docker 
    ``` 
4. Load data into the database:
    ```bash
    docker exec -it -w /server aerospike-client python3 load_data.py
    ```
    >**Note**
    >
    >This will take some time depending on the size of the website you are scraping. There is a ~3 second delay between each page scrape to avoid rate limiting or overloading the server with requests.
5. Access the site at http://localhost:4173