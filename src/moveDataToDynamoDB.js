// Node.js script for AWS Lambda

console.log('Loading event');
var doc = require('dynamodb-doc');
var dynamodb = new doc.DynamoDB();


exports.handler = function(event, context) {
    console.log("Request received:\n", JSON.stringify(event));
    console.log("Context received:\n", JSON.stringify(context));


    var tableName = "MovieData";
    //var datetime = new Date().getTime().toString();
    var item = {
        "title": event.title, 
        "year": parseInt(event.year),
        "Director1": event.Director1,
        "Genre1": event.Genre1,
        "Genre2": event.Genre2,
        "Genre3": event.Genre3,
        "stars": parseInt(event.stars)
    };
    console.log("Item:\n", item);


    dynamodb.putItem({
            "TableName": tableName,
            "Item": item
        }, function(err, data) {
            if (err) {
                context.fail('ERROR: Dynamo failed: ' + err);
            } else {
                console.log('Dynamo Success: ' + JSON.stringify(data, null, '  '));
                context.succeed('SUCCESS');
            }
        });
}
