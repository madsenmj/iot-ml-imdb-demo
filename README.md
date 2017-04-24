# An IoT Machine Learning Demonstration

A demonstration of an IoT project using AWS. I use data from the IMDB to predict the best combination of director, genre, and year for a new movie.

There is a [presentation](/docs/AWS_IoT_Demo.pptx) and a [YouTube Video](https://youtu.be/OQkOtIrpX3g) describing the project.

# Data

I begin with data from two sources:

1. The [IMDB Online Database](ftp://ftp.fu-berlin.de/pub/misc/movies/database/). I started with the `ratings.list` file that provides a breakdown of movie ratings for all of the films in their database.
2. I enhanced this dataset using the [Open Movid Database](http://www.omdbapi.com/), adding information about the director and genre of each film.

## Data Processing and Exploration

The [GetMovieData](/src/GetMovieData.ipynb) notebook steps through the acquisition of the Open MDB data using their API. It also combines the data with a [cleaned version](data/ratings.csv) of the `ratings.list` data from the IMDb. The cleaned version removes the header and footer from the file and turns it into a `csv`. This notebook outputs two additional files that have the Open MDB data: (/src/openmdb.csv) and (/src/openmdb_more.csv). It then combines all the datasets and outputs a simplified dataset containing the director, year, genre, and star rating (/data/movie_ratings_simple.csv).

I present a second notebook, [MovieAnalysis](MovieAnalysis.ipynb) that looks at the data and examines some of its features.

Finally, a third notebook, [MoviePredictionTests](MoviePredictionTests.ipynb) does a first-pass attempt at predicting the rating of a movie given its director, genre, and year.

# IoT Interface

The next part of the project was to upload the 


I needed to subscribe to the $aws/things/MovieSelector/shadow/update topic on the device. Then, when I publish to that topic, the message gets sent back to the device. There is a handler function that works with the response to process the data.

http://docs.aws.amazon.com/iot/latest/developerguide/what-is-aws-iot.html
ratings.list.gz

Extracted the ratings lines (removed header and footer) using Microsoft Excel. Copied the body of the data starting at line 296 and ending before the "REPORT FORMAT" lines to a new worksheet and saved as ratings.csv





# Scripts


So the path looks like this:

1) The IoT sends a request for a prediction. AWS runs the prediction and sends back the probabilities. This repeats for 4 runs as the IoT decides how to best utilize available resources

2) The IoT device then "executes" the best option and gets an "actual" score for the set. The device then sends this back to AWS for storage and learning. AWS puts this data into DynamoDB. 

3) There is a regular (daily?!?!) pipeline that shifts the DyanmoDB data to Redshift and then re-trains the model based on the new data




**I think these are not working and not used... **

getMLModel returns:

```
{
  "MLModelId": "ml-wjbqpgTq9bC",
  "TrainingDataSourceId": "ds-MPfGVCiU36s",
  "CreatedByIamUser": "arn:aws:iam::926793078622:root",
  "CreatedAt": "2016-09-08T15:47:41.436Z",
  "LastUpdatedAt": "2016-09-08T15:54:06.026Z",
  "Name": "ML model: Simple Movie",
  "Status": "COMPLETED",
  "SizeInBytes": 1415234,
  "EndpointInfo": {
    "PeakRequestsPerSecond": 200,
    "CreatedAt": "2016-09-19T12:27:19.917Z",
    "EndpointUrl": "https://realtime.machinelearning.us-east-1.amazonaws.com",
    "EndpointStatus": "READY"
  },
  "TrainingParameters": {
    "algorithm": "sgd",
    "sgd.l1RegularizationAmount": "0.0",
    "sgd.l2RegularizationAmount": "1e-6",
    "sgd.maxMLModelSizeInBytes": "104857600",
    "sgd.maxPasses": "10",
    "sgd.shuffleType": "auto"
  },
  "InputDataLocationS3": "s3://madsenm-movie-hist-data/movie_ratings_simple.csv",
  "MLModelType": "MULTICLASS",
  "LogUri": "https://eml-prod-emr.s3.amazonaws.com/926793078622-pr-ml-wjbqpgTq9bC/userlog/926793078622-pr-ml-wjbqpgTq9bC?AWSAccessKeyId=AKIAJ76NNIATX32EN2VA&Expires=1474911155&Signature=O4tIc9MnIKRe4D700PltfXrd2AM%3D",
  "Recipe": "{\n  \"groups\" : { },\n  \"assignments\" : { },\n  \"outputs\" : [ \"ALL_CATEGORICAL\" ]\n}",
  "Schema": "{\"version\":\"1.0\",\"rowId\":\"title\",\"rowWeight\":null,\"targetAttributeName\":\"stars\",\"dataFormat\":\"CSV\",\"dataFileContainsHeader\":true,\"attributes\":[{\"attributeName\":\"title\",\"attributeType\":\"CATEGORICAL\"},{\"attributeName\":\"year\",\"attributeType\":\"CATEGORICAL\"},{\"attributeName\":\"Director1\",\"attributeType\":\"CATEGORICAL\"},{\"attributeName\":\"Genre1\",\"attributeType\":\"CATEGORICAL\"},{\"attributeName\":\"Genre2\",\"attributeType\":\"CATEGORICAL\"},{\"attributeName\":\"Genre3\",\"attributeType\":\"CATEGORICAL\"},{\"attributeName\":\"stars\",\"attributeType\":\"CATEGORICAL\"}],\"excludedAttributeNames\":[]}"
}

```

getEvaluation returns:

```
{
  "EvaluationId": "ev-BZpIarHNR9D",
  "MLModelId": "ml-wjbqpgTq9bC",
  "EvaluationDataSourceId": "ds-BGSNqUEaOjl",
  "InputDataLocationS3": "s3://madsenm-movie-hist-data/movie_ratings_simple.csv",
  "CreatedByIamUser": "arn:aws:iam::926793078622:root",
  "CreatedAt": "2016-09-08T15:47:41.797Z",
  "LastUpdatedAt": "2016-09-08T15:57:13.362Z",
  "Name": "Evaluation: ML model: Simple Movie",
  "Status": "COMPLETED",
  "PerformanceMetrics": {
    "Properties": {
      "MulticlassAvgFScore": "0.22252705911460363"
    }
  },
  "LogUri": "https://eml-prod-emr.s3.amazonaws.com/926793078622-ev-ev-BZpIarHNR9D/userlog/926793078622-ev-ev-BZpIarHNR9D?AWSAccessKeyId=AKIAJ76NNIATX32EN2VA&Expires=1474911298&Signature=rOyK8zpZTEziRGGELBmUf4QjizI%3D"
}

```


