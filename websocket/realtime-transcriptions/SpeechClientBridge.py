import queue
from threading import Thread
from google.cloud import speech
from google.cloud.speech import types


class SpeechClientBridge:
    def __init__(self, streaming_config, on_response):
        print("Speech Client init")
        self._on_response = on_response
        self._queue = queue.Queue()
        self._ended = False

        client = speech.SpeechClient()
        responses = client.streaming_recognize(
            streaming_config, 
            self.get_requests()
        )
        self.process_responses(responses)

    def terminate(self):
        print("Speech Client Terminate")
        self._ended = True

    def add_request(self, buffer):
        print("Speech Client Add Request")
        self._queue.put(types.StreamingRecognizeRequest(audio_content=bytes(buffer)))

    def get_requests(self):
        print("Speech Client Get Request")
        while not self._ended:
            yield self._queue.get()

    def process_responses(self, responses):
        print("Speech Client process")
        thread = Thread(target=self.process_responses_loop, args=[responses])
        thread.start()

    def process_responses_loop(self, responses):
        print("Speech Client process loop")
        for response in responses:
            self._on_response(response)

            if self._ended:
                break
