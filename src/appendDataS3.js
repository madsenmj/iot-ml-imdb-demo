// Node.js script for AWS Lambda

console.log('Loading function');


var aws = require('aws-sdk');
var s3 = new aws.S3();


exports.handler = function(event, context) {
    //console.log('Received event:', JSON.stringify(event, null, 2));


    // Get the object from the event and show its content type
    var bucket = 'madsenm-movie-hist-data';
    var key = 'movie_ratings_simple.csv';
    var params = {
        Bucket: bucket,
        Key: key
    };
    s3.getObject(params, function(err, data) {
        if (err) {
            console.log(err);
            var message = "Error getting object " + key + " from bucket " + bucket +
                ". Make sure they exist and your bucket is in the same region as this function.";
            console.log(message);
            context.fail(message);
        } else {
            console.log(params_new);
            console.log('CONTENT TYPE getObject:', data.ContentType);


            // convert body(file contents) to a string so we can append
            var body = data.Body.toString('utf-8');
            // append data
            var newdata = event.title + ','  + event.year + ',' + event.Director1 + ',' + event.Genre1 + ',' + event.Genre2 + ',' + event.Genre3 + ',' + event.stars;
            console.log(newdata);
            body += newdata + '\n';


            var params_new = {
                Bucket: bucket,
                Key: key,
                Body: body
            };
            //NOTE this call is now nested in the s3.getObject call so it doesn't happen until the response comes back
            s3.putObject(params_new, function(err, data) {
                        console.log('put here');
                        if (err) {
                            console.log(err);
                            var message = "Error getting object " + key + " from bucket " + bucket +
                                ". Make sure they exist and your bucket is in the same region as this function.";
                            console.log(message);
                            context.fail(message);
                        } else {
                            console.log('CONTENT TYPE putObject:', data.ContentType);
                            context.succeed(data.ContentType);
                        }
            });


        }
    });


};