import { DynamoDB } from '@aws-sdk/client-dynamodb';
import { DynamoDBDocument } from '@aws-sdk/lib-dynamodb';

const dynamo = DynamoDBDocument.from(new DynamoDB());

export const handler = async (event, context) => {
  let body;
  let statusCode = 200;
  const headers = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Methods": "GET,OPTIONS"
  };

  try {
    switch (event.routeKey) {
      case "GET /donuts/{donutId}":
        // Get a single donut by ID
        body = await dynamo.get({
          TableName: "Donuts",
          Key: {
            donutId: event.pathParameters.donutId
          }
        });
        break;
        
        case "GET /donuts":
          // Get all donuts
          body = await dynamo.scan({ TableName: "Donuts" });
          
          if (body.Items) {
            body.Items.sort((a, b) => parseInt(a.donutId) - parseInt(b.donutId));
            
            // Replace S3 URLs with CloudFront URLs
            const CLOUDFRONT_DOMAIN = 'd9kx2czuwyum3.cloudfront.net';
            body.Items = body.Items.map(item => ({
              ...item,
              imageUrl: item.imageUrl
                .replace('http://donuts-finale-ngf-531.s3-website-us-east-1.amazonaws.com/', `https://${CLOUDFRONT_DOMAIN}/`)
                .replace('https://donuts-finale-ngf-531.s3.us-east-1.amazonaws.com/', `https://${CLOUDFRONT_DOMAIN}/`)
            }));
          }
          break;
        
      default:
        throw new Error(`Unsupported route: "${event.routeKey}"`);
    }
  } catch (err) {
    statusCode = 400;
    body = err.message;
  } finally {
    body = JSON.stringify(body);
  }

  return {
    statusCode,
    body,
    headers
  };
};