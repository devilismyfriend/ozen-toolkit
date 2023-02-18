# OZEN toolkit, AI powered audio dataset helper.
<a href='https://ko-fi.com/O4O5GU04F' target='_blank'><img height='36' style='border:0px;height:36px;' src='https://storage.ko-fi.com/cdn/kofi2.png?v=3' border='0' alt='Buy Me a Coffee at ko-fi.com' /></a>

OZEN is a small tool to help you process audio files to a Librispeech format.

Given a folder of files or a single audio file, it will extract the speech, transcribe using Whisper and save in the LS format (wavs in wavs folder, train and valid txts).

## INSTALLATION

```sh
Accept the license terms on https://huggingface.co/pyannote/segmentation 
Install Anaconda if you don't have it.
git clone https://github.com/devilismyfriend/ozen-toolkit
run Set Up Ozen.bat
```

## USAGE

Drag a folder or a file on the Drag_Here.bat to process it.

The first time you'll be prompted to provide an HuggingFace token, once you do a config file will be created where you can specifiy models to use, the validation/training data desired split and more.

Alternatively you can use ozen.py in cli.

