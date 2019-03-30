import codecs
import copy
import logging
import os
import re

import asstosrt
import chardet
from hanziconv import HanziConv
from pysrt import SubRipTime, SubRipFile
import pysrt
import Segment


ad_key_words = ["人人影视","人人视频APP", "字幕组", "资源Q群", "YYeTs", "原创翻译","网易见外", "招募Q号", "小愿8压制组", "火鸟字幕合并器", "圣城家园"]
one_line_ad_key_words = ["翻译", "字幕", "made by", "Made by"]

def get_encoding(file):
    encoding_detect_result = chardet.detect(open(file, 'rb').read())
    encoding = encoding_detect_result['encoding']
    if not encoding:
        return "utf-8"
    if 'gb2312' == encoding.lower():
        return 'gb18030'
    if 'ascii' == encoding.lower():
        return 'utf-8'
    if 'iso-8859-1' == encoding.lower():
        return 'utf-8'
    if 'iso-8859-7' == encoding.lower():
        return 'utf-8'
    return encoding

def is_one_line(sub):
    return len(sub.text.split('\n', 1)) < 2

def is_one_language(subs):
    return ascii_ratio(subs) > 0.9 or (len(list(filter(is_one_line, subs))) * 1.0 / len(subs) > 0.5)

def ascii_ratio(subs):
    c = 0
    l = 0
    for sub in subs:
        for w in sub.text:
            if ord(w) < 128:
                c += 1
        l += len(sub.text)
    r = c * 1.0 / l
    return r

def erase(subs, first):
    for sub in subs:
        lines = sub.text.split('\n')
        if len(lines) < 2:
            sub.text = '...'
        elif first:
            sub.text = lines[-1]
        else:
            sub.text = "\n".join(lines[0:-1])
    return subs

def remove_styles(text):
    sub = re.sub(r'\{[^\}]+\}', '', text)
    if sub != text:
        return sub
    sub = re.sub(r'<[^>]+>', '', text)
    if sub != text:
        return sub
    # not very sure of the below patterns
    sub = re.sub(r'\([^\)]+\)', '', text)
    if sub != text:
        return sub
    sub = re.sub(r'\[[^\]]+\]', '', text)
    if sub != text:
        return sub
    return text

def english_first(subs1, subs2):
    if ascii_ratio(subs1) > ascii_ratio(subs2):
        return subs1, subs2
    else:
        return subs2, subs1

def preprocess_subtitle(subs):

    encoding = get_encoding(subs)
    print('code {}'.format(encoding))

    subs = pysrt.open(subs, encoding)
    for sub in subs:
        sub.text = remove_styles(sub.text)

    subs.data = sorted(subs.data, key=lambda a: a.start)
    new_subs = [subs.data[0]]
    for sub in subs.data[1:]:
        if sub.start == new_subs[-1].start:
            new_subs[-1].text = new_subs[-1].text + '\n' + sub.text
        else:
            new_subs.append(sub)
    subs.data = new_subs
    subs.clean_indexes()

    mix_language = not is_one_language(subs)
    # remove faked subtitle
    if mix_language:
        new_subs = list(filter(lambda a: not is_one_line(a), subs))
        subs.data = new_subs
        subs.clean_indexes()

    sub1 = copy.deepcopy(subs)
    sub2 = copy.deepcopy(subs)

    if mix_language:
        sub1 = erase(sub1, True)
        sub2 = erase(sub2, False)

    en_subs, cn_subs = english_first(sub1, sub2)

    # reformat for cn first
    for en, cn, sub in zip(en_subs, cn_subs, subs):
        if cn.text != en.text:
            sub.text = en.text + "\n" + cn.text
    return en_subs, subs

VTT_PATTERN = re.compile("(\\d{2}:\\d{2}:\\d{2})\\.(\\d{3})")
def vtt_to_srt(lines):
    results = []
    for line in lines:
        find = VTT_PATTERN.findall(line)
        if len(find) == 2:
            results.append(line.replace(".", ","))
            continue
        else:
            results.append(line)
    return results

def replace_chinese_character(source):
    return source.replace("，", ",")\
        .replace("–", "-")\
        .replace("—", "-")\
        .replace("。", ".")\
        .replace("“", "\"")\
        .replace("”", "\"")\
        .replace("‘", "'")\
        .replace("’", "'")\
        .replace("？", "?")\
        .replace("！", "!")\
        .replace("…", "...")\
        .replace("：", ":")

def check_contain_chinese(check_str):
    is_contained = False
    for c in check_str :
        if '\u4e00' <= c <= '\u9fa5':
            is_contained = True
            break
    return is_contained

def is_english(content):
    return not check_contain_chinese(content)

def is_chinese(content):
    return check_contain_chinese(replace_chinese_character(content))

def count_digital(content):
    count = 0
    for i in range(len(content)):
        c = content[i]
        if (c >= '0' and c<= '9') :
            count += 1
    return count

def is_comment(subtitle_array):
    if len(subtitle_array) == 1:
        content = subtitle_array[0]
        return content.startswith("（") and content.endswith("）")
    return False

def is_advertisement(subtitles):
    for word in ad_key_words:
        for line in subtitles:
            if word in line:
                return True
    if len(subtitles) == 1:
        for word in one_line_ad_key_words:
            if word in line:
                return True
    return False

def to_simple_chinese(content):
    return HanziConv.toSimplified(content)

class SubtitleException(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)
    

class SubtitleFile:

    def __init__(self, subtitles):
        self.subtitles = subtitles

    @staticmethod
    def load(file_path):
        ext = file_path.split('.')[-1].lower()
        encoding = get_encoding(file_path)
        logging.info('{} code {}'.format(file_path, encoding))

        lines = []
        with open(file_path, 'r', encoding=encoding) as f:
            if ext == 'ass' or ext == 'ssa':
                lines = asstosrt.convert(f).split("\n")
                ext = 'srt'
            else:
                for line in f:
                    lines.append(line.strip())
        file = SubtitleFile.load_lines(lines, ext, encoding)
        logging.info("load {} success ".format(file_path))
        return file

    @staticmethod
    def loads(content, ext='srt', encoding='utf-8'):
        lines = content.split("\n")
        return SubtitleFile.load_lines(lines, ext, encoding)

    @staticmethod
    def load_lines(lines, ext, encoding):
        if ext == 'srt':
            lines = SubtitleFile.__fix_srt_lines(lines)
            subtitle_file = SubtitleFile(SubtitleFile.__srt_to_subtitle_file(lines, encoding))
            return subtitle_file
        elif ext == 'vtt':
            lines = vtt_to_srt(lines)
            subtitle_file = SubtitleFile(SubtitleFile.__srt_to_subtitle_file(lines, encoding))
            return subtitle_file
        else:
            raise SubtitleException("wrong file subtitle content")

    @staticmethod
    def __fix_srt_lines(lines):
        pattern = re.compile('\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}')
        fixed_lines = []
        group = [lines[0]]
        have_time = False
        for line in lines[1:]:
            group.append(line)
            if not line:
                if len(group) > 2:
                    fixed_lines.extend(group)
                group = []
                have_time = False
            elif pattern.match(line):
                if have_time:
                    fixed_lines.extend(group[:-2])
                    fixed_lines.append("")
                    group = group[-2:]
                have_time = True
        if group:
            fixed_lines.extend(group)
        return fixed_lines

    @staticmethod
    def __srt_to_subtitle_file(lines, encoding):
        subs = pysrt.from_string("\n".join(lines), encoding=encoding, eol='\n')
        return SubtitleCleaner.fix_subtitle(subs)

    def __is_sentence_ends(self, subtitle_content):
        for line in subtitle_content.split("\n"):
            if line.strip() and line.strip()[-1] in ('.', '。', '!', '！'):
                return True
        return False

    def calc_segments(self, min_duration_mills=140000, minimal_duration=90000, min_sentence_number=None):
        assert(min_duration_mills > minimal_duration)
        subs = self.subtitles
        segments = []
        start_index = 0
        end_index = 0
        part_sentence_number = 0
        end_mills = subs[-1].end.ordinal
        while end_index < len(subs.data):
            part_duration = subs[end_index].end.ordinal - subs[start_index].start.ordinal
            part_sentence_number += 1
            end_sub = subs[end_index]
            end_index += 1
            if end_mills - subs[start_index].start.ordinal < min_duration_mills + minimal_duration:
                min_duration_mills = minimal_duration
            if part_duration >= min_duration_mills \
                    and (not min_sentence_number or part_sentence_number > min_sentence_number)\
                    and self.__is_sentence_ends(end_sub.text):
                segments.append(Segment(subs[start_index].start.ordinal, subs[end_index - 1].end.ordinal))
                start_index = end_index
                part_sentence_number = 0

        if not segments:
            logging.warning("find empty segments when clip subtitle")
            return segments

        last_segment = segments[-1]
        segments.remove(last_segment)
        segments.append(Segment(last_segment.start, subs[end_index - 1].end.ordinal))
        return segments

    def save(self, file):
        subs = self.subtitles
        subs = [str(s) for s in subs]
        new_subs = []
        for sub in subs:
            fields = sub.split('\n')
            fields[0] = ''
            new_subs.append('\n'.join(fields))
        subs = new_subs
        subs = "".join(subs)
        subs = "WEBVTT\n\n" + subs
        content = re.sub("(\d{2}:\d{2}:\d{2}),(\d{3})", lambda m: m.group(1) + '.' + m.group(2), subs)
        with codecs.open(file, 'w', 'utf-8') as outfile:
            outfile.write(content)

    #TODO save by file extension
    def save_srt(self, file):
        self.subtitles.save(path=file, encoding='utf-8')

    #TODO optimize later
    def save_en(self, file):
        subs = self.subtitles
        subs = [str(s) for s in subs]
        new_subs = []
        for sub in subs:
            fields = sub.split('\n')
            fields[0] = ''
            new_subs.append('\n'.join(fields[:3]) + '\n')
        subs = new_subs
        subs = "".join(subs)
        subs = "WEBVTT\n\n" + subs
        content = re.sub("(\d{2}:\d{2}:\d{2}),(\d{3})", lambda m: m.group(1) + '.' + m.group(2), subs)
        with codecs.open(file, 'w', 'utf-8') as outfile:
            outfile.write(content)

    def slice(self, segment):
        subs = self.subtitles
        start_time = SubRipTime(milliseconds=segment.start)
        end_time = SubRipTime(milliseconds=segment.end)
        slices = copy.deepcopy(subs.slice(starts_before=end_time, ends_after=start_time))
        slices.shift(milliseconds=-segment.start)
        slices.clean_indexes()
        return SubtitleFile(slices)

    def shift(self, hours=0, minutes=0, seconds=0, mills=0):
        self.subtitles.shift(hours=hours, minutes=minutes, seconds=seconds, milliseconds=mills)

    def combine_cn_en(self, cn_subtitle_path, en_subtitle_path, output_folder):
        cn_subs = pysrt.open(cn_subtitle_path)
        en_subs = pysrt.open(en_subtitle_path)
        cn_dict = {}
        new_subtitle = []
        for cn_sub in cn_subs:
            cn_dict[cn_sub.start.__str__()] = cn_sub.text
        index = 1
        for en_sub in en_subs:
            if en_sub.start.__str__() in cn_dict:
                subRipItem = copy.deepcopy(en_sub)
                subRipItem.text = en_sub.text + "\n" + cn_dict[en_sub.start.__str__()]
                subRipItem.index = index
                check_contain_chinese
                new_subtitle.append(subRipItem)
                index += 1
            else:
                logging.warning("[combine_cn_en] not found in cn dict, {}".format(en_sub.start.__str__()))
        output_file_path = os.path.join(output_folder, "cn_en_subtitle.vtt")
        self.save(output_file_path)
        return output_file_path

    def length(self):
        return len(self.subtitles)

    def __text(self, sub):
        txs = sub.text.split('\n')
        txt = txs[0]
        return txt

    def word_count(self):
        words = list(map(lambda t: self.__text(t).split(), self.subtitles))
        return sum(map(len, words))


class SubtitleCleaner:

    @staticmethod
    def fix_subtitle_file(subtitile_file):
        logging.info('deal with:{}'.format(subtitile_file))
        subtitile_file.subtitles = SubtitleCleaner.fix_subtitle(subtitile_file.subtitles)
        return subtitile_file

    @staticmethod
    def __do_fix(subtitle, subtitle_lines, chinese_first):
        if len(subtitle_lines) == 2 and is_english(subtitle_lines[0]) and is_english(subtitle_lines[1]):
            if chinese_first:
                subtitle.text = subtitle_lines[1] + '\n' + subtitle_lines[0]
            return
            
        chinese = []
        english = []
        for line in subtitle_lines:
            if is_chinese(line):
                chinese.append(line)
            else:
                english.append(line)
        english_line = replace_chinese_character(" ".join(english))
        chinese_line = to_simple_chinese("".join(chinese))
        subtitle.text = english_line + '\n' + chinese_line

    @staticmethod
    def is_chinese_first(subtitles):
        single_type_lines = []
        type = []
        for s in subtitles:
            subtitle_array = s.text.split('\n')
            types = [is_chinese(t) for t in subtitle_array]
            if len(set(types)) == 2:
                type.append(types[0])
            else:
                single_type_lines.append('\n' + str(s))
        if len(single_type_lines) == 0:
            return type[0]
        raise SubtitleException("必须包含中英文字幕:" + "\n".join(single_type_lines))

    @staticmethod
    def __fix_single_line(subtitle, subtitle_lines, chinese_first):
        if len(subtitle_lines) == 1:
            if is_chinese(subtitle_lines[0]):
                subtitle.text = 'no english subtitle' + '\n' + subtitle_lines[0]
            elif is_english(subtitle_lines[0]):
                subtitle.text = subtitle_lines[0] + '\n' + '无中文字幕'
            else:
                subtitle.text = 'no english subtitle\n无中文字幕'

    @staticmethod
    def fix_subtitle(subtitles):
        subs = subtitles
        for sub in subs:
            sub.text = remove_styles(sub.text)

        subs.data = sorted(subs.data, key=lambda a: a.start)
        subs.clean_indexes()
        new_subtitles = []
        chinese_first = SubtitleCleaner.is_chinese_first(subs)

        count = 0
        for subtitle in subs:
            subtitle_array = subtitle.text.split('\n')
            if is_advertisement(subtitle_array):
                logging.warning("ignore advertisement only {} ".format(subtitle_array))
                continue
            subtitle_array = [s for s in subtitle_array if s.strip()]
            if len(subtitle_array) > 4:
                logging.warning(" error subtitle {}".format(subtitle_array))
                raise SubtitleException("subtitle exception " + str(subtitle_array))

            if not subtitle_array:
                continue
            #may have problem later
            elif len(subtitle_array) == 1:
                count += 1
                continue
            switch_count = 0
            prev_english = is_english(subtitle_array[0])
            for i in range(1, len(subtitle_array)):
                l = subtitle_array[i]
                current_english = is_english(l)
                if current_english != prev_english:
                    switch_count += 1
                prev_english = current_english
            if len(subtitle_array) == 4 and switch_count != 1:
                raise SubtitleException("\n{}".format(subtitle))
            SubtitleCleaner.__do_fix(subtitle, subtitle_array, chinese_first)
            new_subtitles.append(subtitle)
        if count > len(subtitles) * 0.95:
            raise SubtitleException("too much single line content")
        return SubRipFile(new_subtitles)

if __name__ == '__main__':
    subs = SubtitleFile.load("C:\\Users\\zhongjianbin\\Desktop\\50.srt")
