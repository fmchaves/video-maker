# Video Maker

The program will generate a video based on a theme proposed by the user. This program is a python reproduction of the project proposed by <a target="_blank" href="https://github.com/filipedeschamps">Filipe Deschamps</a>. To run the program correctly, you need to follow the steps for configuring the apis on the <a target="_blanck" href="https://github.com/filipedeschamps/video-maker">page</a> and fill in the fields in the credentials.json file inside the robots folder. The file has the following structure:

```
{
    "algorithmia": {
        "url": "web/WikipediaParser/0.1.2",
        "api_key": ""
    },
    "ibm-watson": {
        "url": "",
        "api_key": ""
    },
    "google-search": {
        "url": "https://www.googleapis.com/customsearch/v1",
        "api_key": "",
        "search_engine_id": ""
    }
}
```

You can see a sample of a video created by the robot at the following link: http://rebrand.ly/3j4dda3

## Modules

This program will use the following non-standard python modules:

1) Algorithmia to get the content from wikipedia.
2) pysbd to divite the content into sentences.
3) ibm_watson, ibm_cloud_sdk_core.authenticators, ibm_watson.natural_language_understanding_v1 to get the keywords.
4) PIL to standardize images.
5) moviepy to create the video.
