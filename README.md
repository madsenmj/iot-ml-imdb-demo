# An IoT Machine Learning Demonstration

A demonstration of an IoT project using AWS. I use data from the IMDB to predict the best combination of director, genre, and year for a new movie.

There is a [presentation](/docs/AWS_IoT_Demo.pptx) and a [YouTube Video](https://youtu.be/OQkOtIrpX3g) describing the project.

# Data

I begin with data from two sources:

1. The [IMDB Online Database](ftp://ftp.fu-berlin.de/pub/misc/movies/database/). I started with the `ratings.list` file that provides a breakdown of movie ratings for all of the films in their database.
2. I enhanced this dataset using the [Open Movid Database](http://www.omdbapi.com/), adding information about the director and genre of each film.

## Data Processing and Exploration

The [GetMovieData](/src/GetMovieData.ipynb) notebook steps through the acquisition of the Open MDB data using their API. It also combines the data with a [cleaned version](data/ratings.csv) of the `ratings.list` data from the IMDb. The cleaned version removes the header and footer from the file and turns it into a `csv`. This notebook outputs two additional files that have the [Open MDB data with films with more than 5000 ratings:](/src/openmdb.csv) and [films with 1500 to 5000 ratings](/data/openmdb_more.csv). It then combines all the datasets and outputs a simplified dataset containing the director, year, genre, and star rating (/data/movie_ratings_simple.csv).

I present a second notebook, [MovieAnalysis](/src/MovieAnalysis.ipynb) that looks at the data and examines some of its features.

Finally, a third notebook, [MoviePredictionTests](/src/MoviePredictionTests.ipynb) does a first-pass attempt at predicting the rating of a movie given its director, genre, and year.

# IoT AWS Interface

## AWS dynamoDB
The next part of the project was to upload the [data](/data/movie_ratings_simple.tsv) to an AWS dynamoDB database. This consists of first uploading the data to an S3 storage container, then moving from the storage container to the dynamoDB. The dynamoDB requires an input data schema and format following:

```
{"title":{"s":"Test Movie Title"},"Director1":{"s":"Director name"},"Genre1":{"s":"Genre1 Name"},"Genre2":{"s":"Genre2 Name"},"stars":{"n":"9"},"year":{"n":"2002"},"Genre3":{"s":"Genre3 Name"}}
```

I followed [this documentation](http://docs.aws.amazon.com/datapipeline/latest/DeveloperGuide/dp-importexport-ddb-part1.html) to import the data into the dynamoDB.

## AWS Machine Learning

I used the data stored in the S3 container to train the machine learning model [following this tutorial](http://docs.aws.amazon.com/machine-learning/latest/dg/tutorial.html). I established an endpoint for the trained model in order to query the model from my IoT server node.

## AWS IoT 

I built an AWS IoT portal following the [SDK tutorial](https://aws.amazon.com/iot-platform/getting-started/). I registered and connected my [Rapsberry Pi model 3](https://www.raspberrypi.org/products/raspberry-pi-3-model-b/) to the IoT portal. This involved downloading license keys and certificates and putting them on the Raspberry Pi.

The IoT hub is set to look for prediction requests on the `filmrequest` topic from the IoT device.

The IoT device is set to listen on the MQTT topic `$aws/things/MovieSelector/shadow/update` for predictions from the AWS machine learning model.

The IoT hub is looking for new "scored" films on the `filmupdate` topic.

## Lambda Scripts

The data path on AWS looks like this:

1. The IoT sends a request for a prediction. This is directed to a [lambda script](/src/getMLpredictions.js) that queries the trained model. 
2. The trained model returns a JSON object with its prediction. The prediction is then returned to the IoT device. 
3. The IoT device repeats this process several times for different combinations of inputs, looking for the best possible output.
4. The IoT device then makes a decision about which set to use, then gets feedback as to the "real" rating for that set of inputs. It sends the final movie information, with its rating, back to the AWS IoT hub. The hub then directs that data to two places, [storing it in the dynamoDB](/src/moveDataToDynamoDB.js) and [appending it to the S3 tsv file](/src/appendDataS3.js) for future improvements in the machine learning model.


# IoT Device Configuration

The Raspberry Pi uses the [AWS Python SDK](https://github.com/aws/aws-iot-device-sdk-python) to interface with the AWS IoT hub. This requires gathering the certificate and private key files and saving them in the source directory on the Pi.

The Pi also needs a copy of the movie_ratings_simple.csv data file from which it creates random combinations of film titles, directors, years, and genres. This is testing in the [device movie generator](/src/iot_device_movie_generator.ipynb) notebook. We then run through a complete test of the system (including communications with the AWS endpoint) in the [last notebook](/src/iot_device_test.ipynb).

The final version is compiled in a single [device simulator script](/src/iot_device_simulator.py) python script.




