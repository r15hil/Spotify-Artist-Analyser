from django.http import HttpResponse
from django.shortcuts import render
import requests

CLIENT_ID = 'aac7a18b013842f58bb165716c697add'
CLIENT_SECRET = '150614d1fbdb425a86238147e6f9e20b'

AUTH_URL = 'https://accounts.spotify.com/api/token'


# Create your views here.

def home_view(request, *args, **kwargs):
    print(args, kwargs)
    print(request.user)
    #return HttpResponse("<h1>Home Page</h1>")
    return render(request, "home.html", {})

def contact_view(request, *args, **kwargs):
    # my_context = {
    #     "my_text": "This is about how to contact us",
    #     "my_number" : 123,
    #     "my_list" : [123,321,789,987]
    # }
    # POST
    auth_response = requests.post(AUTH_URL, {
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    })

    # convert the response to JSON
    auth_response_data = auth_response.json()

    # save the access token
    access_token = auth_response_data['access_token']

    headers = {
        'Authorization': 'Bearer {token}'.format(token=access_token)
    }

    # base URL of all Spotify API endpoints
    BASE_URL = 'https://api.spotify.com/v1/'

    # Track ID from the URI
    track_id = '6y0igZArWVi6Iz0rj35c1Y'

    # actual GET request with proper header
    r = requests.get(BASE_URL + 'audio-features/' + track_id, headers=headers)

    # base URL of all Spotify API endpoints
    BASE_URL = 'https://api.spotify.com/v1/'

    # Track ID from the URI
    track_id = '1fewSx2d5KIZ04wsooEBOz'

    # actual GET request with proper header
    r = requests.get(BASE_URL + 'audio-features/' + track_id, headers=headers)

    r = r.json()
    
    context = {
        'object': r
    }
    return render(request, "contact.html", context)