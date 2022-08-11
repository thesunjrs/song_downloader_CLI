#!/usr/bin/env python
import requests
import tqdm
import jiosaavn
import os
from mutagen.mp4 import MP4, MP4Cover
import threading
import argparse

def dwnld_sng(song_dwn_url, song_title, download_path):
    with requests.get(song_dwn_url, stream=True) as r, open(f"{os.path.join(download_path, song_title)}.m4a", "wb") as f:
        file_size = int(r.headers['Content-Length'])
        for chunk in tqdm.tqdm(r.iter_content(chunk_size=1024), total=file_size // 1024, unit = 'KB', desc=f"Downloading {song_title}", leave = True):
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
        audio['\xa9ART'] = f"{artist_name}, {featured_artist}"
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
    # Adding arguments for parsing
    parser = argparse.ArgumentParser(description="Download songs with metadata in 320kbps")
    parser.add_argument("--directory", '-d', required=False, nargs=1, metavar='/path/to/directory/in/os/specific/format')
    parser.add_argument("--file", '-f', required=False, nargs=1, metavar='path/to/file/containing/names/of/songs')
    parser.add_argument("--dont-ask", '-a', action='store_true', default=False, help="Do not ask which song to download from search and automatically pick the first entry")
    parser.add_argument("--query-as-filename", '-q', action='store_true', default=False, help="The filenames of downloaded songs would be same as name/query given, instead of general 'Title - Artist' format")

    args = parser.parse_args()


    download_path = args.directory
    download_path = os.getcwd() if args.directory is None else download_path[0]
    # if the directory does not exist, then create it
    isdir = (os.path.isdir(download_path) and os.path.exists(download_path))
    if not isdir:
        os.mkdir(download_path)

    mode = 'interactive' if args.file is None else 'file'
    if mode == 'file':
        if not os.path.exists(args.file[0]):
            raise f"No such file {args.file} present"
        with open(args.file[0], "rt") as f:
            length_of_file = len(f.readlines())
            x = 0 # Counter variable which stores what line of file we have reached in while loop
        f = open(args.file[0], "rt") # again opening so that readline again starts from first line


    while True:
        if mode == 'file':
            if x >= length_of_file:
                break
            song_name = str(f.readline()).strip()
            x += 1
        elif mode == 'interactive':
            song_name = ''
            try:
                song_name = input("Enter name of song: ")
            except KeyboardInterrupt:
                print("\nExiting program")
                break
        try:
            initial_query_name_given = song_name
            if song_name == "":
                continue
            try:
                song_data = jiosaavn.search_for_song(song_name.replace('with lyrics', '').strip())
                if args.dont_ask:
                    song_id = song_data[0]['id'] # Picking the first entry if dont ask is enabled
                else: # Asking for which song to pick if dont ask is disabled (default)
                    print("Which one of these you want?")
                    for i in range(len(song_data)):
                        song_name = song_data[i]['title']
                        subtitle = song_data[i]['description']
                        pre = f"{i + 1}. "
                        print(f"{pre}{song_name}\n{' ' * len(pre)}{subtitle}")

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
                song_name = song_data['song'].replace('?', '').replace(':','').strip()
                artist_name = song_data['primary_artists']
                featured_artist = song_data['featured_artists']
                song_title = (
                    initial_query_name_given
                    if args.query_as_filename
                    else f"{song_name} - {artist_name}"
                )

                audio_path = f"{os.path.join(download_path, song_title)}.m4a"
                img_path = f"{os.path.join(download_path, song_title)}.jpg"

                album = song_data['album']
                year = song_data['year']
                lang = (song_data['language'])
                lang = lang[0].upper() + lang[1:]
                image_url = song_data['image']

                print(f"Selected {song_name} by {artist_name}")

                t1 = threading.Thread(target=dwnld_img, args=(image_url, img_path))
                t1.start()
                dwnld_sng(song_dwn_url = song_data['media_url'], song_title = song_title, download_path=download_path)
                fname = (
                    f"{initial_query_name_given}.m4a"
                    if args.query_as_filename
                    else os.path.join(
                        download_path, f"{artist_name} - {song_name}.m4a"
                    )
                )

                t1.join()
                #print("Saving matadata")
                save_metadata(audio_path = audio_path, song_name = song_name, artist_name = artist_name, featured_artist = featured_artist, img_path = img_path, album = album, year = year, genre = lang)
                os.remove(img_path)
            except Exception as e:
                print("Failed to Download Song")
                print(f"ERROR: {e}")

        except KeyboardInterrupt:
            print("\nExiting Program")
            break

if __name__ == "__main__":
    main()