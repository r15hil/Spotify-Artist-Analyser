from django.http import HttpResponse
from django.shortcuts import render
import requests
import pandas as pd
from .forms import RawForm, RawerForm
import wikipedia
import random
import json 

CLIENT_ID = 'aac7a18b013842f58bb165716c697add'
CLIENT_SECRET = '150614d1fbdb425a86238147e6f9e20b'

AUTH_URL = 'https://accounts.spotify.com/api/token'
BASE_URL = 'https://api.spotify.com/v1/'

def Chart_Data_Gen(data):
    ChartData = {}
    datasets = []
    try:
        for album in data['short_album_name'].unique():
            ## Colour
            r = random.randint(0,255)
            g = random.randint(0,255)
            b = random.randint(0,255)
            colour = "rgb({}, {}, {}, 0.5)".format(r,g,b)
            borderColor = "rgb({}, {}, {})".format(r,g,b)

            ## Data
            data_for_each_album= []
            tmp_album = data[data['short_album_name'] == album]

            for x, track in tmp_album.iterrows():
                tmp_track = {
                    'x': round(track['danceability']*100,2),
                    'y': round(track['valence']*100,2),
                    'r': round(track['energy']*25,2),
                    'track_name': track['track_name'], 
                }
                
                data_for_each_album.append(tmp_track)

            tmp_datasets = {
                "label" : album,
                "data" : data_for_each_album,
                "backgroundColor": colour,
                "borderColor" : borderColor,
                "borderWidth" : 2,
                "hoverRadius" : -5,
                
            }
            datasets.append(tmp_datasets)
    except:
        print(" ")

    ChartData['datasets'] = datasets

    return ChartData


def home_view(request, *args, **kwargs):

    form = RawForm(request.POST or None)
    if form.is_valid():
        form.save()
        track_id = form.cleaned_data['artistID']

    context = {
        "form" : form
    }
    
    return render(request, "home.html", context)

def artist_view(request, *args, **kwargs):
     
    form = RawForm(request.POST or None)
    if form.is_valid():
        form.save()
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
    
    artist_id = artist_id.replace(" ", "%20")

    r = requests.get(BASE_URL + 'search?q=/' + artist_id + '&type=artist', 
                    headers=headers, 
                    params={'include_groups': 'artist', 'limit': 20})
    d = r.json()

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

    auth_response_data = auth_response.json()
    access_token = auth_response_data['access_token']

    headers = {
        'Authorization': 'Bearer {token}'.format(token=access_token)
    }

    artist_data =  requests.get(BASE_URL + 'artists/' + artist_id, headers=headers)
    artist_data = artist_data.json()

    artist_name = artist_data['name']
    try:
        artist_photo = artist_data['images'][1]['url']
    except:
        artist_photo = None

    artist_popularity = artist_data['popularity']
    artist_genres = artist_data['genres']
    artist_followers = artist_data['followers']['total']
    try:
        artist_bio = wikipedia.WikipediaPage(title = artist_name).summary
    except:
        try:
            artist_bio = wikipedia.page(title = artist_name+" "+artist_genres[0]).summary
        except:
            artist_bio = 'Cannot find bio'

    r = requests.get(BASE_URL + 'artists/' + artist_id + '/albums?market=US', 
                headers=headers, 
                params={'include_groups': 'album'})

    d = r.json()

    data = []
    albums = []

    for album in d['items']:

        album_name = album['name']

        trim_name = album_name.split('(')[0].strip()
        if trim_name.upper() in albums:
            continue
        albums.append(trim_name.upper())

        r = requests.get(BASE_URL + 'albums/' + album['id'] + '/tracks?market=US', 
                    headers=headers)
        try: 
            
            tracks = r.json()['items']
            for track in tracks:
                f = requests.get(BASE_URL + 'audio-features/' + track['id'], 
                    headers=headers)
                f = f.json()

                f.update({
                'track_name': track['name'],
                'album_name': album_name,
                'short_album_name': trim_name,
                'release_date': album['release_date'],
                'album_id': album['id']
                })

                data.append(f)
        except:
            continue

    df = pd.DataFrame(data)
    
    ChartData = Chart_Data_Gen(df)
    ChartData = json.dumps(ChartData)
    

    X = (df.filter(['acousticness', 'danceability', 'duration_ms', 'energy',
            'instrumentalness', 'liveness', 'loudness', 'tempo', 'valence'])
    )

    try:
        features = {
            'acousticness': X['acousticness'].mean()*100,
            'danceability': X['danceability'].mean()*100,
            'energy' : X['energy'].mean()*100,
            'instrumentalness' : X['instrumentalness'].mean()*100,
            'liveness' : X['liveness'].mean()*100,
            'loudness' : X['loudness'].mean(),
            'tempo' : X['tempo'].mean(),
            'valence' : X['valence'].mean()*100
        }
    except:
        features = {
            'acousticness': 0,
            'danceability': 0,
            'energy' : 0,
            'instrumentalness' : 0,
            'liveness' : 0,
            'loudness' : 0,
            'tempo' : 0,
            'valence' : 0
        } 

    context = {
        "form": form,
        "artist_id": artist_id,
        "artist_name" : artist_name,
        "artist_photo": artist_photo,
        "artist_bio" : artist_bio,
        "features" : features,
        "popularity" : artist_popularity,
        "genres" : artist_genres,
        "followers" : artist_followers,
        "ChartData" : ChartData,
    }

    return render(request, "analysis.html", context)
