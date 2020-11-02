import base64
import jiosaavn

def format_song(data,lyrics):
    try:
        url = data['media_preview_url']
        url = url.replace("preview", "aac")
        if data['320kbps']=="true":
            url = url.replace("_96_p.mp4", "_320.mp4")
        else:
            url = url.replace("_96_p.mp4", "_160.mp4")
        data['media_url'] = url
    except KeyError or TypeError:
        data['media_url'] = decrypt_url(data['encrypted_media_url'])
        if data['320kbps']!="true":
            data['media_url'] = data['media_url'].replace("_320.mp4","_160.mp4")

    data['song'] = format(data['song'])
    data['music'] = format(data['music'])
    data['singers'] = format(data['singers'])
    data['starring'] = format(data['starring'])
    data['album'] = format(data['album'])
    data["primary_artists"] = format(data["primary_artists"])
    data['image'] = data['image'].replace("150x150","500x500")

    if lyrics:
        if data['has_lyrics']=='true':
            data['lyrics'] = jiosaavn.get_lyrics(data['id'])
        else:
            data['lyrics'] = None

    try:
        data['copyright_text'] = data['copyright_text'].replace("&copy;","©")
    except KeyError:
        pass
    return data