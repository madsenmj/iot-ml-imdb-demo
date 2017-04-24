// Node.js script for AWS Lambda


console.log('Loading event');
exports.handler = function(event, context) {
  var AWS = require('aws-sdk');
  var iotdata = new AWS.IotData({endpoint: 'https://a1oi3e8bkl4am6.iot.us-east-1.amazonaws.com'});


  var ml = new AWS.MachineLearning();
  var endpointUrl = 'https://realtime.machinelearning.us-east-1.amazonaws.com';
  var mlModelId = 'ml-wjbqpgTq9bC';


 
    var item = {
        "title": event.title, 
        "year": event.year,
        "Director1": event.Director1,
        "Genre1": event.Genre1,
        "Genre2": event.Genre2,
        "Genre3": event.Genre3
    };
    console.log("Item:\n", item);
  
  var params = {
        Record : event,
        PredictEndpoint : endpointUrl,
        MLModelId: mlModelId
      }
  
  ml.predict(params,
      function(err, data) {
        if (err) {
          console.log(err);
          context.done(err);
        }
        else {
          console.log('Predict call succeeded \n' + JSON.stringify(data.Prediction));
        
        var payloadout = data.Prediction;
        payloadout['title'] = event.title;
        
        var iotparams = {
        topic: '$aws/things/MovieSelector/shadow/update',
        payload: JSON.stringify(payloadout),
        qos: 1
        };
        
        
        iotdata.publish(iotparams, function(err, data){
            if(err){
                console.log(err);
            }
            else{
                console.log("success?");
                //context.succeed(event);
            }
    });
          
          //if(data.Prediction.predictedLabel === '1'){
          context.succeed(data);
        }
      }
      );


};