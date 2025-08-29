from fastapi import UploadFile
import assemblyai as aai
from assemblyai.streaming.v3 import (
    BeginEvent,
    StreamingClient,
    StreamingClientOptions,
    StreamingError,
    StreamingEvents,
    StreamingParameters,
    StreamingSessionParameters,
    TerminationEvent,
    TurnEvent,
)



def on_begin(self, event: BeginEvent):
    print(f"Session started: {event.id}")

def on_turn(self, event: TurnEvent):
    # Print transcripts as they arrive
    print(f"{event.transcript} (end_of_turn={event.end_of_turn})")
    if event.end_of_turn and not event.turn_is_formatted:
        self.set_params(StreamingSessionParameters(format_turns=True))
    
def on_terminated(self, event: TerminationEvent):
    print(f"Session terminated: {event.audio_duration_seconds} seconds processed")

def on_error(self, error: StreamingError):
    print(f"Error: {error}")
    
    
class AssemblyAIStreamingClient:
    def __init__(self, assembly_api_key, sample_rate=16000):
        self.client = StreamingClient(
            StreamingClientOptions(
                api_key=assembly_api_key,
                api_host="streaming.assemblyai.com"
            )
        )
        self.client.on(StreamingEvents.Begin, on_begin)
        self.client.on(StreamingEvents.Turn, on_turn)
        self.client.on(StreamingEvents.Termination, on_terminated)
        self.client.on(StreamingEvents.Error, on_error)
        self.client.connect(StreamingParameters(
            sample_rate=sample_rate, format_turns=False
        ))
    
    def stream(self, audio_chunk: bytes):
        self.client.stream(audio_chunk)

    def close(self):
        self.client.disconnect(terminate=True)    
    
    