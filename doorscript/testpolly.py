import boto3
from botocore.exceptions import BotoCoreError, ClientError
from contextlib import closing
import os
import sys
from tempfile import gettempdir

polly = boto3.Session(region_name="us-west-2").client('polly')

try:
    response = polly.synthesize_speech(Text=" Honestly I get a lot of pretty good on a weekly basis with this from me personally!", OutputFormat="ogg_vorbis", VoiceId="Joanna", Engine="neural")
except (BotoCoreError, ClientError) as error:
    # The service returned an error, exit gracefully
    print(error)
    sys.exit(-1)

# Access the audio stream from the response
if "AudioStream" in response:
    # Note: Closing the stream is important because the service throttles on the
    # number of parallel connections. Here we are using contextlib.closing to
    # ensure the close method of the stream object will be called automatically
    # at the end of the with statement's scope.
    with closing(response["AudioStream"]) as stream:
        output = os.path.join(gettempdir(), "speech.ogg")

        try:
            # Open a file for writing the output as a binary stream
            with open(output, "wb") as file:
                file.write(stream.read())
            print (output)
        except IOError as error:
            # Could not write to file, exit gracefully
            print(error)
            sys.exit(-1)

else:
    # The response didn't contain audio data, exit gracefully
    print("Could not stream audio")
    sys.exit(-1)