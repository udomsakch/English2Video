import os
import sys
from gtts import gTTS
from pydub import AudioSegment

def create_srt(sentences_en, sentences_full, timestamps, srt_file):
    with open(srt_file, "w", encoding="utf-8") as f:
        for i, (start, end) in enumerate(timestamps, start=1):
            # ฟังก์ชันแปลงเวลาเป็น SRT
            def format_time(ms):
                h = ms // (3600 * 1000)
                m = (ms % (3600 * 1000)) // (60 * 1000)
                s = (ms % (60 * 1000)) // 1000
                ms2 = ms % 1000
                return f"{h:02}:{m:02}:{s:02},{ms2:03}"

            f.write(f"{i}\n")
            f.write(f"{format_time(start)} --> {format_time(end)}\n")
            f.write(sentences_full[i-1] + "\n\n")   # Subtitle = อังกฤษ + แปลไทย


def main():
    if len(sys.argv) < 2:
        print("Usage: python myEnglish2Audio.py BusinessTrip.txt")
        sys.exit(1)

    text_file = sys.argv[1]
    base_name = os.path.splitext(os.path.basename(text_file))[0]   # เช่น BusinessTrip
    out_dir = base_name

    # สร้างโฟลเดอร์
    os.makedirs(out_dir, exist_ok=True)

    sentences_en = []    # เก็บเฉพาะอังกฤษ (สำหรับเสียง)
    sentences_full = []  # เก็บ อังกฤษ + ไทย (สำหรับ SRT)

    # อ่านไฟล์ข้อความ
    with open(text_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if ":" in line:
                eng, thai = line.split(":", 1)
                eng, thai = eng.strip(), thai.strip()
                sentences_en.append(eng)
                sentences_full.append(f"{eng}\n{thai}")
            else:
                # ถ้าไม่มี ":" ให้ถือว่าเป็นอังกฤษล้วน
                sentences_en.append(line)
                sentences_full.append(line)

    audio_files = []
    timestamps = []
    current_time = 0

    # สร้างไฟล์เสียง
    for idx, sentence in enumerate(sentences_en, start=1):
        tts = gTTS(sentence, lang="en")
        mp3_path = os.path.join(out_dir, f"{base_name}_{idx}.mp3")
        tts.save(mp3_path)
        audio_files.append(mp3_path)

        # โหลดไฟล์เสียงเพื่อหาความยาว
        audio = AudioSegment.from_mp3(mp3_path)
        start_time = current_time
        end_time = current_time + len(audio)
        timestamps.append((start_time, end_time))
        current_time = end_time + 5000  # เว้น 5 วินาที

    # ปรับ end_time ให้ subtitle คงค้างจนถึงประโยคถัดไป
    for i in range(len(timestamps) - 1):
        start, _ = timestamps[i]
        next_start, _ = timestamps[i + 1]
        timestamps[i] = (start, next_start)

    # ประโยคสุดท้ายจบที่เวลารวม
    total_duration = current_time
    last_start, _ = timestamps[-1]
    timestamps[-1] = (last_start, total_duration)

    # รวมไฟล์เสียงทั้งหมด
    combined = AudioSegment.empty()
    for file in audio_files:
        combined += AudioSegment.from_mp3(file) + AudioSegment.silent(duration=5000)

    final_mp3 = os.path.join(out_dir, f"{base_name}.mp3")
    combined.export(final_mp3, format="mp3")

    # สร้างไฟล์ SRT
    srt_file = os.path.join(out_dir, f"{base_name}.srt")
    create_srt(sentences_en, sentences_full, timestamps, srt_file)

    print(f"✅ สร้างไฟล์เรียบร้อยในโฟลเดอร์: {out_dir}")
    print(f"- {final_mp3}")
    print(f"- {srt_file}")


if __name__ == "__main__":
    main()
