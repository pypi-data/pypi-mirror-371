# Clean Talk Python Client for Kolas.Ai Public API

Welcome to the **Kolas.Ai Public API** documentation! This repository hosts the Python client for Kolas.Ai's Clean Talk public API, making it easy for developers to integrate Kolas.Ai’s machine learning services into your applications.

## Overview

Clean Talk API is designed to classify message categories based on a trained dataset within a configured project. Use this API to accurately categorize messages into types like "Neutral", "Insult", "Spam" , etc. We support different languages, including English, Russian, Ukrainian, and we can add any languages by request (message to info@kolas.ai).

### Key Features
- **Predict Message Categories**: Use the `/predictions/predict` endpoint to sync classify messages based on your project-specific datasets and `/predictions/asyncPredict` endpoint to async classify messages.
- **High Accuracy**: Predictions include probability scores, giving you confidence in the classification results.
- **OAuth2 Authentication**: Secure access via OAuth2 client credentials flow.

## Usage

The Kolas.Ai API follows the OpenAPI 3.1 standard. To get started:

1. Create a new account on the [Kolas.Ai platform](https://app.kolas.ai/register).
2. Create a new project [Clean Talk](https://app.kolas.ai/projects/create) and configure your datasets.
3. **Authentication**: Obtain an access token using OAuth2 client credentials.
4. **Make Predictions**: Send a POST request to `/predictions/predict` (or `/predictions/asyncPredict`) with your `projectId` and messages.
5. **Receive Predictions**: Retrieve predicted categories and their probabilities in the API response.

## Installation
You can install the CleanTalk Python client via pip. Run the following command:

```bash
pip install clean-talk-client
```

## Authentication

This API uses **OAuth2 client credentials** for secure access. You’ll need to request a token using your client credentials from the Kolas.Ai platform.

```python
from clean_talk_client.kolas_ai_oauth_client import KolasAiOAuthClient

YOUR_CLIENT_ID = ''  # Set your client ID
YOUR_CLIENT_SECRET = ''  # Set your client secret

oauth_client = KolasAiOAuthClient()
auth_result = oauth_client.auth(YOUR_CLIENT_ID, YOUR_CLIENT_SECRET)
```

`$authResult` contains the access token and expires_in information, which you will use to authenticate your API requests. You need to update token after its expiration.

### Example for Sync Request
Once you have your access token, you can make a request like this:

```python
from clean_talk_client.clean_talk_prediction_client import CleanTalkPredictionClient
from clean_talk_client.message import Message
from clean_talk_client.predict_request import PredictRequest

YOUR_PROJECT_ID = '11'  # Set your project ID

client = CleanTalkPredictionClient(auth_result.access_token)
request = PredictRequest(
    YOUR_PROJECT_ID,
    [
        Message('11177c92-1266-4817-ace5-cda430481111', 'Hello world!'),
        Message('22277c92-1266-4817-ace5-cda430482222', 'Good buy world!'),
    ]
)
# Sync request to kolas.ai. It returns result of predictions immediately
response = client.predict(request)
for prediction in response.get_predictions():
    print("MessageId:", prediction.message_id)
    print("Message:", prediction.message)
    print("Prediction:", prediction.prediction)
    print("Probability:", prediction.probability)
    print("Categories:", ", ".join(prediction.categories))
```

### Example Response

```txt
MessageId: 11177c92-1266-4817-ace5-cda430481111
Message: Hello world!
Prediction: Neutral
Probability: 0.9036153107882
Categories: Insult, Neutral, Spam

MessageId: 22277c92-1266-4817-ace5-cda430482222
Message: Good buy world!
Prediction: Neutral
Probability: 0.99374455213547
Categories: Insult, Neutral, Spam
```

### Example for Async Request
Once you have your access token, you can make a request like this:

```python
from clean_talk_client.clean_talk_prediction_client import CleanTalkPredictionClient
from clean_talk_client.message import Message
from clean_talk_client.predict_request import PredictRequest

YOUR_PROJECT_ID = '11'  # Set your project ID

client = CleanTalkPredictionClient(auth_result.access_token)
request = PredictRequest(
    YOUR_PROJECT_ID,
    [
        Message('11177c92-1266-4817-ace5-cda430481111', 'Hello world!'),
        Message('22277c92-1266-4817-ace5-cda430482222', 'Good buy world!'),
    ]
)

# Async request to kolas.ai. Results of predictions will be sent on registered webhook
client.async_predict(request)
```

Responses will be sent to the configured webhook URL in your project settings.

## Documentation Links
- [Kolas.Ai OpenAPI schema](https://github.com/kolasai/public-openapi): Explore our OpenAPI specification.
- [Kolas.Ai Platform Documentation](https://kolas.ai/documentation/): Learn more about configuring projects and using Kolas.Ai’s platform.

## License

This API specification is released under the **Apache 2.0 License**. See the [LICENSE](https://www.apache.org/licenses/LICENSE-2.0.html) for more details.

__

Feel free to explore, test, and integrate Kolas.Ai's API, and reach out with any questions!
