from django.http import HttpResponse
from django.shortcuts import render
import requests
import pandas as pd
from .forms import RawForm, RawerForm

CLIENT_ID = 'aac7a18b013842f58bb165716c697add'
CLIENT_SECRET = '150614d1fbdb425a86238147e6f9e20b'

AUTH_URL = 'https://accounts.spotify.com/api/token'


# Create your views here.

def home_view(request, *args, **kwargs):

    form = RawForm(request.POST or None)
    if form.is_valid():
        form.save()
        print(form.cleaned_data['artistID'])
        track_id = form.cleaned_data['artistID']

    context = {
        "form" : form
    }
    
    return render(request, "home.html", context)



def contact_view(request, *args, **kwargs):

    form = RawForm(request.POST or None)
    if form.is_valid():
        form.save()
        print(form.cleaned_data['artistID'])
        track_id = form.cleaned_data['artistID']
    else:
        track_id = '6y0igZArWVi6Iz0rj35c1Y' 

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

    # actual GET request with proper header
    r = requests.get(BASE_URL + 'audio-features/' + track_id, headers=headers)

    r = r.json()
    
    context = {
        'form' : form,
        'object': r
    }

    return render(request, "contact.html", context)



#spotify:artist:3Nrfpe0tUJi4K4DXYWgMUX
def artist_view(request, *args, **kwargs):

    form = RawForm(request.POST or None)
    if form.is_valid():
        form.save()
        print(form.cleaned_data['artistID'])
        #artist_id = form.cleaned_data['artistID']
        artist_id = form.cleaned_data['artistID']
    else:
        artist_id = '36QJpDe2go2KgaRleHCDTp'

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
    
    #artist_id = '36QJpDe2go2KgaRleHCDTp'
    print("before: ", artist_id)
    artist_id = artist_id.replace(" ", "%20")
    print("after: ", artist_id)

    r = requests.get(BASE_URL + 'search?q=/' + artist_id + '&type=artist', 
                    headers=headers, 
                    params={'include_groups': 'artist', 'limit': 5})
    d = r.json()
    for i in d['artists']['items']:
        print(i['name'])

    context = {
        "form" : form,
        "artists": d['artists']['items'],
    }

    return render(request, "artist.html", context)