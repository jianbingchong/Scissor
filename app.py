import copy
import os
import tkinter
import time
from tkinter import scrolledtext
import tkinter.filedialog

from moviepy.video.io.VideoFileClip import VideoFileClip
from pysrt import SubRipTime

from subtitle import SubtitleFile


class SubtitleMain():
    mainWindow = tkinter.Tk()
    subtitle_path = tkinter.StringVar()
    video_path = tkinter.StringVar()
    output_path = tkinter.StringVar()


    # 路径赋值
    def selectSubtitlePath(self):
        _path = tkinter.filedialog.askopenfilename(title='选择字幕文件')
        self.subtitle_path.set(_path)

    def selectVideoPath(self):
        _path = tkinter.filedialog.askopenfilename(title='选择视频文件')
        self.video_path.set(_path)

    def selectOutputFolder(self):
        _path = tkinter.filedialog.askdirectory(title='请选择路径')
        self.output_path.set(_path)

    # # 桌面
    def grid_views(self):
        self.mainWindow.geometry('600x400')  # 指定主框体大小
        self.mainWindow.title('钢剪')  # 标题名
        self.mainWindow.resizable(width=True, height=True)
        tkinter.Label(self.mainWindow, text="字幕文件").grid(row=4, column=1, sticky=tkinter.E, padx=5, pady=5)
        self.xls_path = tkinter.StringVar()
        self.xls_path_entry = tkinter.Entry(self.mainWindow, width=50, stat="readonly")
        self.xls_path_entry["textvariable"] = self.subtitle_path
        self.xls_path_entry.grid(row=4, column=2, sticky=tkinter.E)
        tkinter.Button(self.mainWindow, text="　选择　", command=self.selectSubtitlePath).grid(row=4, column=5, sticky=tkinter.E)
        tkinter.Button(self.mainWindow, text="　校验　", command=self.validate).grid(row=4, column=7, sticky=tkinter.E)

        tkinter.Label(self.mainWindow, text="视频文件").grid(row=5, column=1, sticky=tkinter.E)
        self.video_path_entry = tkinter.Entry(self.mainWindow, width=50, stat="readonly")
        self.video_path_entry["textvariable"] = self.video_path
        self.video_path_entry.grid(row=5, column=2, sticky=tkinter.E)
        tkinter.Button(self.mainWindow, text="　选择　", command=self.selectVideoPath).grid(row=5, column=5, sticky=tkinter.E)
        frame_root = tkinter.Frame(self.mainWindow)
        time_frame = tkinter.Frame(frame_root).grid(row=6, columnspan=4)
        tkinter.Label(time_frame, text="开始时间:").grid(row=0, column=1,  sticky=tkinter.W)
        tkinter.Text(time_frame, width=10, height=1).grid(row=0, column=2, sticky=tkinter.W)

        tkinter.Label(time_frame, text="结束时间:").grid(row=0, column=3, sticky=tkinter.W)
        tkinter.Text(time_frame, width=10, height=1).grid(row=0, column=4, sticky=tkinter.W)


        tkinter.Label(self.mainWindow, text="").grid(row=7, column=0)
        # 滚动文本框
        scrolW = 60  # 设置文本框的长度
        scrolH = 18  # 设置文本框的高度
        self.text = scrolledtext.ScrolledText(self.mainWindow, width=scrolW, height=scrolH, wrap=tkinter.WORD)
        self.text.grid(row=10, columnspan=30, sticky=tkinter.E)


    def pack_views(self):
        self.mainWindow.geometry('600x500')  # 指定主框体大小
        self.mainWindow.title('钢剪')  # 标题名
        self.mainWindow.resizable(width=True, height=True)
        frame_root = tkinter.Frame(self.mainWindow)
        subtitle_frame = tkinter.Frame(frame_root)
        tkinter.Label(subtitle_frame, text="字幕文件").pack(side=tkinter.LEFT, anchor=tkinter.NW,padx=5, pady=5, fill=tkinter.X, expand=tkinter.YES)
        self.xls_path = tkinter.StringVar()
        self.xls_path_entry = tkinter.Entry(subtitle_frame, width=50, stat="readonly")
        self.xls_path_entry["textvariable"] = self.subtitle_path
        self.xls_path_entry.pack(side=tkinter.LEFT, anchor=tkinter.NW, padx=5, pady=5, fill=tkinter.X)
        tkinter.Button(subtitle_frame, text="　选择　", command=self.selectSubtitlePath).pack(side=tkinter.LEFT, anchor=tkinter.NW, padx=5, pady=5, fill=tkinter.X)

        tkinter.Button(subtitle_frame, text="　校验　", command=self.validate_subtitle).pack(side=tkinter.LEFT, anchor=tkinter.NW, padx=5, pady=5, fill=tkinter.X)
        #
        video_frame = tkinter.Frame(frame_root)
        tkinter.Label(video_frame, text="视频文件").pack(side=tkinter.LEFT, padx=5, pady=5)
        self.video_path_entry = tkinter.Entry(video_frame, width=50, stat="readonly")
        self.video_path_entry["textvariable"] = self.video_path
        self.video_path_entry.pack(side=tkinter.LEFT, anchor=tkinter.NW, padx=5, pady=5, fill=tkinter.X)
        tkinter.Button(video_frame, text="　选择　", command=self.selectVideoPath).pack(side=tkinter.LEFT, padx=5, pady=5)

        config_frame = tkinter.Frame(frame_root)
        tkinter.Label(config_frame, text="开始时间:").pack(side=tkinter.LEFT, padx=5, pady=5)
        self.start_text = tkinter.Text(config_frame, width=20, height=1)
        self.start_text.pack(side=tkinter.LEFT, padx=5, pady=5)

        tkinter.Label(config_frame, text="结束时间:").pack(side=tkinter.LEFT, padx=5, pady=5)
        self.end_txt = tkinter.Text(config_frame, width=20, height=1)
        self.end_txt.pack(side=tkinter.LEFT, padx=5, pady=5)

        output_frame = tkinter.Frame(frame_root)
        tkinter.Label(output_frame, text="输出路径").pack(side=tkinter.LEFT, padx=5, pady=5)
        self.output_path_entry = tkinter.Entry(output_frame, width=50, stat="readonly")
        self.output_path_entry["textvariable"] = self.output_path
        self.output_path_entry.pack(side=tkinter.LEFT, anchor=tkinter.NW, padx=5, pady=5, fill=tkinter.X)
        tkinter.Button(output_frame, text="　选择　", command=self.selectOutputFolder).pack(side=tkinter.LEFT, padx=5, pady=5)
        tkinter.Button(output_frame, text="　校验　", command=self.clip).pack(side=tkinter.LEFT,
                                                                                         anchor=tkinter.NW, padx=5,
                                                                                         pady=5, fill=tkinter.X)
        # 滚动文本框
        scrolW = 60  # 设置文本框的长度
        scrolH = 18  # 设置文本框的高度
        self.text = scrolledtext.ScrolledText(self.mainWindow, width=scrolW, height=scrolH, wrap=tkinter.WORD)
        self.text.pack(side=tkinter.BOTTOM, anchor=tkinter.CENTER, fill=tkinter.BOTH, expand=tkinter.YES, padx=5, pady=10)

        subtitle_frame.pack(side=tkinter.TOP,  anchor=tkinter.NW, expand=tkinter.YES, fill=tkinter.BOTH)
        video_frame.pack(side=tkinter.TOP,  anchor=tkinter.NW, expand=tkinter.YES, fill=tkinter.BOTH)
        config_frame.pack(side=tkinter.TOP,  anchor=tkinter.NW, fill=tkinter.BOTH)
        output_frame.pack(side=tkinter.TOP,  anchor=tkinter.NW, fill=tkinter.BOTH)
        frame_root.pack()

    def clip(self):
        start_time_mills = float(self.start_text.get('0.0', tkinter.END))
        end_time_mills = float(self.end_txt.get('0.0', tkinter.END))
        subtitle = SubtitleFile.load(self.subtitle_path.get())
        subs = subtitle.subtitles
        video = VideoFileClip(self.video_path.get())
        start_time = SubRipTime(milliseconds=start_time_mills)
        end_time = SubRipTime(milliseconds=end_time_mills)
        slices = copy.deepcopy(subs.slice(starts_before=end_time, ends_after=start_time))
        slices.shift(milliseconds=-start_time_mills)
        slices.clean_indexes()
        output_sutbitle = SubtitleFile(slices)
        output_subtitle_file = os.path.join(self.output_path.get(), 'out_' + self.subtitle_path.get().replace('\\','/').split('/')[-1])
        output_sutbitle.save(output_subtitle_file)
        video_clip = video.subclip(t_start=start_time_mills, t_end=end_time_mills)
        output_video_file = os.path.join(self.output_path.get(),  'out_' + self.video_path.get().replace('\\','/').split('/')[-1].replace("mkv", "mp4"))
        video_clip.write_videofile(output_video_file, audio_codec='aac', progress_bar=False)
        self.__clear_scor_text()
        self.text.insert('end', output_subtitle_file + '\n' + output_video_file)



    def validate_subtitle(self):
        if not self.subtitle_path.get():
            self.__clear_scor_text()
            self.text.insert('end', '请选择文件')
            return
        try:
            self.text.delete(1.0, tkinter.END)
            subtitle_file = SubtitleFile.load(self.subtitle_path.get())
            self.text.insert('end', '字幕校验通过')
        except Exception as ex:
            message = str(ex)
            if message == 'wrong file subtitle content':
                message = '字幕文件格式不正确，目前只支持 srt,ass,vtt格式'
            elif message == 'can not determine language ordinary':
                message = '字幕每一段请确保一行中文一行英文'
            self.text.see(tkinter.END)  # 一直查看文本的最后位置~
            time.sleep(0.5)
            self.text.insert('end', "字幕异常:\n" + message + "\r\n")
            self.text.update()  # 一直更新输出

    def __clear_scor_text(self):
        self.text.delete(1.0, tkinter.END)

    def app(self):
        # self.grid_views()
        self.pack_views()
        tkinter.mainloop()


def main():
    SubtitleMain().app();
    pass;


if __name__ == "__main__":
    main()