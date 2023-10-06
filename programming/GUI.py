import tkinter as tk
from tkinter import filedialog
import webDriver
import tools

class my_class(object):
    pass

class GUIBoard(object):
    def __init__(self):
        self.root = tk.Tk()
        self.values=[]
        self.entries = []  # 用于存储 Entry 组件的列表
        self.AIFlag = tk.BooleanVar()
        

    def create_entries(self,x,y,width,tag=""):
        tk.Label(self.root,text=tag).place(x=x,y=y)
        entry = tk.Entry(self.root)
        entry.place(x=x,y=y+25)
        entry.config(width=width)
        self.entries.append(entry)

    def create_submit_button(self,x,y):
        # 创建提交按钮
        submit_button = tk.Button(self.root, text="运行脚本", command=self.submit)
        submit_button.grid(row=len(self.entries), column=0)
        submit_button.place(x=x,y=y)

    def create_checkBox(self,x,y,lable):
        checkButton=tk.Checkbutton(self.root,text=lable, variable=self.AIFlag)
        checkButton.place(x=x,y=y)


    def submit(self):

        self.values = [entry.get() for entry in self.entries]
        print(self.values," ",self.AIFlag.get())
        webdriver=webDriver.webRun(self.values[0],int(self.values[1]),self.values[2],self.AIFlag.get())
        webdriver.run()

    def uploadImg(self,x,y):
        upload_button = tk.Button(self.root, text="上传问卷二维码", command=self.upload_image)
        upload_button.place(x=x,y=y)

    def upload_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.jpeg *.png *.gif *.bmp")])

        if file_path:
            self.selected_file = file_path
            print(f"已选择文件：{file_path}")

            qr_code_data = tools.questionnaireTools.decode_qr_code(self,file_path)

            print(qr_code_data)
            if qr_code_data:
                self.entries[0].insert(tk.END, qr_code_data)
      
    def mainBoard(self):
        boardWidth=600
        boardHeight=400

        self.root.title("问卷星自动填写脚本")
        self.root.geometry(f"{boardWidth}x{boardHeight}")

        self.create_entries(5,5,30,"问卷网址(直接输入网站或者上传问卷二维码)")
        self.uploadImg(240,30)
        self.create_entries(5,55,20,"填写次数")
        self.create_checkBox(5,100,"是否使用Ai来填写填空题（会导致脚本运行速度变慢），不勾选则全部填“不知道")
        self.create_entries(5,140,30,"如果要使用此功能，需要填入openAI的api-key")
        #tk.Label(self.root,text="请注意：该脚本无法处理填空题（因为我懒），如果问卷中有填空题，脚本只会填“不知道”").place(x=30,y=110)
        self.create_submit_button(250,200)
        

        self.root.mainloop()




