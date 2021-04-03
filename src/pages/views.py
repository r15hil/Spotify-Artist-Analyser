from django.http import HttpResponse
from django.shortcuts import render
import requests
import pandas as pd
from .forms import RawForm

CLIENT_ID = 'aac7a18b013842f58bb165716c697add'
CLIENT_SECRET = '150614d1fbdb425a86238147e6f9e20b'

AUTH_URL = 'https://accounts.spotify.com/api/token'


# Create your views here.

def home_view(request, *args, **kwargs):
    return render(request, "home.html", {})



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




def artist_view(request, *args, **kwargs):

    form = RawForm(request.POST or None)
    if form.is_valid():
        form.save()
        print(form.cleaned_data['artistID'])

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
    
    artist_id = '36QJpDe2go2KgaRleHCDTp'

    # pull all artists albums
    r = requests.get(BASE_URL + 'artists/' + artist_id + '/albums', 
                    headers=headers, 
                    params={'include_groups': 'album', 'limit': 2})
    d = r.json()

    data = []   # will hold all track info
    albums = [] # to keep track of duplicates

    # loop over albums and get all tracks
    for album in d['items']:
        album_name = album['name']

        # here's a hacky way to skip over albums we've already grabbed
        trim_name = album_name.split('(')[0].strip()
        if trim_name.upper() in albums or int(album['release_date'][:4]) > 1983:
            continue
        albums.append(trim_name.upper()) # use upper() to standardize
        
        # pull all tracks from this album
        r = requests.get(BASE_URL + 'albums/' + album['id'] + '/tracks', headers=headers)
        tracks = r.json()['items']
        
        for track in tracks:
            # get audio features (key, liveness, danceability, ...)
            f = requests.get(BASE_URL + 'audio-features/' + track['id'], 
                headers=headers)
            f = f.json()
            
            # combine with album info
            f.update({
                'track_name': track['name'],
                'album_name': album_name,
                'short_album_name': trim_name,
                'release_date': album['release_date'],
                'album_id': album['id']
            })
            
            data.append(f)

    df = pd.DataFrame(data)
    print(df.head())

    context = {
        "form" : form,
        "danceability": df['danceability'].mean(),
        "loudness": df['loudness'].mean(),
        "energy": df['energy'].mean(),
    }

    return render(request, "artist.html", context)