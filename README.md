# song_downloader
Downloads best quality (320kbps) songs with all metadata  

All the parameters are optional.

- If directory paramter is provided, all songs are downloaded in that directory. If the parameter is not provided, all songs are downloaded in current directory.
- If file parameter is given, then it reads the names of songs from file. If this parameter is not provided, it defaults to interactive mode, asking name of new song each time after comopleting of download of previous song.
- This program searches the song name provided and asks from a list of song which song the user wants to download by default, be it file mode or interactive mode. But if you dont want to be asked everytime to pick from the songs, you can add ```--dont-ask`` or ```-a``` flag.
- Downloaded songs are named in this format: ```Title - Artist``` by default. But if you want to have the file name the same as name/query you provided, you can do so by passing ```--query-as-filename``` or ```-q``` flag.  

This means if you just type ```python main.py```, it would ask you for name of song, and then ask you to pick one from search, it would download it, and this would be repeated. To exit, just press Ctrl+C.

# Contributors
Ankit Sangwan (initial author)
Hemish (Contributor) <hemish04082005@gmail.com>