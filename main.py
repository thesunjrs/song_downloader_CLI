#!/usr/bin/env python
import requests
import tqdm
import jiosaavn
import os
from mutagen.mp4 import MP4, MP4Cover
import threading

download_path = "./Songs" #Provide download path here

def dwnld_sng(song_dwn_url, song_title):
    with requests.get(song_dwn_url, stream=True) as r, open("{}/{}.m4a".format(download_path, song_title), "wb") as f:
        file_size = int(r.headers['Content-Length'])
        for chunk in tqdm.tqdm(
        r.iter_content(chunk_size=1024),
        total= int(file_size / 1024),
        unit = 'KB',
        desc = "Downloading {}".format(song_title),
        leave = True
        ):
            f.write(chunk)

def dwnld_img(image_url, img_path):
    response = requests.get(image_url)
    with open(img_path, 'wb') as f:
        f.write(response.content)

def save_metadata(audio_path, song_name, artist_name, featured_artist, img_path, album, year, genre):
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

def main():
    isdir = os.path.isdir(download_path)
    if not isdir:
        os.mkdir(download_path)
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
                elif pref.isnumeric and int(pref) <= len(song_data):
                    pref = int(pref)
                else:
                    print("Invalid Value Entered")
                    continue

                song_id = song_data[pref-1]['id']
                song_data = jiosaavn.get_song(str(song_id))
                song_name = song_data['song'].replace('?', '').strip()
                artist_name = song_data['primary_artists']
                featured_artist = song_data['featured_artists']
                song_title = "{} - {}".format(song_name, artist_name)
                audio_path = "{}/{}.m4a".format(download_path, song_title)
                img_path = "{}/{}.jpg".format(download_path, song_title)

                album = song_data['album']
                year = song_data['year']
                lang = (song_data['language'])
                lang = lang[0].upper() + lang[1:]
                image_url = song_data['image']
                
                print("Selected {} by {}".format(song_name, artist_name))

                t1 = threading.Thread(target=dwnld_img, args=(image_url, img_path))
                t1.start()
                dwnld_sng(song_dwn_url = song_data['media_url'], song_title = song_title)
                fname = "{}/{} - {}.m4a".format(download_path, artist_name, song_name)
                t1.join()
                #print("Saving matadata")
                save_metadata(audio_path = audio_path, song_name = song_name, artist_name = artist_name, featured_artist = featured_artist, img_path = img_path, album = album, year = year, genre = lang)
                os.remove(img_path)
            except Exception as e:
                print("Failed to Download Song")
                print("ERROR: {}".format(e))

if __name__ == "__main__":
    main()