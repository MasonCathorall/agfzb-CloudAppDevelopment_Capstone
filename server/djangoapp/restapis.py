from imaplib import _Authenticator
from urllib.request import HTTPBasicAuthHandler
import requests
import json
from .models import CarDealer, DealerReview
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions


# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))


def get_request(url, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    try:
        # Call get method of requests library with URL and parameters
        # if(api_key): 
        #     params = dict()
        #     params["text"] = kwargs["text"]
        #     params["version"] = kwargs["version"]
        #     params["features"] = kwargs["features"]
        #     params["return_analyzed_text"] = kwargs["return_analyzed_text"]
        #     response = requests.get(url, headers={'Content-Type': 'application/json'},
        #                             params=kwargs, auth=HTTPBasicAuthHandler('apikey', api_key))
        # else:
        response = requests.get(url, headers={'Content-Type': 'application/json'},
                                params=kwargs)
    except:
        # If any error occurs
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data

# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def post_request(url, json_payload, **kwargs):
    print(kwargs)
    print(json_payload)
    print("POST from {} ".format(url))
    try:
        response = requests.post(url, params=kwargs, json=json_payload)
    except:
        # If any error occurs
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data


# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list
def get_dealers_from_cf(url):
    results = []
    json_result = get_request(url)
    # print(json_result)
    # Retrieve the dealer data from the response
    dealers = json_result["docs"]
    # print(json_result["docs"])
    # For each dealer in the response
    for dealer in dealers:
        # Get its data in `doc` object
        # Create a CarDealer object with values in `doc` object
        dealer_obj = CarDealer(address=dealer["address"], city=dealer["city"], full_name=dealer["full_name"],id=dealer["id"], lat=dealer["lat"], long=dealer["long"], short_name=dealer["short_name"], st=dealer["st"], state=dealer["state"], zip=dealer["zip"])
        
        results.append(dealer_obj)

    return results


# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
def get_dealer_reviews_from_cf(url, dealerId):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    print(json_result["docs"])
    dealers = json_result["docs"]
    for review_doc in dealers:
        dealerReview_obj = DealerReview(
            dealership=review_doc["dealership"], 
            name=review_doc["name"], 
            purchase=review_doc["purchase"],
            review=review_doc["review"], 
            purchase_date=review_doc["purchase_date"], 
            car_make=review_doc["car_make"], 
            car_model=review_doc["car_model"],
            car_year=review_doc["car_year"], 
            sentiment="NULL", 
            id=review_doc["id"])

        dealerReview_obj.sentiment = analyze_review_sentiments(dealerReview_obj.review)
        # print(dealerReview_obj)
        results.append(dealerReview_obj)

    return results

def get_dealer_by_id_from_cf(url, dealerId):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url,dealerId=dealerId)

    dealers = json_result["docs"]
    for dealer in dealers:
        # Create a CarDealer object with values in `doc` object
        dealer_obj = CarDealer(address=dealer["address"], city=dealer["city"], full_name=dealer["full_name"],
        id=dealer["id"], lat=dealer["lat"], long=dealer["long"],
        short_name=dealer["short_name"],
        st=dealer["st"], zip=dealer["zip"],state=dealer["state"])
        results.append(dealer_obj)

    return results

def get_dealer_by_state_from_cf(url, state):
    results = []
    json_result = get_request(url,state=state)

    # For each dealer object
    dealers = json_result["docs"]

    for dealer in dealers:
        # Get its content in `doc` object
        # Create a CarDealer object with values in `doc` object
        dealer_obj = CarDealer(address=dealer["address"], city=dealer["city"], full_name=dealer["full_name"],
                                id=dealer["id"], lat=dealer["lat"], long=dealer["long"],
                                short_name=dealer["short_name"],
                                st=dealer["st"], zip=dealer["zip"],state=dealer["state"])
        results.append(dealer_obj)

    return results



# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative
def analyze_review_sentiments(text):
    api_key="eLd8XE1U0lvLh63al1GSX_6QJpegHYv_JEbmWAyXFY5B"
    url="https://api.us-east.natural-language-understanding.watson.cloud.ibm.com/instances/4a6602c4-3098-42e1-94a6-293a5b896638"
    authenticator = IAMAuthenticator(api_key) 

    natural_language_understanding = NaturalLanguageUnderstandingV1(version='2021-08-01',authenticator=authenticator) 

    natural_language_understanding.set_service_url(url) 

    response = natural_language_understanding.analyze( text=text+"hello hello hello",features=Features(sentiment=SentimentOptions(targets=[text+"hello hello hello"]))).get_result() 

    label=json.dumps(response, indent=2) 

    label = response['sentiment']['document']['label'] 

    return(label) 


