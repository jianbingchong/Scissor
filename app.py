import tkinter
import time
from tkinter import scrolledtext
import tkinter.filedialog

from subtitle import SubtitleFile


class SubtitleMain():
    xin = tkinter.Tk()
    path = tkinter.StringVar()

    # 路径赋值
    def selectPath(self):
        path_ = tkinter.filedialog.askopenfilename(title='选择文件')
        self.path.set(path_)

    # 桌面
    def views(self):
        self.xin.geometry('600x400')  # 指定主框体大小
        self.xin.title('钢剪')  # 标题名
        tkinter.Label(self.xin, text="文件").grid(row=4, column=1, sticky=tkinter.E)
        self.xls_path = tkinter.StringVar()
        self.xls_path_entry = tkinter.Entry(self.xin, width=50, stat="readonly")
        self.xls_path_entry["textvariable"] = self.path
        self.xls_path_entry.grid(row=4, column=2, sticky=tkinter.E)
        tkinter.Button(self.xin, text="　选择　", command=self.selectPath).grid(row=4, column=5, sticky=tkinter.E)
        # 占位
        # tkinter.Label(self.xin, text="").grid(row=5, column=0)
        tkinter.Button(self.xin, text="　校验　", command=self.validate).grid(row=4, column=7, sticky=tkinter.E)

        tkinter.Label(self.xin, text="").grid(row=7, column=0)
        # 滚动文本框
        scrolW = 60  # 设置文本框的长度
        scrolH = 18  # 设置文本框的高度
        self.text = scrolledtext.ScrolledText(self.xin, width=scrolW, height=scrolH, wrap=tkinter.WORD)
        self.text.grid(row=10, columnspan=30, sticky=tkinter.E)


    # 验证事件
    def validate(self):
        if not self.path.get():
            self.__clear_scor_text()
            self.text.insert('end', '请选择文件')
            return
        try:
            self.text.delete(1.0, tkinter.END)
            subtitle_file = SubtitleFile.load(self.path.get())
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
        self.views()
        tkinter.mainloop()


def main():
    SubtitleMain().app();
    pass;


if __name__ == "__main__":
    main()