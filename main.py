import requests
import tqdm
import jiosaavn
import os
from mutagen.mp4 import MP4, MP4Cover

download_path = "./Songs"
def dwnld_sng(song_dwn_url, song_id):
    with requests.get(song_dwn_url, stream=True) as r, open("{}/{}.mp4".format(download_path, song_id), "wb") as f:
        file_size = int(r.headers['Content-Length'])
        for chunk in tqdm.tqdm(
        r.iter_content(chunk_size=1024),
        total= int(file_size / 1024),
        unit = 'KB',
        desc = "Downloading {} by {}".format(song_name, artist_name),
        leave = True
        ):
            f.write(chunk)
    os.rename("{}/{}.mp4".format(download_path, song_id), "{}/{}.m4a".format(download_path, song_id))

def rename(song_id, song_name, artist_name):
    fname = "{}/{} - {}.m4a".format(download_path, artist_name, song_name)
    os.rename("{}/{}.m4a".format(download_path, song_id), "{}".format(fname))

def dwnld_img(image_url, song_id):
    ext = image_url.split(".")[-1]
    response = requests.get(image_url)
    img_name = "{}/{}.{}".format(download_path, song_id, ext)
    with open(img_name, 'wb') as f:
        f.write(response.content)
    return img_name

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
    print("If you want lyrics please add the word 'with lyrics' at the end of query")
    while True:
        song_name = input("Enter Song Name: ")
        if song_name == "":
            break
        else:
            if 'with lyrics' in song_name.lower():
                lyrics = True
            else:
                lyrics = False
            try:
                song_data = jiosaavn.search_song(song_name.replace('with lyrics', '').strip(), lyrics)
                print("Which one of these you want?")
                if len(song_data) >= 5:
                    for i in range(5):
                        song_name = song_data[i]['song']
                        artist_name = song_data[i]['primary_artists']
                        print("{}. {} by {}".format(i+1, song_name, artist_name))
                else:
                    for i in range(len(song_data)):
                        song_name = song_data[i]['song']
                        artist_name = song_data[i]['primary_artists']
                        print("{}. {} by {}".format(i+1, song_name, artist_name))

                pref = input("Enter song number(Hit Enter for Default i,e 1): ").strip(".")
                if pref == '':
                    pref = 1
                else:
                    pref = int(pref)
                #print(song_data[pref-1])
                try:
                    if pref > len(song_data):
                        print("Number out of range. Please Enter valid number")
                    else:
                        song_id = song_data[pref-1]['id']
                        song_dwn_url = song_data[pref-1]['media_url']
                        song_name = song_data[pref-1]['song']
                        artist_name = song_data[pref-1]['primary_artists']
                        featured_artist = song_data[pref-1]['featured_artists']
                        album = song_data[pref-1]['album']
                        year = song_data[pref-1]['year']
                        lang = (song_data[pref-1]['language'])
                        lang = lang[0].upper() + lang[1:]
                        print("Found {} by {}".format(song_name, artist_name))
                        dwnld_sng(song_dwn_url, song_id)
                        image_url = song_data[pref-1]['image']
                        #print("Downloading Image")
                        img_path = dwnld_img(image_url, song_id)
                        fname = "{}/{} - {}.m4a".format(download_path, artist_name, song_name)
                        #print("Saving matadata")
                        save_metadata(song_id, song_name, artist_name, featured_artist, img_path, album, year, genre=lang)
                        rename(song_id, song_name, artist_name)
                        
                        os.remove(img_path)
                        
                        ################################################
                        ###################GET LYRICS###################
                        if lyrics == True:
                            try:
                                lyr = jiosaavn.get_lyrics(song_id)
                                with open("{} (Lyrics).txt".format(fname), "w") as f:
                                    f.write(lyr.replace("<br>", "\n"))
                            except:
                                print("Lyrics not found")

                
                except Exception as e:
                    print("Error: {}".format(e))
                
                
            except Exception as e:
                print("Failed to Download Song")
                print("ERROR: {}".format(e))
