
import speech_recognition as sr
import subprocess
from ctypes import *
from contextlib import contextmanager
import os
import sys

ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)

# to hide stderr caused by pyaudio
def py_error_handler(filename, line, function, err, fmt):
    pass

c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)

# to hide stderr caused by pyaudio
@contextmanager
def noalsaerr():
    asound = cdll.LoadLibrary('libasound.so')
    asound.snd_lib_error_set_handler(c_error_handler)
    yield
    asound.snd_lib_error_set_handler(None)

# to hide stderr caused by pyaudio
@contextmanager
def suppress_stderr():
    with open(os.devnull, 'w') as devnull:
        old_stderr = sys.stderr
        sys.stderr = devnull
        try:
            yield
        finally:
            sys.stderr = old_stderr

#obtain audio from the microphone
r=sr.Recognizer() 

def check_start():
    with suppress_stderr(), noalsaerr():
        with sr.Microphone() as source:
            print("Please wait. Calibrating microphone...") 
            #listen for 1 seconds and create the ambient noise energy level 
            r.adjust_for_ambient_noise(source, duration=1) 
            print('Say "Start" to start!')
            audio=r.listen(source)
            try:
                text = r.recognize_google(audio)
                text = text.lower()
                if 'start' in text:
                    print(f'You say "{text}"!')
                    return True
                else:
                    return False
            except:
                print("Failed to check start.")

def choose_song():
    with suppress_stderr(), noalsaerr():
        with sr.Microphone() as source:
            print("Please wait. Calibrating microphone...") 
            #listen for 1 seconds and create the ambient noise energy level 
            r.adjust_for_ambient_noise(source, duration=1) 
            print('Please choose a song (say "I want number 1/2/3"):')
            audio=r.listen(source)

            # recognize speech using Google Speech Recognition 
            try:
                text = r.recognize_google(audio)
                text = text.lower()
                if 'one' in text:
                    print(f'You say "{text}"!')
                    return 1
                elif 'two' in text:
                    print(f'You say "{text}"!')
                    return 2
                elif 'three' in text:
                    print(f'You say "{text}"!')
                    return 3
                else:
                    print(f'You say "{text}", please try again.')
                    return -1
            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio")
                return -2
            except sr.RequestError as e:
                print("No response from Google Speech Recognition service: {0}".format(e))
                return -3

def main():
    start = False

    while True:
        try:
            if start:
                song_num = choose_song()
                if song_num > 0: # choose song successfully
                    subprocess.run(f"mpg123 song{song_num}.mp3", shell=True) # blocking call
                    # if used in main function, replace the above line as asynchronous
                    # subprocess.Popen(["mpg123", f"song{song_num}.mp3"]) # non-blocking
                    # 麥克風和音響要同時用的話，要一起插在音效介面(卡)上
            else:
                start = check_start()
        except KeyboardInterrupt:
            print("Receiving Ctrl+C, terminating...")
            break


if __name__ == "__main__":
    main()