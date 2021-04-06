from django.http import HttpResponse
from django.shortcuts import render
import requests
import pandas as pd
from .forms import RawForm, RawerForm
import wikipedia

CLIENT_ID = 'aac7a18b013842f58bb165716c697add'
CLIENT_SECRET = '150614d1fbdb425a86238147e6f9e20b'

AUTH_URL = 'https://accounts.spotify.com/api/token'
BASE_URL = 'https://api.spotify.com/v1/'


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

    print(access_token)

    headers = {
        'Authorization': 'Bearer {token}'.format(token=access_token)
    }
    
    artist_id = artist_id.replace(" ", "%20")

    r = requests.get(BASE_URL + 'search?q=/' + artist_id + '&type=artist', 
                    headers=headers, 
                    params={'include_groups': 'artist', 'limit': 5})
    d = r.json()

    # for i in d['artists']['items']:
    #     print(i['name'])

    context = {
        "form" : form,
        "artists": d['artists']['items'],
    }

    return render(request, "artist.html", context)

def analysis_view(request, *args, **kwargs):

    form = RawForm(request.POST or None)

    if form.is_valid():
        form.save()
        #artist_id = form.cleaned_data['artistID']
        artist_id = form.cleaned_data['artistID']

    s_beginning = 'spotify:artist:'
    s_end = '.x'

    artist_id = list(request.POST.keys())[1]

    artist_id = artist_id.replace(s_beginning,'')
    artist_id = artist_id.replace(s_end,'')

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

    artist_data =  requests.get(BASE_URL + 'artists/' + artist_id, headers=headers)
    artist_data = artist_data.json()

    artist_name = artist_data['name']
    artist_popularity = artist_data['popularity']
    artist_genres = artist_data['genres']
    artist_followers = artist_data['followers']['total']
    artist_bio = wikipedia.WikipediaPage(title = artist_name).summary

    r = requests.get(BASE_URL + 'artists/' + artist_id + '/albums?market=US', 
                headers=headers, 
                params={'include_groups': 'album', 'limit':5})

    d = r.json()

    data = []   # will hold all track info
    albums = [] # to keep track of duplicates

    for album in d['items']:

        album_name = album['name']

        trim_name = album_name.split('(')[0].strip()
        if trim_name.upper() in albums:
            continue
        albums.append(trim_name.upper())

        r = requests.get(BASE_URL + 'albums/' + album['id'] + '/tracks?market=US', 
                    headers=headers)
        tracks = r.json()['items']

        for track in tracks:
            # get audio features (key, liveness, danceability, ...)
            f = requests.get(BASE_URL + 'audio-features/' + track['id'], 
                headers=headers)
            f = f.json()
            data.append(f)

    df = pd.DataFrame(data)
 
    X = (df.filter(['acousticness', 'danceability', 'duration_ms', 'energy',
            'instrumentalness', 'liveness', 'loudness', 'tempo', 'valence'])
    )

    print(X['danceability'])
    print(X['danceability'].mean())

    features = {
        'acousticness': X['acousticness'].mean(),
        'danceability': X['danceability'].mean(),
        'energy' : X['energy'].mean(),
        'instrumentalness' : X['instrumentalness'].mean(),
        'liveness' : X['liveness'].mean(),
        'loudness' : X['loudness'].mean(),
        'tempo' : X['tempo'].mean(),
        'valence' : X['valence'].mean()
    }

    context = {
        "form": form,
        "artist_id": artist_id,
        "artist_name" : artist_name,
        "artist_bio" : artist_bio,
        "features" : features,
        "popularity" : artist_popularity,
        "genres" : artist_genres,
        "followers" : artist_followers,
    }

    return render(request, "analysis.html", context)
