#this script takes a list of song names and downloads them from youtube
#it also downloads the lyrics and saves them in a text file with the same name as the song
#it also downloads the video and saves the subtitles in a srt file with the same name as the song

import youtube_dl
import re
import time
import lyricsgenius as lg
import os
from youtube_transcript_api import YouTubeTranscriptApi
import requests

#this function takes a song name and returns the youtube url of the first result
def get_url(song_name):
    #go to YouTube and search for the song
    search_url = "https://www.youtube.com/results?search_query=" + song_name
    search_url+= "&sp=EgIoAQ%253D%253D"

    #get the html of the search results
    html = requests.get(search_url).text
    #get the title of the first video
    title = re.findall(r"\"title\":{\"runs\":\[{\"text\":\"(.+?)\"}],\"accessibility\"", html)[0]
    
    print("="*10+"\n{}\na été trouvé sous le nom de\n{}\n".format(song_name, title)+'-'*10)
    #before continuing, wait for the user to press enter, otherwise skip the song
    butt = input("Appuyez sur entrée pour continuer,\nsur n pour passer à la chanson suivante,\nou sur r pour télécharger la chanson en la renommant avec le nouveau nom\n")
    if butt == 'n':
        return None

    #find the first video id
    video_id = re.findall(r"watch\?v=(\S{11})", html)[0]

    #create the url
    url = "https://www.youtube.com/watch?v=" + video_id
    return (url, title if butt == 'r' else song_name)

#this function takes a song name and gets the lyrics with a GENIUS API
def get_non_aligned_lyrics(song_name):
    api_key = "tD7BvuC0DyOU1s85INC0JtYNfcARkNWZc9cOlCIMG4zr14hwKaOe0pPYm-tc4Lkf"
    genius = lg.Genius(api_key)
    #try to get the lyrics 10 times, if it fails, return an empty string
    for i in range(10):
        try:
            song = genius.search_song(song_name)
            break
        except:
            print('failed to get lyrics for {}'.format(song_name))
            time.sleep(1)

    return song.lyrics


#this function takes a song name and downloads the song into the the theme folder
def download_song(song_name, theme_name):
    #get script absolute path
    script_path = os.path.dirname(os.path.realpath(__file__))
    #theme folder is in the same folder as the script
    theme_name = os.path.join(script_path, theme_name)
    #make sure the theme folder exists
    if not os.path.exists(theme_name):
        os.mkdir(theme_name)
    try:
        #get the url of the song
        url, song_name = get_url(song_name)
    except:
        print("Vidéo non trouvée pour {}".format(song_name))
        return
    #download video in mp3
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': '{}/{}.%(ext)s'.format(theme_name, song_name),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    #download the song
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


#this function takes a song name and downloads the lyrics, it saves the lyrics in a text file with the same name as the song
def download_non_aligned_lyrics(song_name, theme_name):
    lyrics = get_non_aligned_lyrics(song_name)
    lyrics = lyrics.replace('/', '')
    lyrics = lyrics.replace('\\', '')
    #get script absolute path
    script_path = os.path.dirname(os.path.realpath(__file__))
    #theme folder is in the same folder as the script
    theme_name = os.path.join(script_path, theme_name)
    #make sure the theme folder exists
    if not os.path.exists(theme_name):
        os.mkdir(theme_name)
    file = open('{}/{}.txt'.format(theme_name, song_name), 'w', encoding='utf-8')
    file.write(lyrics)
    file.close()

def download_video_and_aligned_lyrics(song_name, theme_name):
    #get script absolute path
    script_path = os.path.dirname(os.path.realpath(__file__))
    #theme folder is in the same folder as the script
    theme_name = os.path.join(script_path, theme_name)
    #make sure the theme folder exists
    if not os.path.exists(theme_name):
        os.mkdir(theme_name)
    
    # get the video id of the first search result
    #DEAL WITH THIS
    try :
        url, song_name = get_url(song_name)
        video_id = url.split('=')[1]
    except:
        print("Vidéo non trouvée pour {}".format(song_name))
        return

    try:    
        # assigning srt variable with the list
        # of dictionaries obtained by the get_transcript() function
        # get language from the theme name
        language = theme_name.split('(')[1].split(')')[0]
        srt = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])

        #create a file with the same name as the song
        file = open('{}/{}.srt'.format(theme_name, song_name), 'w', encoding='utf-8')

        # iterating through all the dictionaries
        for i in range(len(srt)):
            # writing start time
            file.write(str(srt[i]['start']))
            file.write("-->")
            # writing end time
            file.write(str(srt[i]['start'] + srt[i]['duration']))
            file.write("\n")
            # writing text
            file.write(str(srt[i]['text']))
            file.write("\n\n")

        # closing the file
        file.close()
    except:
        print('Sous-titres non trouvés pour {}'.format(song_name))
        return
    
    #download video in mp3 without verbose
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': '{}/{}.%(ext)s'.format(theme_name, song_name),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True
    }

    #download the song
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

french_songs = [
    'Bigflo et Oli - Dommage',
    'Angèle - Balance ton quoi',
    'Vitaa & Slimane - Ça va ça vient',
    'Angèle - Tout oublier',
    # 'Angèle - Bruxelles',
    # "Mulan - Comme un homme Disney",
    # "Stromae - Papaoutai",
    # "Stromae - Tous les mêmes",
    # "Stromae - Formidable",
    # "Stromae - Alors on danse",
    # "Stromae - Carmen",
    # "Stromae - Ta fête",
    # "Stromae - Quand c'est",
    # "Stromae - Ave Cesaria",
    # "Stromae - Sommeil",
    # "Stromae - L'enfer",
    # "Stromae - Fils de joie",
    # "Disney - Le Roi Lion - L'histoire de la vie",
    # "Disney - Le Roi Lion - Je voudrais déjà être roi",
    # "Disney - Le Roi Lion - Hakuna Matata",
    # "Disney - Le Roi Lion - L'amour brille sous les étoiles",
    # "Disney - Tarzan - Enfant de l'homme",
    # "Disney - Tarzan - Deux mondes",
    # "Disney - Tarzan - De zéro en héros",
    # "Disney - Aladdin - Ce rêve bleu",
    # "Disney - Aladdin - Je suis ton meilleur ami",
    # "Disney - Aladdin - Prince Ali",
    # "Disney - La belle et la bête - Belle",
    # "Disney - La reine des neiges - Libérée, délivrée",
    # "Disney - La petite sirène - Sous l'océan",
    # "Disney - La petite sirène - Partir là-bas",
    # "Disney - La petite sirène - Embrasse-la",
    # "Disney - Zootopie - Essaye",
    # "Disney - Zootopie - Le jour",
    # "Disney - Oliver et compagnie - Pour être un homme",
    # "Disney - Oliver et compagnie - Bonne compagnie",
    # "Disney - Pocahontas - L'air du vent",
    # "Disney - Pocahontas - Des sauvages",
    # "Disney - Pocahontas - Au-delà de la rivière",
    # # "Disney - Mulan - Comme un homme",
    # "Disney - Mulan - Une belle fille à aimer",
    # "Disney - Mulan - Honneur à tous",
    # "Disney - Mulan - Réflexion",
    # "Disney - Le bossu de Notre-Dame - Les bannis ont droit d'amour",
    # "Disney - Le bossu de Notre-Dame - Le temps des cathédrales",
    # "Disney - Le bossu de Notre-Dame - Dieu que la vie est injuste",
    # "Disney - Le bossu de Notre-Dame - Les cloches de Notre-Dame",
    # "Disney - Kuzco - Monde parfait",
    # "Disney - Kuzco - Il viendra",
    # "Disney - Kuzco - Pour être un homme",
    # "Disney - Là-haut - Là-haut",
    # "Disney - Là-haut - Le chant du guerrier",
    # "Disney - Là-haut - Le voyage de Carl",
    # "Disney - Coco - Un poco loco",
    # "Disney - Coco - La Llorona",
    # "Disney - Toy Story - Je suis ton ami",
    # "Disney - Frère des ours - Bienvenue",
    # "Disney - Frère des ours - Transformation",
    # "Disney - Frère des ours - Grand frère",
    # "Disney - Frère des ours - Si je t'avais dans mon équipe",
    # "Disney - Frère des ours - Je m'en vais",
    # "Disney - Frère des ours - Le grand esprit de la forêt",
    # "Disney - Dumbo - L'éléphant",
    # "Disney - Dumbo - La chanson des éléphants roses",
    # "Disney - Dumbo - La chanson du clown",
    # "Disney - Dumbo - La chanson de la pluie",
    # "Disney - Winnie l'ourson - Je suis un petit ourson tout mignon",
    # "Disney - Winnie l'ourson - Je chasse de miel",
    # "Disney - Cendrillon - C'est ça l'amour",
    # "Disney - Cendrillon - Tendre rêve",
    # "Disney - Cendrillon - Bibbidi-Bobbidi-Boo",
    # "Disney - Cendrillon - Un sourire en chantant",
    # "Disney - Vaiana - Le bleu lumière",
    # "Disney - Blanche-Neige et les sept nains - Un jour mon prince viendra",
    # "Disney - Blanche-Neige et les sept nains - Sifflez en travaillant",
    # "Disney - Blanche-Neige et les ssept nains - Heigh-Ho",
    # "Disney - Nemo - Sous l'océan",
    # "Disney - Nemo - Le monde de Nemo",
    # "Disney - Nemo - La vie est belle",
]

for song in french_songs:
    download_video_and_aligned_lyrics(song, 'french(fr)')