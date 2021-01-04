#!/usr/bin/env python
import requests
import tqdm
import jiosaavn
import os
from mutagen.mp4 import MP4, MP4Cover
import threading

download_path = "./Songs" #Provide download path here
def dwnld_sng(song_dwn_url, song_id):
    with requests.get(song_dwn_url, stream=True) as r, open("{}/{}.m4a".format(download_path, song_id), "wb") as f:
        file_size = int(r.headers['Content-Length'])
        for chunk in tqdm.tqdm(
        r.iter_content(chunk_size=1024),
        total= int(file_size / 1024),
        unit = 'KB',
        desc = "Downloading {} by {}".format(song_name, artist_name),
        leave = True
        ):
            f.write(chunk)


def rename(song_id, song_name, artist_name):
    fname = "{}/{} - {}.m4a".format(download_path, song_name, artist_name)
    os.rename("{}/{}.m4a".format(download_path, song_id), "{}".format(fname))

def dwnld_img(image_url, img_name):
    response = requests.get(image_url)
    with open(img_name, 'wb') as f:
        f.write(response.content)

def save_metadata(song_id, song_name, artist_name, featured_artist, img_path, album, year, genre):
    audio_path = "{}/{}.m4a".format(download_path, song_id)
    audio = MP4(audio_path)
    audio['\xa9nam'] = song_name
    audio['\xa9alb'] = album
    audio['aART'] = artist_name
    if featured_artist != '':
        audio['\xa9ART'] = artist_name + ", " + featured_artist
    else:
        audio['\xa9ART'] = artist_name
    audio['\xa9day'] = year
    audio['\xa9gen'] = genre
    with open(img_path, "rb") as f:
        audio["covr"] = [
            MP4Cover(f.read(), imageformat=MP4Cover.FORMAT_JPEG)
        ]
    audio.save()

if __name__ == "__main__":
    while True:
        song_name = input("Enter Song Name: ")
        if song_name == "":
            continue
        else:
            try:
                song_data = jiosaavn.search_for_song(song_name.replace('with lyrics', '').strip())
                print("Which one of these you want?")
                for i in range(len(song_data)):
                    song_name = song_data[i]['title']
                    artist_name = song_data[i]['more_info']['primary_artists']
                    print("{}. {} by {}".format(i+1, song_name, artist_name))

                pref = input("Enter song number(Hit Enter for Default i,e 1): ").replace(".", '')
                if pref == '':
                    pref = 1
                else:
                    pref = int(pref)
                try:
                    if pref > len(song_data):
                        print("Number out of range. Please Enter valid number")
                    else:
                        song_id = song_data[pref-1]['id']
                        #print(song_id)
                        song_data = jiosaavn.get_song(str(song_id))
                        #print(song_data)
                        song_dwn_url = song_data['media_url']
                        song_name = song_data['song'].replace('?', '').strip()
                        artist_name = song_data['primary_artists']
                        featured_artist = song_data['featured_artists']
                        album = song_data['album']
                        year = song_data['year']
                        lang = (song_data['language'])
                        lang = lang[0].upper() + lang[1:]
                        print("Found {} by {}".format(song_name, artist_name))
                        image_url = song_data['image']
                        img_path = "{}/{}.jpg".format(download_path, song_id)
                        #print("Downloading Image")
                        t1 = threading.Thread(target=dwnld_img, args=(image_url, img_path))
                        t1.start()
                        dwnld_sng(song_dwn_url, song_id)
                        
                        fname = "{}/{} - {}.m4a".format(download_path, artist_name, song_name)
                        t1.join()
                        #print("Saving matadata")
                        save_metadata(song_id, song_name, artist_name, featured_artist, img_path, album, year, genre=lang)
                        rename(song_id, song_name, artist_name)
                        os.remove(img_path)
                
                except Exception as e:
                    print("Error: {}".format(e))
                
                
            except Exception as e:
                print("Failed to Download Song")
                print("ERROR: {}".format(e))
