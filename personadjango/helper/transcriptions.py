from moviepy.editor import VideoFileClip
import logging

def save_transcription_to_file(input_text, target_file_path):
    """
    Save the provided transcription text to a specified file.

    Parameters:
    input_text (str): The transcription text to be saved.
    target_file_path (str): The path to the file where the text will be saved.

    Raises:
    Exception: If there is an error while writing to the file.
    """
    try:
        # Open the target file in write mode
        with open(target_file_path, 'w') as file:
            file.write(input_text)
    except Exception as e:
        logging.error(f'Error saving transcription: {e}')

def convert_video_to_audio(source_file_path, target_file_path):
    """
    Convert a video file to an audio file and save it.

    Parameters:
    source_file_path (str): The path to the source video file.
    target_file_path (str): The path to the target audio file.

    Raises:
    Exception: If there is an error while converting or saving the audio file.
    """
    try:
        # Load the video file
        video = VideoFileClip(source_file_path)
        # Extract the audio from the video
        audio = video.audio
        # Save the extracted audio to the target file
        audio.write_audiofile(target_file_path, codec='libmp3lame')
        logging.info(f'Audio extracted and saved to {target_file_path}')
    except Exception as e:
        logging.error(f'Error converting video to audio: {e}')
        raise e