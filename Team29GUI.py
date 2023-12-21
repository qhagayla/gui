import PySimpleGUI as sg
import cv2
import os
from datetime import datetime, timedelta
import uuid

def get_video_duration(file_path):
    cap = cv2.VideoCapture(file_path)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frames // fps
    cap.release()
    return duration

def seconds_to_readable_time(seconds):
    return str(timedelta(seconds=seconds))

def main():
    cap = cv2.VideoCapture(0)  # Access the default camera
    recording = False
    out = None
    video_files = []
    paused = False
    start_time = None

    session_id = '1'  # Session ID set to '1'

    layout = [
        [sg.Text(f"Session ID: {session_id}")],
        [sg.Column([
            [sg.Text('Name:'), sg.InputText(key='-NAME-', size=(20, 1))],
            [sg.Text('Age:'), sg.InputText(key='-AGE-', size=(5, 1))],
            [sg.Image(filename='', key='-CAM-', size=(400, 300)), sg.Text('', key='-TIME-')],
            [sg.Button('Start', key='-START-', size=(10, 2)), sg.Button('Pause', key='-PAUSE-', size=(10, 2)), sg.Button('Stop', key='-STOP-', size=(10, 2))]
        ]),
        sg.VSeperator(),
        sg.Column([
            [sg.Listbox(values=[], size=(25, 20), key='-RECORDINGS-')],
            [sg.Button('Play', key='-PLAY-', size=(8, 1)), sg.Button('Delete', key='-DELETE-', size=(8, 1))],
            [sg.Text('', key='-REC-TIME-')]
        ])]
    ]

    window = sg.Window('Camera Recorder', layout)

    while True:
        event, values = window.read(timeout=20)

        if event == sg.WIN_CLOSED:
            break

        if recording and not paused:
            ret, frame = cap.read()
            if ret:
                imgbytes = cv2.imencode('.png', frame)[1].tobytes()
                window['-CAM-'].update(data=imgbytes)
                elapsed_time = datetime.now() - start_time if start_time else datetime.now()
                window['-TIME-'].update(value=str(elapsed_time).split(".")[0])
                out.write(frame)

        if event == '-START-' and not recording:
            recording = True
            start_time = datetime.now()
            name = values['-NAME-'] if values['-NAME-'] else 'Unknown'
            age = values['-AGE-'] if values['-AGE-'] else 'Unknown'
            title = f'{name}_Age{age}'
            out = cv2.VideoWriter(f'{title}.avi', cv2.VideoWriter_fourcc(*'XVID'), 20, (640, 480))
            window['-START-'].update(disabled=True, button_color=('white', 'green'))

        elif event == '-PAUSE-' and recording:
            paused = not paused
            if paused:
                window['-PAUSE-'].update('Unpause')
            else:
                window['-PAUSE-'].update('Pause')
                start_time = datetime.now() - (start_time - datetime.now())

        elif event == '-STOP-' and recording:
            recording = False
            paused = False
            out.release()
            video_files.append(f'{title}.avi')
            window['-RECORDINGS-'].update(values=video_files)
            window['-START-'].update(disabled=False, button_color=('white', 'blue'))

        elif event == '-PLAY-':
            selected_video = values['-RECORDINGS-']
            if selected_video:
                os.startfile(selected_video[0])

        elif event == '-DELETE-':
            selected_video = values['-RECORDINGS-']
            if selected_video:
                os.remove(selected_video[0])
                video_files.remove(selected_video[0])
                window['-RECORDINGS-'].update(values=video_files)
                window['-REC-TIME-'].update('')

        elif event == '-RECORDINGS-':
            selected_video = values['-RECORDINGS-']
            if selected_video:
                video_duration = get_video_duration(selected_video[0])
                readable_duration = seconds_to_readable_time(video_duration)
                start_time = os.path.getctime(selected_video[0])
                start_time = datetime.fromtimestamp(start_time)
                end_time = start_time + timedelta(seconds=video_duration)
                window['-REC-TIME-'].update(value=f"Start: {start_time}, End: {end_time}")

    window.close()
    if cap:
        cap.release()

if __name__ == '__main__':
    main()
