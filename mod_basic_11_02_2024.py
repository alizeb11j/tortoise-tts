from TikTokLive import TikTokLiveClient
from TikTokLive.types.events import CommentEvent, ConnectEvent
from TikTokLive.types.events import GiftEvent
from pygame import mixer 
import re
import threading
import os
import multiprocessing 

import time

import torch
import torchaudio
import sys


from api_fast import TextToSpeech, MODELS_DIR
from utils.audio import load_audio, load_voices
from utils.text import split_and_recombine_text
  
# Starting the mixer 

path=""
path_rose="Rose.mp3"
path_star="Star.mp3"
path_GG="GG.mp3"
path_live="Live.mp3"
path_heart="Heart.mp3"
path_fire="Fire.mp3"
path_doughnut="Doughnut.mp3"
path_unknown="unknown.mp3"

Path_to_file='test.txt'
outpath = "results/tts1"
outname = "test"

myvoice="anime"
selected_voices = myvoice.split(',')
from queue import Queue
q = Queue(maxsize = 1000)
regenerate = None
if regenerate is not None:
    regenerate = [int(e) for e in regenerate.split(',')]

def get_path(giftname):

    if(giftname=="Rose"):
        path=path_rose
    elif(giftname=="GG"):
        path=path_GG
    elif(giftname=="Star"):
        path=path_star
    elif(giftname=="LIVE Fest"):
        path=path_live
    elif(giftname=="Heart Me"):
        path=path_heart
    elif(giftname=="Fire"):
        path=path_fire
    elif(giftname=="Doughnut"):
        path=path_doughnut
    else:
        path=path_unknown
    return path


# Instantiate the client with the user's username
client: TikTokLiveClient = TikTokLiveClient(unique_id="@florentinhoff")
# mixer.init()
if torch.cuda.is_available():
    tts = TextToSpeech(models_dir=MODELS_DIR, use_deepspeed=False, kv_cache=True, half=True)


# Define how you want to handle specific events via decorator
@client.on("connect")
async def on_connect(_: ConnectEvent):
    print("Connected to Room ID:", client.room_id)



async def on_comment(event: CommentEvent):
    # print(f"{event.user.nickname} -> {event.comment}")
    
    Comm=event.comment
    if Comm is not None:
      CommList = Comm.split()
      for Comment in CommList: 
        if((Comment.lower()=="hola")or(Comment.lower()=="hi") or (Comment.lower()=="hey") or (Comment.lower()=="hello")or (Comment.lower()=="helo") or (Comment.lower()=="999")):
          # print("here")
          # print(event.user.nickname)
          Nickname=event.user.nickname
          Nickname = re.sub(r"[^a-zA-Z0-9]","",Nickname)
          q.put("Hi! "+ Nickname)
          break
        
        
              

# # Define handling an event via "callback"
client.add_listener("comment", on_comment)

@client.on("gift")
@client.on("gift")
async def on_gift(event: GiftEvent):
    print(f"{event.user.unique_id} sent {event.gift.count}x \"{event.gift.info.name}\"")
    # Streakable gift & streak is over
    if event.gift.streakable and not event.gift.streaking:
        msg = f"{event.user.unique_id} sent {event.gift.count} {event.gift.info.name}"
        q.put(msg)
        #print(msg)
        #PATH=get_path(event.gift.info.name)
        #mixer.music.stop()
        #mixer.music.load(PATH)
        #mixer.music.play()


    # Non-streakable gift
    elif not event.gift.streakable:
        msg = f"{event.user.unique_id} sent {event.gift.info.name}"
        q.put(msg)
        #print(f"{event.user.unique_id} sent \"{event.gift.info.name}\"")
        #PATH=get_path(event.gift.info.name)
        #mixer.music.load(PATH)
        #mixer.music.play()

def proc_comments(que):
  print("Proc_comm")
  seed=None
  
  while True:
    #print("Running")
    #time.sleep(10)
    #continue
    if not q.empty():
      Nick_name_=q.get()

      # print(Nick_name_)
      with open(Path_to_file, 'w') as f:
          f.write(Nick_name_)
          # print(Comment.lower())
          # f.write(Comment.lower())

                  
      # Process text
      with open(Path_to_file, 'r', encoding='utf-8') as f:
          text = ' '.join([l for l in f.readlines()])
      if '|' in text:
          print("Found the '|' character in your text, which I will use as a cue for where to split it up. If this was not"
              "your intent, please remove all '|' characters from the input.")
          texts = text.split('|')
      else:
          texts = split_and_recombine_text(text)
      seed = int(time.time()) if seed is None else seed
      
      # for selected_voice in selected_voices:
      selected_voice='anime'
      voice_outpath = os.path.join(outpath, selected_voice)
      os.makedirs(voice_outpath, exist_ok=True)

      if '&' in selected_voice:
          voice_sel = selected_voice.split('&')
      else:
          voice_sel = [selected_voice]

      voice_samples, conditioning_latents = load_voices(voice_sel)
      all_parts = []
      mcount=0
      for j, text in enumerate(texts):
          start_time = time.time()
          gen = tts.tts(text, voice_samples=voice_samples, use_deterministic_seed=seed)
          end_time = time.time()
          audio_ = gen.squeeze(0).cpu()
          print("Time taken to generate the audio: ", end_time - start_time, "seconds")
          print("RTF: ", (end_time - start_time) / (audio_.shape[1] / 24000))
          f_name=os.path.join(voice_outpath, f'{Nick_name_}.wav')
          if(os.path.exists(f_name)):
            nn=Nick_name_+str(mcount)
            f_name=os.path.join(voice_outpath, f'{nn}.wav')
            mcount+=1
          torchaudio.save(f_name, audio_, 24000)
          print("Playing", text)
                
          # mixer.music.load(os.path.join(voice_outpath, f'{Nickname}.wav'))
          # mixer.music.play()
    else:
      time.sleep(1)

    
def proc_client():
    client.run()
        
proc_thread = threading.Thread(target=proc_comments, args=(q,))
client_thread = threading.Thread(target=proc_client)
 

if __name__ == '__main__':
    # Run the client and block the main thread
    # await client.start() to run non-blocking
    client_thread.start()
    proc_thread.start()
    
    proc_thread.join()
    client_thread.join()
        

# if __name__ == '__main__':
#     # Run the client and block the main thread
#     # await client.start() to run non-blocking
#     client.run()