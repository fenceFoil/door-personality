import boto3
from botocore.exceptions import BotoCoreError, ClientError
from contextlib import closing
import os
import sys
from tempfile import gettempdir

polly = None

def speak(text, voice, outputPath):
    # Init polly if necessary
    global polly
    if polly == None:
        polly = boto3.Session(region_name="us-west-2").client('polly')

    # Make request
    try:
        response = polly.synthesize_speech(Text=text, OutputFormat="ogg_vorbis", VoiceId="Joanna" if voice == None else voice, Engine="neural")
    except (BotoCoreError, ClientError) as error:
        # The service returned an error, exit gracefully
        print(error)
        return False

    # Access the audio stream from the response
    if "AudioStream" in response:
        # Note: Closing the stream is important because the service throttles on the
        # number of parallel connections. Here we are using contextlib.closing to
        # ensure the close method of the stream object will be called automatically
        # at the end of the with statement's scope.
        with closing(response["AudioStream"]) as stream:
            try:
                # Open a file for writing the output as a binary stream
                with open(outputPath, "wb") as file:
                    file.write(stream.read())
                print (outputPath)
            except IOError as error:
                # Could not write to file, exit gracefully
                print(error)
                return False
    else:
        # The response didn't contain audio data, exit gracefully
        print("Could not stream audio from polly")
        return False

    return True