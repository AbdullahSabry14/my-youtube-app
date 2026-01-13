# from google import genai

# c = genai.Client(api_key="AIzaSyAZBWQyV70RdE2FlPlwIRYbLkjCBdi2m40")

# re = c.models.generate_content(
#     model="gemini-3-flash-preview",
#     contents="انا ابو الصبري مبرمج احفظني يا عسل"
# )
# print(re.text)



import sys
import io
import os

if sys.stdout is None or sys.stderr is None:
    # بدال devnull اللي بيخنق الـ Pipes، بنستخدم StringIO
    # هذا بيخلي MoviePy تفتكر إن في Terminal شغال وما بتعمل Crash
    sys.stdout = io.StringIO()
    sys.stderr = io.StringIO()
else:
    try:
        if hasattr(sys.stdout, 'buffer'):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except:
        pass
    
import pyi_splash
import requests
from PIL import Image
from tqdm import tqdm
from urllib.parse import quote_plus
import time 
from requests.exceptions import ReadTimeout, ConnectionError, RequestException
import re
import glob
import math
from moviepy.editor import *
import numpy as np
import customtkinter as ctk
import tkinter as tk
from plyer import notification
import threading
from elevenlabs.client import ElevenLabs
from elevenlabs import save
from google import genai

pyi_splash.close()

ctk.set_appearance_mode("Dark")

lolo = ctk.CTk()
lolo.title("صانع الفيديوهات")
lolo.geometry("410x180")
lolo.resizable(False, False)

key1 = "sk_663aea92de9cc1d28fbf892accf52374f634a5dde791d2c0"
key2 = "AIzaSyAZBWQyV70RdE2FlPlwIRYbLkjCBdi2m40"

FINAL_RESOLUTION = (720, 1280)
ZOOM_FACTOR = 1.25
CLIP_DURATION = 2.5
elevenlabs = ElevenLabs(api_key=key1)

FONT_PATH = "Cairo-Black.ttf"

def cleanup_directories():

    audio_files = glob.glob(os.path.join("Audio", "*.mp3"))
    for f in audio_files:
        try:
            time.sleep(0.1) 
            os.remove(f)
        except OSError as e:
            print(f"❌ خطأ في حذف ملف الصوت {f}: {e}")

    image_files = glob.glob(os.path.join("Images", "*.jpg"))
    for f in image_files:
        try:
            time.sleep(0.1) 
            os.remove(f)
        except OSError as e:
            print(f"❌ خطأ في حذف ملف الصورة {f}: {e}")

    os.makedirs("Audio", exist_ok=True)
    os.makedirs("Images", exist_ok=True)

class script_writing :
    def __init__(self, title):
        self.titlei = title
        self.script_content = None

    def script(self) :
        popo = f"""أنت "كاتب سكريبت فيديو قصير (Shorts) محترف"، متخصص في إنتاج محتوى عربي مؤثر وسريع الإيقاع، ملتزم تماماً بالقيود الفنية الصارمة التالية:
**المهمة:** صياغة سكريبت خام وموصول بالكامل عن الموضوع: [{self.titlei}].
**القيود الصارمة (الإلزامية):**
1. **العدد:** يجب أن يكون الناتج 50 كلمة بالضبط. يجب أن تتأكد من عدّ الكلمات بدقة قبل الإخراج.
2. **الأسلوب:** لا تستخدم أي علامات ترقيم داخلية (مثل الفاصلة، النقطة، الفاصلة المنقوطة). يجب أن يكون النص سلسلة متصلة وخاماً تماماً.
3. **الخطاف:** يجب أن يبدأ النص بخطاف قوي ومثير لا يتجاوز 10 كلمات لجذب المشاهد فوراً.
4. **الهيكل:** صلب الموضوع يجب أن يكون سريعاً وقوياً ومُركّزاً وينتهي دون خاتمة تقليدية.
5. للمرة المليون تأكد كثير انه السكريبت صغير ليكون حوالي نصف دقيقة ويأتي 50 كلمة بالضبط لا أقل ولا أكثر حتى لا يخرّب الفيديو ركّز وأعد قراءة السكريبت ألف مرة قبل النتيجة.
6. لا تكتب جمل قصيرة جداً مكونة من كلمتين أو ثلاث فهذا يزعج تقسيم الفيديو.
7. ليكون نصف دقيقة ثلاثين ثانية بالضبط وإلا يخرّب الفيديو كله.
اجعل النص من فقرة واحدة متصلة لا تفصل بين الجمل بأسطر جديدة ولا بفواصل كبيرة
ويجب أن يكون أصلي وحقيقي منك بأسلوب واضح وسلس ومترابط بحيث تنتقل الفكرة بانسياب طبيعي
استخدم لغة عربية بسيطة وجمل قصيرة تشبه أسلوب الفيديوهات القصيرة على يوتيوب
لا تضع مقدمات أو نهايات مثل مرحبًا أو في الختام
لا تنسى الفيديو لازم يكون بالزبط نصف دقيقة أي بالزبط 30 ثانية ولازم كل جملة منطقية اقدر اسوي منها صورة مناسبة للكلام
الناتج المطلوب: ابدأ بالنص الـ 50 كلمة مباشرة فقط 50 كلمة لا أقل ولا أزيد قدر الإمكان بشرط أن يكون السكريبت 30 ثانية بالزبط"""

        try:
            c = genai.Client(api_key=key2)
            re = c.models.generate_content(
                model="gemini-3-flash-preview",
                contents=popo
            )
            summary_content = re.text
            self.script_content = summary_content
            word_count = len(summary_content.split())
            print("--------------------------------------------------")
            print(f"✅ تم توليد السكريبت بنجاح (موضوع: {self.titlei})")
            print(f"✅ عدد الكلمات في النص الناتج: {word_count}")
            print("--------------------------------------------------")
            print(f"السكريبت: {summary_content}\n")

            return summary_content

        except Exception as e:
            raise Exception(f"فشل الاتصال أو التوليد عبر جيماين: {e}")

class script_division(script_writing) :
    def __init__(self, script_obj):
        self.script_content = script_obj.script_content
        self.unvocalized_script = None
        self.vecalized_script = None

    def divisio1(self) :
        popo = f"""مهمتك هي تقسيم السكريبت الخام والموصول التالي إلى جمل كاملة وطبيعية.
**القيود الصارمة (الإلزامية):**
1. استخدم علامات الترقيم المناسبة (مثل النقطة أو الفاصلة المنقوطة أو علامة الاستفهام) لإنهاء كل جملة.
2. الإخراج يجب أن يكون **النص المقسم فقط كنص خام موصول واحد**.
3. **ممنوع بتاتاً** استخدام الترقيم المتسلسل (1. 2. 3...) أو أي مقدمات أو شروحات أو ملاحظات أو أي نص إضافي قبل أو بعد الجمل المقسمة.
4. لا تقم بتشكيل أي كلمة.
5. احذر واقول لا تنسى أن تقسمه تقسيمات منطقية وشوف الي قبل الجمل وما بعدها لتعرف اين تقص 
6. الرجاء أيضا لا تطول عدد الكلمات للمقطع الواحد كثيرا وخليهن حوالي 10 مقاطع نصية 10 او 9 11 زي هيك يعني لا تطول نص المقطع النصي ولا تقلل ولا تزيد مقاطع نصية يعني حوالي 10 او 8
7. الرجاء عدم تكثير عدد المقاطع النصية للسكريبت الواحد الرجاء لا يتجاوزن عن 10 مقاطع أكثر اشي فقط وطبعا المقطع النصي الواحد لا تقصره كثير ولا يكن عدة كلمات مش يعني يكون في المقطع الواحد كلمتين او ثلاثة لا يزبط ولا حتى كلمات كثير في المنتصف .وقسم لوينتا يوقف ووينتا يتحرك
السكريبت الخام: [{self.script_content}]."""
        c = genai.Client(api_key=key2)
        r = c.models.generate_content(
            model="gemini-3-flash-preview",
            contents=popo
        )
        summary_content = r.text
        clean = summary_content.replace(".", "#").replace("،", "#").replace("؛", "#").replace("؟", "#").replace("\n", '#').replace("  ", " ")
        while "##" in clean:
            clean = clean.replace("##", "#")
        clean = re.sub(r'\s*\d+\.\s*', '', clean)
        telist = [text.strip() for text in clean.split("#") if text.strip()]
        final_list = []
        current_chunk = ""
        for item in telist:
            if not current_chunk:
                current_chunk = item
            else:
                if len(current_chunk.split()) < 5:
                    current_chunk += " " + item
                else:
                    final_list.append(current_chunk)
                    current_chunk = item
        if current_chunk:
            final_list.append(current_chunk)

        print("قائمة المقاطع النهائية بعد الدمج:", final_list)
        self.unvocalized_script = final_list
        return final_list

    def division2(self) :
        if self.unvocalized_script is None :
            self.divisio1()

        raw_text_to_vocalize = " | ".join(self.unvocalized_script)

        print("\n...جاري تشكيل جميع المقاطع في طلب واحد ومُسرَّع:")

        popo_segment = f"""أنت **خبير تشكيل لغوي عربي مطلق ومُدقق صوتي للمحركات اللفظية**، ومهمتك الوحيدة والحصرية هي **التشكيل الإلزامي والدقيق لغوياً وصوتياً بنسبة 100%** للعبارات العربية الفصيحة التالية بالكامل.
        **الأوامر الصارمة المطلقة (ممنوع المخالفة بتاتاً - هذا النص سيتحول إلى صوت):**
        1. **التشكيل التام الإجباري (صوتي):** يجب تشكيل **كل حرف متحرك** في النص باستخدام إحدى الحركات الأربع فقط: **الفتحة، الضمة، الكسرة، أو الشدة (مع الحركة التابعة)**. التشكيل يجب أن يكون تاماً 100% لضمان جودة النطق وتحويله إلى كلام. إذا كان الحرف غير ساكن، يجب أن يحمل حركة.
        2. **الإخراج الخام فقط:** الناتج هو **النص المُشكَّل بالكامل والخام**، دون أي كلمات إضافية، مقدمات، شروحات، أو ترقيم متسلسل.
        3. **الحفاظ على الفاصل:** يجب عليك **إلزامياً** الاحتفاظ بفاصل **' | '** بين كل جملة مشكلة لتفصل بينها. لا تغير الفاصل أو تحذفه.
        4. **التدقيق الصوتي:** تأكد أن التشكيل يضمن النطق الصحيح للكلمات عند قراءتها بواسطة محرك صوتي (TTS).
        5. شكَل بمنطق حسب الجملة وموقعها بمنطق وشكل ب الضمة والفتحة والكسرة فقط لضمان تحويله لصوت ووينتا يوقف ووينتا يتحرك
         النص الأصلي (بين الأقواس المعقوفة): [{raw_text_to_vocalize}]"""
        try:
            c = genai.Client(api_key=key2)
            re = c.models.generate_content(
                model="gemini-3-flash-preview",
                contents=popo_segment
            )
            summary_content = re.text

            final_vocalized_text = summary_content.replace(" | ", "#").replace("|", "#")

            while "##" in final_vocalized_text:
                final_vocalized_text = final_vocalized_text.replace("##", "#")

            self.vecalized_script = final_vocalized_text
            print("\nالسكريبت المُشكَّل المُقسَّم بـ #: " + final_vocalized_text + "\n")
            return final_vocalized_text

        except Exception as e:
            raise Exception(f"فشل حرج في مرحلة التشكيل الجماعي عبر Ollama: {e}")

class audio_clips :
    def __init__(self, text):
        self.text = text

    def clip(self) :
        audio_paths = []

        vocalized_segments = [s.strip() for s in self.text.split("#") if s.strip()]
        print(f"💡 عدد المقاطع الصوتية المكتشفة: {len(vocalized_segments)}")

        for key, i in enumerate(vocalized_segments) :

            clean_text = i
            print(f"جاري توليد صوت للمقطع {key+1}: {clean_text[:50]}...")
            try:
                audio = elevenlabs.text_to_speech.convert(
                    text=clean_text,
                    voice_id="P1bg08DkjqiVEzOn76yG",
                    model_id="eleven_multilingual_v2",
                )
                output_path = f"Audio\\audio{key+1}.mp3"
                save(audio, output_path)
                audio_paths.append(output_path)
            except Exception as e:
                print(f"❌ فشل في توليد الصوت للمقطع رقم {key+1}: {e}")
                
        return audio_paths

class pictures :
    def __init__(self, script_texts):
        self.script_texts = script_texts
        self.output_dir = "Images"
        self.image_size_params = "width=720&height=1280&nologo=true"

    def generate_image_for_prompt(self, prompt_text, part):
        popo = f"""Translate to a short English prompt: [{prompt_text}]. 
                Keywords: Cinematic, Photorealistic, No text.
                Whatever the case, do not write on the image in any language, and ensure the image makes sense in relation to the sentence. Be careful to use logic and provide a clear explanation to the image creator to ensure it is appropriate."""
        c = genai.Client(api_key=key2)
        re = c.models.generate_content(
            model="gemini-3-flash-preview",
            contents=popo
        )
        summary_content = re.text
        print(f"البرومبت الإنجليزي للمقطع {part+1}: {summary_content}\n")

        encoded = quote_plus(summary_content)
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        url = f"https://image.pollinations.ai/prompt/{encoded}?{self.image_size_params}&seed={int(time.time())}"
        MAX_RETRIES = 5

        for attempt in range(MAX_RETRIES):
            try:
                resp = requests.get(url, headers=headers, timeout=60)
                if resp is not None and resp.status_code == 200:
                    final_path = os.path.join(self.output_dir, f"part{part+1}.jpg")
                    with open(final_path, 'wb') as f:
                        f.write(resp.content)
                    print(f"✅ تم تحميل الصورة رقم {part+1} بنجاح في المحاولة رقم {attempt + 1}.")
                    return final_path
                else:
                    print(f"⚠️ سيرفر الصور مشغول.. محاولة {attempt + 1}")
            except Exception as e:
                print(f"⚠️ محاولة {attempt + 1} فشلت للمقطع {part+1}: {e}")
            time.sleep(3)
        return None

    def picture(self) :
        generated_paths = []
        for part, prompt in enumerate(tqdm(self.script_texts, desc="Generating images")):
            if prompt:
                path = self.generate_image_for_prompt(prompt, part)
                if path:
                    generated_paths.append(path)
                # else :
                    # raise Exception(f"❌ توقف! فشل تحميل الصورة رقم {part+1}. تأكد من الإنترنت أو جرب لاحقاً.")
        return generated_paths
# class pictures :
#     def __init__(self, script_texts):
#         self.script_texts = script_texts
#         self.output_dir = "Images"
#         # &model=flux
#         self.image_size_params = "width=720&height=1280&nologo=true"

#     def generate_image_for_prompt(self, prompt_text, part):
#         time.sleep(part * 5)
#         try:
#             popo = f"""Translate this Arabic sentence into a short, powerful English image prompt.
#             Output ONLY the English text.
#             Strict Rules:
#             1. No intro/outro.
#             2. No text, no captions, no letters on image.
#             3. Essential Keywords only: Cinematic, 8k, Photorealistic, dramatic lighting, highly detailed, no text.
#             Sentence: [{prompt_text}]"""
#             c = genai.Client(api_key=key2)
#             re = c.models.generate_content(
#                 model="gemini-3-flash-preview",
#                 contents=popo
#             )
#             summary_content = re.text
#             print(f"البرومبت الإنجليزي للمقطع {part+1}: {summary_content}\n")

#             encoded = quote_plus(summary_content)
#             import random
#             rand_val = random.randint(1, 1000000)
#             url = f"https://image.pollinations.ai/prompt/{encoded}?{self.image_size_params}&seed={rand_val}&model=flux&cache={rand_val}"
#             MAX_RETRIES = 7

#             for attempt in range(MAX_RETRIES):
#                 try:
#                     resp = requests.get(url, timeout=60)
#                     if resp.status_code == 200 and len(resp.content) > 30000:
#                         final_path = os.path.join(self.output_dir, f"part{part+1}.jpg")
#                         with open(final_path, 'wb') as f:
#                             f.write(resp.content)
#                         print(f"✅ تم تحميل الصورة {part+1}")
#                         return final_path
#                     else:
#                         print(f"⚠️ السيرفر مشغول للمقطع {part+1}.. محاولة {attempt+1}")
#                         time.sleep(6)
#                 except Exception:
#                     time.sleep(6)
#                     print(f"⚠️ خطأ اتصال في المحاولة {attempt+1} للمقطع {part+1}")
#                     continue
#             return None
#         except Exception as e:
#             print(f"❌ خطأ فني في المقطع {part+1}: {e}")
#             return None
#     def picture(self) :
#         import concurrent.futures
#         generated_paths = [None] * len(self.script_texts)
#         def do(prompt_idx_tuple) :
#             part, prompt = prompt_idx_tuple
#             return self.generate_image_for_prompt(prompt, part), part
#         print(f"🚀 جاري طلب {len(self.script_texts)} صور في نفس الوقت...")
#         with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
#             tasks = [(i, p) for i, p in enumerate(self.script_texts) if p]
#             future_to_part = {executor.submit(do, task): task[0] for task in tasks}
#             for future in concurrent.futures.as_completed(future_to_part):
#                 path,part_idx = future.result()
#                 if path:
#                     generated_paths[part_idx] = path
#                 else :
#                     print(f"❌ فشل تحميل الصورة {part_idx+1} بعد كل المحاولات.")
#         return [p for p in generated_paths if p is not None]

class final_video() :
    def __init__(self, pictures_paths, script_processor, audio_paths, titel):
        self.script_processor = script_processor
        self.pictures = pictures_paths
        self.unvocalized_texts = self.script_processor.unvocalized_script
        self.audio_paths = audio_paths
        self.titel = titel

    def create_image_clip_with_zoom(self, picture_path, duration, index):
        global FINAL_RESOLUTION, ZOOM_FACTOR
        target_w, target_h = FINAL_RESOLUTION

        try:
            base_image = Image.open(picture_path)
        except Exception as e:
            return None
        w_orig, h_orig = base_image.size
        final_ratio = max(target_w / w_orig, target_h / h_orig)

        if index % 2 == 0:
            start_factor = 1.0
            end_factor = ZOOM_FACTOR
        else:
            start_factor = ZOOM_FACTOR
            end_factor = 1.0
        def make_frame_zoomed(t):
            t_norm = t / duration
            scale_diff = end_factor - start_factor
            scale_factor = start_factor + scale_diff * (t_norm ** 0.4)

            current_ratio = final_ratio * scale_factor
            new_w = int(w_orig * current_ratio)
            new_h = int(h_orig * current_ratio)

            resampling_method = Image.Resampling.BILINEAR if hasattr(Image, 'Resampling') else Image.BILINEAR
            resized_image = base_image.resize((new_w, new_h), resampling_method)
            x_crop = (new_w - target_w) // 2
            y_crop = (new_h - target_h) // 2

            cropped_image = resized_image.crop(
                (x_crop, y_crop, x_crop + target_w, y_crop + target_h)
            )

            return np.array(cropped_image.convert('RGB'))

        return VideoClip(make_frame_zoomed, duration=duration).set_fps(24)

    def w(self) :
        global FINAL_RESOLUTION, ZOOM_FACTOR, FONT_PATH

        num_texts = len(self.unvocalized_texts)
        num_audio = len(self.audio_paths)

        if num_texts == 0 or num_audio == 0 or len(self.pictures) == 0:
            raise Exception("لا يوجد نصوص أو أصوات أو صور متاحة لإنشاء المقاطع. فشل حرج.")

        num_clips = min(num_texts, num_audio, len(self.pictures))
        print(f"💡 سيتم إنشاء {num_clips} مقطع فيديو (عدد النصوص = {num_texts}، عدد الأصوات = {num_audio}، عدد الصور = {len(self.pictures)}).")

        pictures_to_use = self.pictures[:num_clips]
        texts_to_use = self.unvocalized_texts[:num_clips]
        audio_paths_to_use = self.audio_paths[:num_clips]

        clips = []
        audio_segments = []

        for index, (picture, text_content_raw, audio_path) in enumerate(zip(pictures_to_use, texts_to_use, audio_paths_to_use)) :

            try:
                with AudioFileClip(audio_path) as audio_clip_temp:
                    duration = audio_clip_temp.duration
                print(f"جاري معالجة مقطع رقم {index+1} (المدة من الصوت: {duration:.2f} ثانية)...")
                video_clip = self.create_image_clip_with_zoom(picture, duration, index)
                if video_clip is None:
                    continue
                audio_segments.append(AudioFileClip(audio_path))
                words = text_content_raw.split()
                display_text_list = list(words)
                if len(words) <= 4 :
                    split_index = math.ceil(len(words) / 1)
                    display_text_list.insert(split_index, '\n')

                elif len(words) >= 5 and len(words) <= 10 :
                    split_index = math.ceil(len(words) / 2)
                    display_text_list.insert(split_index, '\n')
                else :
                    split_index = 5
                    display_text_list.insert(split_index, '\n')

                display_text = " ".join(display_text_list)
                current_font = FONT_PATH if os.path.exists(FONT_PATH) else "Arial"
                with TextClip(
                    display_text,
                    fontsize=40,
                    color="yellow",
                    method="caption",
                    stroke_color="black",
                    font=current_font,
                    stroke_width=1,
                    size=(FINAL_RESOLUTION[0] * 0.9, None)
                ).set_position(("center", 840)).set_duration(duration) as text_clip:

                    final_clip = CompositeVideoClip([video_clip, text_clip], size=FINAL_RESOLUTION).set_duration(duration)
                    clips.append(final_clip)

                video_clip.close()

            except Exception as e:
                print(f"❌ خطأ في معالجة المقطع رقم {index+1}: {e}")
                if audio_segments: audio_segments.pop().close()
                continue

        if not clips:
            raise Exception("لم يتم إنشاء أي مقاطع فيديو صالحة. فشل حرج.")

        FADE_DURATION = 1

        try:
            final_video_base = concatenate_videoclips(clips)
            video_audio_base = concatenate_audioclips(audio_segments)

            final_duration = final_video_base.duration
            global_status_label.configure(text="...🔊 جاري دمج مقاطع الصوت الأصلية والموسيقى")

            op = "Sonder(chosic.com).mp3"

            if os.path.exists(op):
                music_clip = AudioFileClip(op).subclip(16).set_duration(final_duration).volumex(0.25)
                combined_audio = CompositeAudioClip([video_audio_base, music_clip])
                final_audio = combined_audio.audio_fadeout(FADE_DURATION).set_duration(final_duration)
            else:
                final_audio = video_audio_base.audio_fadeout(FADE_DURATION)

            final_video_base.audio = final_audio

            final_video_base.write_videofile(
                f"{self.titel}.mp4",
                fps=24,
                codec='libx264',
                preset='ultrafast',
                bitrate='2500k',
                audio_codec='aac',
                threads=4,
                verbose=True,
                remove_temp=True,
                logger='bar'
            )

            # الإغلاق بعد الكتابة فقط
            final_video_base.close()
            video_audio_base.close()
            if os.path.exists(op):
                music_clip.close()

            for clip in clips:
                clip.close()
            for segment in audio_segments:
                segment.close()

        except Exception as e:
            raise Exception(f"فشل حرج في مرحلة الدمج النهائي للفيديو أو الصوت: {e}")

        finally:
            pass

        print("\n✅ تم بنجاح! تم حفظ فيديو الاختبار.")
        notification.notify(
            title="صانع الفيديوهات 📹",
            message="تم إنشاء الفيديو بنجاح\nشكراً لك, المبرمج عبدالله",
            timeout=10
        )

def final() :
    def task():

        try:
            cleanup_directories()
            lab2.configure(state="disabled")

            if not entr.get():
                global_status_label.configure(text="الرجاء كتابة اسم الموضوع للبدء")
                lab2.configure(state="normal")
                return
            
            global_status_label.configure(text="...جاري كتابة السكريبت")
            scriptj = script_writing(title=entr.get())
            scriptj.script()

            global_status_label.configure(text="...جاري تقسيم السكريبت وتشكيله")
            time.sleep(1)
            divided_script = script_division(script_obj=scriptj)
            unvocalized_texts = divided_script.divisio1()
            time.sleep(1)
            vocalized_text = divided_script.division2()

            global_status_label.configure(text="...جاري إنشاء الصور")
            time.sleep(3)
            picture_creator = pictures(script_texts=unvocalized_texts)
            picture = picture_creator.picture()
            
            global_status_label.configure(text="...جاري إنشاء المقاطع الصوتية")
            audio_creator = audio_clips(text=vocalized_text)
            audio_paths = audio_creator.clip()


            global_status_label.configure(text="...جاري إنشاء الفيديو ودمج الصوت (بدون موسيقى خلفية)")
            final_video(pictures_paths=picture, script_processor=divided_script, audio_paths=audio_paths, titel=entr.get().strip()).w()

            global_status_label.configure(text="تم الإنتهاء من إنشاء الفيديو القصير بنجاح")

        except Exception as e:
            global_status_label.configure(text=f"❌ خطأ فادح: {e}")
            print(f"خطأ فادح: {e}")

        finally:
            lab2.configure(state="normal")

    threading.Thread(target=task).start()

global_status_label = ctk.CTkLabel(lolo, font=("Arial", 15), text="الرجاء كتابة اسم الموضوع للبدء", fg_color="gray20", text_color="white")
global_status_label.pack(side=tk.BOTTOM, fill=tk.X)
entr = ctk.CTkEntry(lolo, font=("Arial", 15), placeholder_text="اسم الموضوع", justify='right')
entr.pack(pady=14)
lab2 = ctk.CTkButton(lolo, text="إنشاء الفيديو", font=("Arial", 18, "bold"), command=final)
lab2.pack(pady= 34)
lolo.mainloop()




# moviepy
# proglog
# plyer.platforms.win.notification
# imageio_ffmpeg
# PIL._imagingtk
# PIL._tkinter_finder
# customtkinter

# imageio
# moviepy