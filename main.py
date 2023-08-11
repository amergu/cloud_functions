from google.cloud import firestore
import cv2

client = firestore.Client()


def get_video_details(path=None):
    if path is None:
        return 0, 0

    try:
        data = cv2.VideoCapture(path)
    except Exception as e:
        print(f"Error in initialising cv2 with the video path : {e}")
        return 0, 0, 0

    # count the number of frames
    frames = data.get(cv2.CAP_PROP_FRAME_COUNT)
    fps = data.get(cv2.CAP_PROP_FPS)

    if int(frames) == 0 or int(fps) == 0:
        return 0, 0, 0

    # calculate duration of the video
    seconds = round(frames / fps)

    return seconds, frames, fps


# Converts strings added to /messages/{pushId}/original to uppercase
def analyse_video(data, context):
    path_parts = context.resource.split("/documents/")[1].split("/")
    collection_path = path_parts[0]
    document_path = "/".join(path_parts[1:])

    task_doc = client.collection(collection_path).document(document_path)

    try:
        metadata = data["value"]["fields"]["metadata"]["mapValue"]
        if len(metadata.keys()) != 0:
            return
    except Exception as e:
        print(f"Error in reading task metadata: {e}")

    try:
        media_url = data["value"]["fields"]["mediaURL"]["stringValue"]
    except Exception as e:
        print(f"Error in reading mediaURL : {e}")
        print("Analysis aborted")
        return

    if not media_url:
        print("Media URL is empty, analysis is aborted")
        return

    seconds, frames, fps = get_video_details(media_url)
    print(f"Video analysed: seconds: {seconds}, frames: {frames}, fps: {fps}")

    try:
        metadata = {
            "seconds": seconds,
            "frames": frames,
            "fps": fps
        }
        task_doc.update({"metadata": metadata})
        print(f"Document successfully updated with metadata : {metadata}")
    except Exception as e:
        print(f"Error in updating the document with the metadata: {e}")
