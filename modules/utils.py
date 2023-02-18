from pydub import AudioSegment
import torch
from transformers import pipeline,AutoProcessor, WhisperForConditionalGeneration
import re
import os
from datetime import datetime
def create_dir(path):
    if not os.path.exists(path):
        os.mkdir(path)
def create_output_structure(output_path, project_name, project_timestamp):
    # Create the output directory
    if not os.path.exists(output_path):
        os.mkdir(output_path)
    #if not os.path.exists(os.path.join(output_path, project_name)):
    #    os.mkdir(os.path.join(output_path, project_name))
    if not os.path.exists(os.path.join(output_path, project_name + '_' + project_timestamp)):
        os.mkdir(os.path.join(output_path, project_name + '_' + project_timestamp))
    if not os.path.exists(os.path.join(output_path, project_name + '_' + project_timestamp, 'wavs')):
        os.mkdir(os.path.join(output_path, project_name + '_' + project_timestamp, 'wavs'))
    output_path = os.path.join(output_path, project_name + '_' + project_timestamp)
    #create train.txt and valid.txt
    with open(os.path.join(output_path, 'train.txt'), 'w') as f:
        f.write('')
    with open(os.path.join(output_path, 'valid.txt'), 'w') as f:
        f.write('')
    
    #create_dir(output_path)
    return output_path
def add_to_textfile(file_path, text):
    with open(file_path, "a") as text_file:
        text_file.write(text)

def convert_to_wav(file_path):
    # Load the audio file
    audio = AudioSegment.from_file(file_path)

    # Add a silent spacer at the beginning
    spacer_milli = 2000
    spacer = AudioSegment.silent(duration=spacer_milli)
    audio = spacer.append(audio, crossfade=0)

    # Export the audio to a WAV file
    base_path, ext = os.path.splitext(file_path)
    output_path = base_path + '.wav'
    audio.export(output_path, format='wav')

    return output_path
def generate_timestamp():
    #generate project timestamp
    project_timestamp = datetime.now().strftime("%Y_%m_%d-%H_%M")
    return project_timestamp
def load_pyannote_audio_pipeline(model_name,use_auth_token=None):
    from pyannote.audio import Pipeline
    if use_auth_token is None:
        pipeline = Pipeline.from_pretrained(model_name)
    else:
        pipeline = Pipeline.from_pretrained(model_name,use_auth_token=use_auth_token)
    return pipeline
def load_pyannote_audio_model(model_name,use_auth_token=None):
    from pyannote.audio import Model
    if use_auth_token is None:
        pipeline = Model.from_pretrained(model_name)
    else:
        pipeline = Model.from_pretrained(model_name,use_auth_token=use_auth_token)
    return pipeline
def segment_audio_file(file_path, model):
    from pyannote.audio.pipelines import VoiceActivityDetection
    pipeline = VoiceActivityDetection(segmentation=model)
    HYPER_PARAMETERS = {
    # onset/offset activation thresholds
        "onset": 0.6, "offset": 0.4,
        # remove speech regions shorter than that many seconds.
        "min_duration_on": 2.0,
        # fill non-speech regions shorter than that many seconds.
        "min_duration_off": 0.0
    }
    pipeline.instantiate(HYPER_PARAMETERS)
    vad = pipeline(file_path)
    #pyannote.core.Annotation object
    #return a list of segments
    #for segment, _, label in vad.itertracks(yield_label=True):
    #    if label == "SPEECH":
    #        print(f"Speech found from {segment.start:.1f}s to {segment.end:.1f}s")
    #print(vad)
    return str(vad)
def diarize_audio_file(file_path, pipeline):
    DEMO_FILE = {'uri': 'blabla', 'audio': file_path}
    dz = pipeline(DEMO_FILE)  
    return str(dz)

#Preparing audio files according to the diarization
def millisec(timeStr):
  #print(timeStr)
  #remove [ and ]
  timeStr = timeStr.replace("[","").replace("]","")
  spl = timeStr.split(":")
  s = (int)((int(spl[0]) * 60 * 60 + int(spl[1]) * 60 + float(spl[2]) )* 1000)
  return s
def group_diarization(diarization):
    
    dzs = diarization.splitlines()

    groups = []
    g = []
    lastend = 0

    for d in dzs:   
        if g and (g[0].split()[-1] != d.split()[-1]):      #same speaker
            groups.append(g)
            g = []
        
        g.append(d)
        
        end = re.findall('[0-9]+:[0-9]+:[0-9]+\.[0-9]+', string=d)[1]
        end = millisec(end)
        if (lastend > end):       #segment engulfed by a previous segment
            groups.append(g)
            g = [] 
        else:
            lastend = end
    if g:
        groups.append(g)
    #print(*groups, sep='\n')
    return groups
def group_segmentation(diarization):
    
    dzs = diarization.splitlines()

    groups = []
    g = []
    lastend = 0
    #print(dzs)
    for d in dzs:   
        if g:      #same speaker
            groups.append(g)
            g = []
        
        g.append(d)
        
        end = re.findall('[0-9]+:[0-9]+:[0-9]+\.[0-9]+', string=d)[1]
        end = millisec(end)
        if (lastend > end):       #segment engulfed by a previous segment
            groups.append(g)
            g = [] 
        else:
            lastend = end
    if g:
        groups.append(g)
    #print(*groups, sep='\n')
    return groups
def segment_file_by_diargroup(file_path,output_path, groups,gidx=-1):
    audio = AudioSegment.from_wav(file_path)
    gidx = gidx
    for g in groups:
        start = re.findall('[0-9]+:[0-9]+:[0-9]+\.[0-9]+', string=g[0])[0]
        end = re.findall('[0-9]+:[0-9]+:[0-9]+\.[0-9]+', string=g[-1])[1]
        start = millisec(start) #- spacermilli
        end = millisec(end)  #- spacermilli
        #print(start, end)
        gidx += 1
        file = audio[start:end].export(os.path.join(output_path,str(gidx) + '.wav'), format='wav')
        #print(file)
    return gidx
def init_transcribe_pipeline(model_name,device=0):
    pipe = pipeline(
        "automatic-speech-recognition",
        model=model_name,
        chunk_length_s=30,
        device=device,
    )
    
    return pipe
def transcribe_audio(audio_file,pipe):
    # Load the audio file
    
    #audio = AudioSegment.from_file(audio_file)

    # Convert to raw audio data
    #raw_audio_data = audio.raw_data
    #sample_rate = audio.frame_rate
    #sample_width = audio.sample_width
    #num_channels = audio.channels

    # Create the ASR pipeline

    # Process the audio file
    #prediction = pipe(audio, return_timestamps=True)["chunks"]
    prediction = pipe(audio_file)["text"]
    #print(prediction)
    return prediction