import json
import boto3
from decimal import Decimal

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Donuts')

# Helper class to convert Decimal to int/float for JSON serialization
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return int(obj) if obj % 1 == 0 else float(obj)
        return super(DecimalEncoder, self).default(obj)

def lambda_handler(event, context):
    # CORS headers
    headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Methods": "GET,OPTIONS"
    }
    
    try:
        route_key = event.get('routeKey', '')
        
        if route_key == 'GET /donuts/{donutId}':
            # Get single donut by ID
            donut_id = event['pathParameters']['donutId']
            response = table.get_item(Key={'donutId': donut_id})
            body = response.get('Item', {})
            
        elif route_key == 'GET /donuts':
            # Get all donuts
            response = table.scan()
            items = response.get('Items', [])
            
            # Sort by donutId
            items.sort(key=lambda x: int(x.get('donutId', 0)))
            
            # Replace S3 URLs with CloudFront URLs
            cloudfront_domain = 'd9kx2czuwyum3.cloudfront.net'
            for item in items:
                if 'imageUrl' in item:
                    item['imageUrl'] = item['imageUrl'].replace(
                        'http://donuts-finale-ngf-531.s3-website-us-east-1.amazonaws.com/',
                        f'https://{cloudfront_domain}/'
                    ).replace(
                        'https://donuts-finale-ngf-531.s3.us-east-1.amazonaws.com/',
                        f'https://{cloudfront_domain}/'
                    )
            
            body = {'Items': items}
            
        else:
            raise Exception(f'Unsupported route: "{route_key}"')
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps(body, cls=DecimalEncoder)
        }
        
    except Exception as e:
        return {
            'statusCode': 400,
            'headers': headers,
            'body': json.dumps({'error': str(e)})
        }