import requests
import json
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth

from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import Features,SentimentOptions


# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))
def get_request(url, **kwargs):
    print(kwargs)
    print("GET from {}".format(url))

    api_key = kwargs.get("api_key")

    try:
        if api_key:
            params = dict()
            params["text"] = kwargs["text"]
            params["version"] = kwargs["version"]
            params["features"] = kwargs["features"]
            params["return_analyzed_text"] = kwargs["return_analyzed_text"]
            response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
                                    auth=HTTPBasicAuth('apikey', api_key))
        else:
            response = requests.get(url, params=kwargs, headers={'Content-Type': 'application/json'})
    except:
        print("Network exception occurred")

    status_code = response.status_code
    print("With status {}".format(status_code))
    json_data = json.loads(response.text)
    return json_data

# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)

def post_request(url, json_payload, **kwargs):
    print(kwargs)
    print("POST to {}".format(url))

    try:
        response = requests.post(url, params=kwargs, json=json_payload)

    except:
        print("Network exception occured")
        
    status_code = response.status_code
    print("With status {}".format(status_code))
    json_data = json.loads(response.text)
    return json_data

# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list
def get_dealers_from_cf(url, **kwargs):
    results = []
    json_result = get_request(url)

    if json_result:
        dealers = json_result["rows"]

        for dealer in dealers:
            dealer_doc = dealer["doc"]
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"])
            results.append(dealer_obj)
    return results

# Create a get_rs_from_cf method to get reviews by dealer id from a cloud function

# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
def get_dealer_reviews_from_cf(url, dealer_id):
    results = []
    json_result = get_request(url, dealer_id=dealer_id)

    if json_result:
        reviews = json_result["body"]["data"]["docs"]

        for r in reviews:
            review_obj = review_obj = DealerReview(dealership=r["dealership"],
                            name=r["name"],
                            purchase=r["purchase"],
                            review=r["review"]) 
            review_obj.sentiment = analyze_review_sentiments(review_obj.review)

            if "id" in r:
                review_obj.id = r["id"]
            if "purchase_date" in r:
                review_obj.purchase_date = r["purchase_date"]
            if "car_make" in r:
                review_obj.car_make = r["car_make"]
            if "car_model" in r:
                review_obj.car_model = r["car_model"]
            if "car_year" in r:
                review_obj.car_year = r["car_year"]

            results.append(review_obj)

    return results




# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text

# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative
def analyze_review_sentiments(text):
    url = "https://api.us-south.natural-language-understanding.watson.cloud.ibm.com/instances/ff4a714e-621f-4290-8706-7f4d65d16fbe"
    api_key = "jgHMDqhsZ0yYD3zhh35gZoKfXo81wWSU3pnYshmdd8qf"
    version = "2022-03-30"
    feature = "sentiment"

    authenticator = IAMAuthenticator(api_key)
    natural_language_understanding = NaturalLanguageUnderstandingV1(version='2021-08-01',authenticator=authenticator)
    natural_language_understanding.set_service_url(url)

    response = natural_language_understanding.analyze( text=text,features=Features(sentiment=SentimentOptions(targets=[text]))).get_result()

    json.dumps(response, indent=2)

    return response['sentiment']['document']['label']