// Node.js script for AWS Lambda

console.log('Loading event');
exports.handler = function(event, context) {
  var AWS = require('aws-sdk');

  var ml = new AWS.MachineLearning();
  var mlModelId = 'ml-wjbqpgTq9bC';

  var params = {
        EvaluationId : "ev-BZpIarHNR9D"
      }
    
  
  ml.getEvaluation(params,
      function(err, data) {
        if (err) {
          console.log(err);
          context.done(err);
        }
        else {
          console.log('Call succeeded \n' + JSON.stringify(data.Prediction));
        
          context.succeed(data);
        }
      }
      );

};