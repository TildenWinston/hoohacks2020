import os, io
from google.cloud import vision
import pandas as pd

os.environ['GOOGLE_APPLICATION_CREDENTIALS']=r'google-suite-token.json'
client = vision.ImageAnnotatorClient()

image = vision.types.image('gs://zoom-education-suite-videos/happy.jpg')
reponse = client.label_detection(image=image) 
labels = reponse.label_annotations

df = pd.DataFrame(columns=['description', 'score', 'topicality'])
for i in labels:
    df = df.append(
        dict(
            description=i.description,
            score=i.score,
            topicality=i.topicality
        ), ignore_index=True
    )
print(df)