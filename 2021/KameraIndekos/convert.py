from pydub import AudioSegment

filename = 'AwACAgUAAxkBAAICSGC18nD_INVmxa5VpGtek7zES7LRAAJCAgACr1yxVRqGo82E1nnqHwQ.ogg'
audio = AudioSegment.from_file(
    filename, 'ogg')
audio.export(filename, format='ogg')
