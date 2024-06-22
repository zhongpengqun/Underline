# Reference
- 本项目需要借鉴多线程编程
        - https://github.com/aws-samples/kinesis-poster-worker/tree/master



# multi thread的时候如何ctrl + c的时候exit system
        - https://stackoverflow.com/questions/4330111/meaning-of-daemon-property-on-python-threads

        - ctrl + c 退出 线程

# keyboard lib 建议看下doc，非常有用
https://github.com/boppreh/keyboard




def winEnumHandler( hwnd, ctx ):
    if win32gui.IsWindowVisible( hwnd ):
        print ( hex( hwnd ), win32gui.GetWindowText( hwnd ) )


def get_menu_item_txt(menu,idx):
    import win32gui_struct
    mii, extra = win32gui_struct.EmptyMENUITEMINFO() #新建一个win32gui的空的结构体mii
    win32gui.GetMenuItemInfo(menu, idx, True, mii) #将子菜单内容获取到mii
    ftype, fstate, wid, hsubmenu, hbmpchecked, hbmpunchecked,\
    dwitemdata, text, hbmpitem = win32gui_struct.UnpackMENUITEMINFO(mii) #解包mii
    return text

def run():
    # xuhao=win32api.ShellExecute(1,'notepad',r'C:\Users\zlzk\Documents\GitHub\MyCustomizedShortcuts\README.md','','',1)
    subprocess.Popen(['notepad.exe', r'C:\Users\zlzk\Documents\GitHub\MyCustomizedShortcuts\README.md'])

    print('正在打开软件，请稍等。。。。')
    time.sleep(5)

    print(dir(win32gui))
    print('------------------')
    win32gui.EnumWindows( winEnumHandler, None )

    handle=win32gui.FindWindow(None,'README - 记事本')
    handleEdit=win32gui.FindWindowEx(handle,None,'EDIT',None)
    menu=win32gui.GetMenu(handle)
    menu1=win32gui.GetSubMenu(menu,0)#子菜单文件，编辑，格式等
    # for i in range(5):
    #     print(get_menu_item_txt(menu,i))
    content=['人生',]
    for index,li in enumerate(content):
        for cont in li:
            print(cont)
            win32gui.SendMessage(handleEdit, win32con.WM_CHAR, ord(cont), 0)
            time.sleep(0.2)
        if index%2!=0:
            win32api.keybd_event(13,0,0,0)
            time.sleep(0.5)
            win32api.keybd_event(13,0,win32con.KEYEVENTF_KEYUP,0)

    cmdId=win32gui.GetMenuItemID(menu1,3)#获取保存按钮
    print('----------')
    print(cmdId)
    win32gui.PostMessage(handle,win32con.WM_COMMAND,cmdId,0)#点击保存
    print('============')
    win32gui.PostMessage(handle,win32con.WM_CLOSE,0,0)#关闭窗口
    print('.............')





D:\Github\MyCustomizedShortcuts>pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple