import argparse
import configparser
import os
from modules.utils import *
from datetime import datetime
import sys
import colorama
from tqdm import tqdm
colorama.init(strip=not sys.stdout.isatty()) # strip colors if stdout is redirected
from termcolor import cprint 
from pyfiglet import figlet_format
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert an audio file to WAV format')
    parser.add_argument('file_path', help='Path to the file or directory to convert')
    parser.add_argument('-output_path', help='Path to the output directory', default=os.getcwd()+os.sep+'output')
    parser.add_argument('-project_name', help='project_name', type=str, default='none')
    parser.add_argument('-whisper_model', help='Which whisper model to use, HF repo address', default='openai/whisper-large-v2')
    parser.add_argument('-device', help='Which device to use, cpu or cuda', default='cuda')
    parser.add_argument('-mode', help='Automatic diarization and segmentation', default='segment and transcribe', type=str, choices=['auto', 'segment and transcribe', 'diarize', 'transcribe'])
    parser.add_argument('-diaization_model', help='Which diarization model to use, HF repo address', default='pyannote/speaker-diarization')
    parser.add_argument('-segmentation_model', help='Which segmentation model to use, HF repo address', default='pyannote/segmentation')
    parser.add_argument('-seg_onset', help='onset activation threshold, influences the segment detection', default=0.6, type=float)
    parser.add_argument('-seg_offset', help='offset activation threshold, influences the segment detection', default=0.4, type=float)
    parser.add_argument('-seg_min_duration', help='minimum duration of a segment, remove speech regions shorter than that many seconds.', default=2.0, type=float)
    parser.add_argument('-seg_min_duration_off', help='fill non-speech regions shorter than that many seconds.', default=0.0, type=float)
    parser.add_argument('-hf_token', help='Huggingface token', default='')
    parser.add_argument('-valid_ratio', help='Ratio of validation data', default=0.2, type=float)
    parser.add_argument('-ignore-cofnig', help='Ignore the config, specifiy your own setting sin CLI', action='store_true')
    args = parser.parse_args()
    #check for config.ini
    if os.path.isfile('config.ini') and not args.ignore_cofnig:
        config = configparser.ConfigParser()
        config.read('config.ini')
        args.whisper_model = config['DEFAULT']['whisper_model']
        args.device = config['DEFAULT']['device']
        args.diaization_model = config['DEFAULT']['diaization_model']
        args.segmentation_model = config['DEFAULT']['segmentation_model']
        args.valid_ratio = float(config['DEFAULT']['valid_ratio'])
        args.hf_token = config['DEFAULT']['hf_token']
        args.seg_onset = float(config['DEFAULT']['seg_onset'])
        args.seg_offset = float(config['DEFAULT']['seg_offset'])
        args.seg_min_duration = float(config['DEFAULT']['seg_min_duration'])
        args.seg_min_duration_off = float(config['DEFAULT']['seg_min_duration_off'])
    if not os.path.isfile('config.ini') and not args.ignore_cofnig:
        #create config.ini
        config = configparser.ConfigParser()
        config['DEFAULT'] = {'hf_token': ''}
        config['DEFAULT']['hf_token'] = ''
        config['DEFAULT']['whisper_model'] = 'openai/whisper-large-v2'
        config['DEFAULT']['device'] = 'cuda'
        config['DEFAULT']['diaization_model'] = 'pyannote/speaker-diarization'
        config['DEFAULT']['segmentation_model'] = 'pyannote/segmentation'
        config['DEFAULT']['valid_ratio'] = str(0.2)
        config['DEFAULT']['seg_onset'] = str(0.6)
        config['DEFAULT']['seg_offset'] = str(0.4)
        config['DEFAULT']['seg_min_duration'] = str(2.0)
        config['DEFAULT']['seg_min_duration_off'] = str(0.0)
        with open('config.ini', 'w') as configfile:
            config.write(configfile)
    #check if thre's a .TOKEN file in the current directory
    cprint(figlet_format('OZEN', font='starwars'),
       'yellow', 'on_black', attrs=['bold'])
    #cprint(figlet_format('TOOLKIT', font='starwars'),
    #   'yellow', 'on_black', attrs=['bold'])
    if args.hf_token == '':
            #colorama.init()
            print(colorama.Fore.RED + 'No Huggingface Token found' + colorama.Fore.RESET)
            #prompt for token
            args.hf_token = input('This tool uses PyAnnote which requires the user to accept its terms on the model page\nPlease visit https://huggingface.co/pyannote/segmentation and create a token to paste here. \nTo continue enter your Huggingface token: ')
            if args.hf_token == '':
                print('No token entered, exiting...')
                exit()
            elif args.hf_token != '' and not args.ignore_cofnig:
                config['DEFAULT']['hf_token'] = args.hf_token
                with open('config.ini', 'w') as configfile:
                    config.write(configfile)
    if not args.file_path:
        parser.print_help()
        exit()
    file_path = args.file_path
    timestamp = generate_timestamp()
    if args.project_name == 'none':
        args.project_name = os.path.basename(os.path.normpath(file_path))
    output_path = create_output_structure(args.output_path, args.project_name, timestamp)
    train_file = os.path.join(output_path, 'train.txt')
    valid_file = os.path.join(output_path, 'valid.txt')
    wavs_path = os.path.join(output_path, 'wavs')
    if os.path.isfile(file_path):
        # Convert a single file
        file_ext = os.path.splitext(file_path)[-1].lower()
        file_path, filename = os.path.split(file_path)
        if file_ext in ['.mp3', '.m4a', '.flac', '.ogg', '.wav']:
            if file_ext != '.wav':
                print(colorama.Fore.GREEN + 'Converting to WAV...' + colorama.Fore.RESET)
                file_path = convert_to_wav(os.path.join(file_path, filename))
            else:
                    file_path = os.path.join(file_path, filename)
            if args.mode == 'auto':
                print(colorama.Fore.GREEN + 'Loading Diraization Model...' + colorama.Fore.RESET)
                pipe = load_pyannote_audio_pipeline(args.diaization_model, args.hf_token)
                print(colorama.Fore.GREEN + 'Diarizing...' + colorama.Fore.RESET)
                diarization = diarize_audio_file(file_path, pipe)
                #mil = millisec(diarization)
                print(colorama.Fore.GREEN + 'Grouping Diarization...' + colorama.Fore.RESET)
                dir_groups = group_diarization(diarization)
                groups = group_diarization(diarization)
                print(colorama.Fore.GREEN + 'Segmenting...' + colorama.Fore.RESET)
                wavs = segment_file_by_diargroup(file_path, groups)
                del pipe
                print(colorama.Fore.GREEN + 'Loading Transcribing Model...' + colorama.Fore.RESET)
                transcribe_pipe = init_transcribe_pipeline(args.whisper_model, args.device)
                #create progress bar
                print(colorama.Fore.GREEN + 'Transcribing...' + colorama.Fore.RESET)
                pb = tqdm(total=len(groups))
                for wav in range(0,wavs):
                    wav = str(wav)
                    res = transcribe_audio(os.path.join(os.getcwd(), wav+'.wav'),transcribe_pipe)
                    pb.update(1)
            if args.mode == 'segment and transcribe':
                print(colorama.Fore.GREEN + 'Loading Segment Model...' + colorama.Fore.RESET)
                pipe = load_pyannote_audio_model(args.segmentation_model, args.hf_token)
                segments = segment_audio_file(file_path, pipe, args.seg_onset, args.seg_offset, args.seg_min_duration, args.seg_min_duration_off)
                #milisecs = millisec(segments)
                print(colorama.Fore.GREEN + 'Segmenting...' + colorama.Fore.RESET)
                groups = group_segmentation(segments)
                wavs = segment_file_by_diargroup(file_path,wavs_path, groups)
                del pipe
                
                print(colorama.Fore.GREEN + 'Loading Transcribing Model...' + colorama.Fore.RESET)

                transcribe_pipe = init_transcribe_pipeline(args.whisper_model, 0 if args.device == 'cuda' else -1)
                print(colorama.Fore.GREEN + 'Transcribing...' + colorama.Fore.RESET)
                amount_to_train = int(len(groups) * (1 - args.valid_ratio))
                amount_to_valid = len(groups) - amount_to_train
                pb = tqdm(total=len(groups))
                for wav in range(0,amount_to_train):
                    wav = str(wav)
                    res = transcribe_audio(os.path.join(wavs_path, wav+'.wav'),transcribe_pipe)[1:]
                    #add to train file
                    add_to_textfile(train_file, 'wavs/'+wav+'.wav|'+res+'\n')
                    pb.update(1)
                for wav in range(amount_to_train,amount_to_train+amount_to_valid):
                    wav = str(wav)
                    res = transcribe_audio(os.path.join(wavs_path, wav+'.wav'),transcribe_pipe)[1:]
                    #add to valid file
                    add_to_textfile(valid_file, 'wavs/' + wav + '.wav|' + encode_utf8(res) + '\n')
                    pb.update(1)
    elif os.path.isdir(file_path):
        # Convert all files in the directory
        gidx = -1
        for filename in os.listdir(file_path):
            file_path = args.file_path
            file_ext = os.path.splitext(filename)[1].lower()
            if file_ext in ['.mp3', '.m4a', '.flac', '.ogg', '.wav']:
                if file_ext != '.wav':
                    print(colorama.Fore.GREEN + 'Converting to WAV...' + colorama.Fore.RESET)
                    file_path = convert_to_wav(os.path.join(file_path, filename))
                else:
                    file_path = os.path.join(file_path, filename)
                if args.mode == 'auto':
                    print(colorama.Fore.GREEN + 'Loading Diraization Model...' + colorama.Fore.RESET)
                    pipe = load_pyannote_audio_model(args.diaization_model, args.hf_token)
                    print(colorama.Fore.GREEN + 'Diarizing...' + colorama.Fore.RESET)
                    diarization = diarize_audio_file(file_path, pipe)
                    mil = millisec(diarization)
                    print(colorama.Fore.GREEN + 'Grouping Diarization...' + colorama.Fore.RESET)
                    dir_groups = group_diarization(diarization)
                    groups = group_diarization(diarization)
                    print(colorama.Fore.GREEN + 'Segmenting...' + colorama.Fore.RESET)
                    wavs = segment_file_by_diargroup(file_path, groups, gidx)
                    del pipe
                    print(colorama.Fore.GREEN + 'Loading Transcribing Model...' + colorama.Fore.RESET)
                    transcribe_pipe = init_transcribe_pipeline(args.whisper_model, 0 if args.device == 'cuda' else -1)
                    print(colorama.Fore.GREEN + 'Transcribing...' + colorama.Fore.RESET)
                    pb = tqdm(total=len(groups))
                    for wav in range(0,amount_to_train):
                        gidx += 1
                        wav = str(wav)
                        res = transcribe_audio(os.path.join(wavs_path, wav+'.wav'),transcribe_pipe)[1:]
                        #add to train file
                        add_to_textfile(train_file, 'wavs/'+wav+'.wav|'+res+'\n')
                        pb.update(1)
                    for wav in range(amount_to_train,amount_to_train+amount_to_valid):
                        gidx += 1
                        wav = str(wav)
                        res = transcribe_audio(os.path.join(wavs_path, wav+'.wav'),transcribe_pipe)[1:]
                        #add to valid file
                        add_to_textfile(valid_file, 'wavs/'+wav+'.wav|'+res+'\n')
                        pb.update(1)
                if args.mode == 'segment and transcribe':
                    print(colorama.Fore.GREEN + 'Loading Segment Model...' + colorama.Fore.RESET)
                    pipe = load_pyannote_audio_model(args.segmentation_model, args.hf_token)
                    segments = segment_audio_file(file_path, pipe, args.seg_onset, args.seg_offset, args.seg_min_duration, args.seg_min_duration_off)
                    #milisecs = millisec(segments)
                    print(colorama.Fore.GREEN + 'Segmenting...' + colorama.Fore.RESET)
                    groups = group_segmentation(segments)
                    wavs = segment_file_by_diargroup(file_path,wavs_path, groups, gidx)
                    del pipe
                    
                    transcribe_pipe = init_transcribe_pipeline(args.whisper_model, 0 if args.device == 'cuda' else -1)
                    print(colorama.Fore.GREEN + 'Loading Transcribing Model...' + colorama.Fore.RESET)
                    amount_to_train = int(len(groups) * (1 - args.valid_ratio))
                    amount_to_valid = len(groups) - amount_to_train
                    print(colorama.Fore.GREEN + 'Transcribing...' + colorama.Fore.RESET)
                    pb = tqdm(total=len(groups))
                    
                    for wav in range(0,amount_to_train):
                        gidx += 1
                        wav = str(wav)
                        res = transcribe_audio(os.path.join(wavs_path, str(gidx)+'.wav'),transcribe_pipe)[1:]
                        #add to train file
                        add_to_textfile(train_file, 'wavs/'+str(gidx)+'.wav|'+res+'\n')
                        pb.update(1)
                    for wav in range(amount_to_train,amount_to_train+amount_to_valid):
                        gidx += 1
                        wav = str(wav)
                        res = transcribe_audio(os.path.join(wavs_path, str(gidx)+'.wav'),transcribe_pipe)[1:]
                        #add to valid file
                        add_to_textfile(valid_file, 'wavs/'+str(gidx)+'.wav|'+res+'\n')
                        pb.update(1)
                    
        
    else:
        print(f'Error: {file_path} is not a file or directory.')
    print(colorama.Fore.GREEN + ' Done!' + colorama.Fore.RESET)
    print('')
