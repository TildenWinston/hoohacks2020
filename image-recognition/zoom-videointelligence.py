import os
from google.cloud import videointelligence

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=r'zoom-token_2.json'

def zoom_analysis(video, frame_to_use=0):
    video_client = videointelligence.VideoIntelligenceServiceClient()
    features = [videointelligence.enums.Feature.LABEL_DETECTION]

    operation = video_client.annotate_video(
        video, features=features)
    print('\nProcessing video for label annotations:')

    result = operation.result(timeout=120)
    print('\nFinished processing.')

    frame_offsets = []

    # first result is retrieved because a single video was processed
    segment_labels = result.annotation_results[0].segment_label_annotations
    for i, segment_label in enumerate(segment_labels):
        for category_entity in segment_label.category_entities:
            # Take frames with people
            if(category_entity.description == 'person'):
                print('\tLabel category description: {}'.format(
                    category_entity.description))
                print(segment_label)
                frame = segment_label.frames[frame_to_use]
                time_offset = (frame.time_offset.seconds + 
                                frame.time_offset.nanos / 1e9)
                print('\tFirst frame time offset: {}s'.format(time_offset))
                print('\tFirst frame confidence: {}'.format(frame.confidence))
                print('\n')
                frame_offsets.append(time_offset)
    return sorted(set(frame_offsets))

frames = zoom_analysis('gs://zoom-suite/facial-expressions.mp4')
print(frames)