import gradio as gr
import openai
import config
import subprocess
import win32com.client as wincl
import soundfile as sf

openai.api_key = config.OPENAI_API_KEY

messages = [{"role": "system",
             "content": 'You are a personal assistant. Respond to all input in 25 words or less.'}]

speak = wincl.Dispatch("SAPI.SpVoice")
speak.Speak("I hear you.")
# subprocess.call(["speak", "I hear you. Please go on."])
# subprocess.call(["espeak-ng", "-v", "el", "Σε ακούω. Παρακαλώ συνεχίστε."])


def transcribe(audio):
    global messages

    sf.write("temp.wav", audio+'.wav', 44100)
    with open("temp.wav", "rb") as f:
        data = f.read()

    transcript = openai.Audio.transcribe("whisper-1", data)

    messages.append({"role": "user", "content": transcript["text"]})

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=messages)

    system_message = response["choices"][0]["message"]
    messages.append(system_message)

    speak.Speak(system_message['content'])
    # subprocess.call(["espeak-ng", "-v", "el", system_message['content']])

    chat_transcript = ""
    for message in messages:
        if message['role'] != 'system':
            chat_transcript += message['role'] + \
                ": " + message['content'] + "\n\n"

    return chat_transcript


ui = gr.Interface(fn=transcribe, inputs=gr.Audio(
    source="microphone", type="filepath", ), outputs="text").launch()
ui.launch()

# def reverse_audio(audio):
#     sr, data = audio
#     reversed_audio = (sr, np.flipud(data))
#     return reversed_audio


# mic = gr.Audio(source="microphone", type="numpy", label="Speak here...")
# gr.Interface(reverse_audio, mic, "audio").launch()
