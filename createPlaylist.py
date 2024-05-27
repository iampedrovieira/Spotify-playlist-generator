from requests import get,post
import json
import time
import os
from dotenv import load_dotenv


######## GPT CODE #########

def count_occurrences(array1, array2):
    result = {}
    for item in set(array1):  # Using set to avoid redundant counting
        count = min(array1.count(item), array2.count(item))
        if count > 0:
            result[item] = count
    return result

def save_array_to_file(array, file_name, encoding='utf-8'):
    with open(file_name, 'w', encoding=encoding) as file:
        for item in array:
            file.write(item + '\n')

def read_array_from_file(file_name):
    with open(file_name, 'r') as file:
        array = [line.strip() for line in file.readlines()]
    return array

###########################

def get_auth_header(token):
  return ({ "Authorization": "Bearer " + token})

def get_userid(token):
  url="https://api.spotify.com/v1/me"
  headers = get_auth_header(token)
  result = get(url, headers=headers)
  json_result = json.loads(result.content)

  if 'error' in json.loads(result.content):
      print('Token Error')
      print(result)
      exit()
  
  return json_result['id']

def create_playlist(token,user_id,pl_name,pl_desc):
    url = f'https://api.spotify.com/v1/users/{user_id}/playlists'
    headers = { "Authorization": "Bearer " + token, "Content-Type": "application/x-www-form-urlencoded"}
    data = {'name': pl_name,"description": pl_desc,
    "public": "true"}
    
    while True:
      result = post(url, headers=headers, data=json.dumps(data))
    
      if result.status_code == 429:
          retry_after = int(result.headers.get('Retry-After', 1))
          print(f"Rate limit exceeded. Retrying after {retry_after} seconds...")
          time.sleep(retry_after)
      else:
        break
    if 'error' in json.loads(result.content):
      print('Token Error')
      print(result)
      exit()
    return json.loads(result.content)['id']

def search_artist(token,name):
    url="https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    
    params = params = {
        'q': name,
        'type': 'artist'
    }
    
    genres_list=['big room', 'german techno', 'edm', 'slap house', 'melodic techno', 'progressive electro house', 'dutch trance', 'italian techno', 'progressive uplifting trance', 'trance', 'minimal tech house', 'dutch house', 'house', 'euphoric hardstyle', 'minimal techno', 'rawstyle', 'progressive electro housedutch trance', 'progressive house', 'brostep', 'psychedelic trance', 'future house', 'hamburg electronic', 'electro house', 'dutch edm', 'belgian dnb', 'dance pop','pop dance', 'canadian electronic']
    while True:
      result = get(url,params=params ,headers=headers)
      
      if result.status_code == 429:
          retry_after = int(result.headers.get('Retry-After', 1))
          print(f"Rate limit exceeded. Retrying after {retry_after} seconds...")
          time.sleep(retry_after)
      else:
          break
    if 'error' in json.loads(result.content):
      print('Token Error')
      print(result)
      exit()
    #Find artist
    artist_name = ''
    artist_id=''
    same_name = 0 
    best_artist_name=''
    best_artist_id=''
    for artist in json.loads(result.content)['artists']['items']:
      
      if artist['name'].upper() == name.upper():
        if same_name == 0:
          best_artist_name = artist['name']
          best_artist_id = artist['id']

        same_name = same_name + 1
        artist_id = artist['id']
        artist_name = artist['name']
        
    #Choose the best artist with same name
    if same_name > 1:
      max_genres = 0
      for artist in json.loads(result.content)['artists']['items']:
        if artist['name'].upper() == name.upper():
            max_genres_temp = len(count_occurrences(genres_list, artist['genres']))
            if max_genres_temp > max_genres:
              max_genres = max_genres_temp
              artist_id = artist['id']
             
              artist_name = artist['name']
      #This means spotify don't have artist genres defined and use the first result with the same name
      if max_genres == 0:
        artist_id = best_artist_id
        artist_name = best_artist_name
   
    return artist_id,artist_name
    
#This function return artist track based on a basic spotify recommendations 
def get_best_artist_track(token_auth,artist_name,qt_not_found_artist_count):
  artist_id,name = search_artist(token_auth,artist_name)
 
  if artist_name.upper() != name.upper():
    print('\t\tArtist not found on spotify')
    qt_not_found_artist_count = qt_not_found_artist_count + 1
    return [],qt_not_found_artist_count
  base_url=f"https://api.spotify.com/v1/recommendations?"
  q_artists = f'seed_artists={artist_id}'
  q_limit = '&limit=100'
  url = base_url + q_artists + q_limit
  headers = get_auth_header(token_auth)
  while True:
    result = get(url, headers=headers)
    
    if result.status_code == 429:
        retry_after = int(result.headers.get('Retry-After', 1))
        print(f"Rate limit exceeded. Retrying after {retry_after} seconds...")
        time.sleep(retry_after)
    else:
        break
  
  music_list = []

  if 'error' in json.loads(result.content):
      print('Token Error')
      print(result)
      exit()
  for track in json.loads(result.content)['tracks']:
    flag = False
    for artist in track['artists']:
      if name in artist['name']:
        flag = True
        
    if flag:
      music = {'name':track['name'],
              'popularity':track['popularity'],
              'id':track['id']}
      music_list.append(music)
  music_list = sorted(music_list, key=lambda x: x['popularity'],reverse=True)

  return music_list,qt_not_found_artist_count
#This record info from Tomorrowland stages
def get_tomorrowland_stage_artist():
  #Read tomorrowland page
  artist_result = get('https://www.tomorrowland.com/api/v2?method=LineUp.getArtists&eventid=17&format=json')
  stage_result = get('https://www.tomorrowland.com/api/v2?method=LineUp.getStages&eventid=17&format=json')

  performances_list =[]
  for artist in json.loads(artist_result.content)['artists']:
    
    for performance in artist['performances']:
      if 'b2b' in artist['name']:
      
        for splited_name in artist['name'].split('b2b'):
          
          performance_obj = {'artist_name':splited_name.split('(')[0].strip(' '), 'stage_id':performance['stage_id'],'date':performance['start_time']}
      else:
        performance_obj= {'artist_name':artist['name'].split('(')[0].strip(' '), 'stage_id':performance['stage_id'],'date':performance['start_time']}
      performances_list.append(performance_obj)

  stages_list = []
  #Structure data by stages,date
  #Performace objects
  for performace in performances_list:
    stage_obj = {'name':'','stage_id':performace['stage_id'],'date':'','artists':[]}

    #Create first stage object
    if len(stages_list) == 0:
      stage_obj['date'] = performace['date']
      artist_obj = [{'artist_name':performace['artist_name']}]
      stage_obj['artists'] = artist_obj
      stages_list.append(stage_obj)
    else:
      is_create = False
      for final_stage in stages_list:
        if performace['date'] == final_stage['date'] and performace['stage_id'] == final_stage['stage_id'] :
          is_create =True
          artist_obj = {'artist_name':performace['artist_name']}
          final_stage['artists'].append(artist_obj)
      if is_create == False:
        stage_obj['date'] = performace['date']
        artist_obj = [{'artist_name':performace['artist_name']}]
        stage_obj['artists'] = artist_obj
        stages_list.append(stage_obj)

  for stage_obj in stages_list:
    #Set Stage name and concat date
    stage_obj['date'] = stage_obj['date'].split(' ')[0]
    for stage in json.loads(stage_result.content)['stages']:
      if stage_obj['stage_id'] == stage['id']:
        stage_obj['name'] = stage['name']
  
  return stages_list
 
def add_tracks_to_playlist(token_auth,playlist_id,tracks):
  
  url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'
  headers = { "Authorization": "Bearer " + token_auth, "Content-Type": "application/x-www-form-urlencoded"}
  data = {'uris': tracks,"position": 0}
  
  while True:
    result = post(url, headers=headers, data=json.dumps(data))
    
    if result.status_code == 429:
        retry_after = int(result.headers.get('Retry-After', 1))
        print(f"Rate limit exceeded. Retrying after {retry_after} seconds...")
        time.sleep(retry_after)
    else:
        break
  if 'error' in json.loads(result.content):
    print('Token Error')
    print(result)
    exit()

def get_top_artist_tracks(token_auth,artist_name):
  artist_id,name = search_artist(token_auth,artist_name)
  if artist_name.upper() != name.upper():
    print('\t\tArtist not found on spotify')
    return []
  url=f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks"
  headers = get_auth_header(token_auth)
  result = get(url, headers=headers)
  while True:
    result = get(url, headers=headers)
    if result.status_code == 429:
        retry_after = int(result.headers.get('Retry-After', 1))
        print(f"Rate limit exceeded. Retrying after {retry_after} seconds...")
        time.sleep(retry_after)
    else:
        break
    
  music_list = []

  if 'error' in json.loads(result.content):
      print('Token Error')
      print(result)
      exit()
 
  for track in json.loads(result.content)['tracks']:
    music = {'name':track['name'],
              'popularity':track['popularity'],
              'id':track['id']}
    music_list.append(music)

  return music_list


def main():
  load_dotenv()
  token_auth = os.getenv("TOKEN")
  #Read save progress
  playlist_created = read_array_from_file('playlist-save.txt')
  stages = get_tomorrowland_stage_artist()
  print('Fetching user id from spotify')
  sp_userid = get_userid(token_auth)
  for stage in stages:
    print('===============')
    print("Creating playlist to " + stage['name']+' day ' +stage['date'])
    date_srt = stage['date'].split('-')[2] + '/'+ stage['date'].split('-')[1]
    stage_name = stage['name']
    pl_name = f'Tomorrowland {stage_name} {date_srt}'
    if pl_name not in playlist_created:
      track_uris_list = []
      for artist in stage['artists']:
        artist_name = artist['artist_name']
        tracks_list = get_top_artist_tracks(token_auth,artist_name)
        i = 0
        for track in tracks_list:
          i = i + 1
          if i <= 5:
            track_id = 'spotify:track:'+track['id']
            track_uris_list.append(track_id)
    
      pl_desc = "This playlist was generated automatically with spotify recommendation API. You'll find songs by the artists who will be on this stage at Tomorrowaland 2024 Some unpopular artist or group colabs may not be here"
      print(f'\tCreating Playlist {pl_name}ß on spotify')
      playlist_id = create_playlist(token_auth,sp_userid,pl_name,pl_desc)
      print("\t\t Add tracks to playlist")
      add_tracks_to_playlist(token_auth,playlist_id,track_uris_list)
      print(f'\t Playlist {pl_name} created with {len(track_uris_list)} tracks')
      
      #Auto save
      playlist_created.append(pl_name)
      save_array_to_file(playlist_created, 'playlist-save.txt')
    else:
      print("\t\t Already created")
      

if __name__ == "__main__":

  main()
 