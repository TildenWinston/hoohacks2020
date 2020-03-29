import os
from google.cloud import videointelligence
# from google.cloud import vision
# from vision import types

os.environ['GOOGLE_APPLICATION_CREDENTIALS']=r'google-suite-token.json'

def zoom_analysis(video, frame_to_use):
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
                frame = segment_label[frame_to_use]
                time_offset = (frame.time_offset.seconds + 
                                frame.time_offset.nanos / 1e9)
                print('\tFirst frame time offset: {}s'.format(time_offset))
                print('\tFirst frame confidence: {}'.format(frame.confidence))
                print('\n')
                frame_offsets.append(time_offset)
    return sorted(set(frame_offsets))

frames = zoom_analysis('gs://zoom-education-suite-videos/emotions-test.mp4', 0)
print(frames)