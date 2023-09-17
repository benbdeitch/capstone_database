
from app.blueprints.API.helper_functions.get_from_database.friend_requests import get_friend_requests
from app.blueprints.API.helper_functions.get_from_database.friends_list import get_friends
from app.blueprints.API.helper_functions.get_from_database.recommendations import get_recommendations

from app.blueprints.API.helper_functions.get_from_database.reading_history import get_reading_history
from app.blueprints.API.helper_functions.get_from_database.reading_list import get_reading_list

#This function is for swiftly accessing the majority of the account's information. It is used when initially loading the webpage, and when manually refreshing it, to handle desyncs between the browser and database. 
#The 'user' object it accepts is the user ID of the associated account. 
def get_account_data(user):
    #Setting up the initial response. These are the categories that it is defined upon, written out at the beginning for easier comprehension. Regardless of the data, it will always return a dictionary with exactly these keys. 
    response = { 'username': "", 'token': "", 'email': "", 'friends':{}, 'friendRequests': {"in": [], "out":[]}, 'readingList':[], 'readingHistory':[], 'recommendations':{'in': [], 'out': []}}

    #Accessing the user's reading list. 
    response["readingList"] = get_reading_list(user)

    #Accessing the user's Reading History.
    response["readingHistory"] = get_reading_history(user)

   #Accesses the Friends list
    response["friends"] = get_friends(user)
    
    #Accessing incoming Recommendations: 
    response["recommendations"] = get_recommendations(user)

    #Accessing  incoming Friend Requests:
    response["friendRequests"] = get_friend_requests(user)
    print(response)
    return response

