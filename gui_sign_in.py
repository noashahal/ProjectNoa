import wx
import win32ui
import win32con
from client_call_management import *
#from simple_window_2 import *
WIDTH = 300
LENGTH = 250
START = 0
BORDER = 5


class GuiAll(wx.Frame):
    """
    """
    def __init__(self, e, title):
        super().__init__(e, title=title)
        self.SetSize((WIDTH, LENGTH))
        #self.Centre()
        self.lock = threading.Lock()
        # The combo box (drop down menu)
        self.combo_box = None
        # The client object
        self.client = None

        # panel:
        self.pnl = wx.Panel(self)  # creates panel
        self.sb = wx.StaticBox(self.pnl)  # sequence of items
        self.sbs = wx.BoxSizer(wx.VERTICAL)  # boarder

        # menu:
        self.make_menu()

    def make_menu(self):
        """
        makes menu with quit
        """
        menu_bar = wx.MenuBar()  # creates a MenuBar
        file_menu = wx.Menu()  # adds menu
        menu_item = file_menu.Append(wx.ID_EXIT, 'Quit', 'Quit application')
        menu_bar.Append(file_menu, 'Menu&')  # adds item to menu
        self.SetMenuBar(menu_bar)  # sets menu bar
        self.Bind(wx.EVT_MENU, self.on_quit, menu_item)  # binds quit function

    def on_quit(self, e):
        """
        when the user presses the quit button,
        the function is called, ending the GUI loop
        """
        self.Close()

    def start_client(self, username):
        """
        starts client when signs in
        """
        self.client = Client(username)

    def start(self):
        """
        sets sizer and shows
        """
        self.SetSizer(self.sbs)
        self.Centre()
        self.Show(True)

    def close(self):
        self.Close(True)

    def anotha_one(self, username):
        """
        opens anotha one
        """
        ex = []
        ex = wx.App(None)
        # ex = wx.App()
        GuiCallOrWait(username)
        ex.MainLoop()
        #del ex


class GuiSignIn(GuiAll):
    """
    initiates ui
    """
    def __init__(self):
        super().__init__(None, "Sign In")
        self.param_user = wx.TextCtrl(self.pnl)  # username panel
        self.init_ui()

    def init_ui(self):
        # username:
        username_sizer = wx.BoxSizer(wx.HORIZONTAL)
        text_user = wx.StaticText(self.pnl, label='Username')  # username text
        username_sizer.Add(window=text_user, proportion=START, flag=wx.ALL | wx.CENTER, border=BORDER)
        username_sizer.Add(window=self.param_user, proportion=START, flag=wx.ALL | wx.CENTER, border=BORDER)

        # sign in button:
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        sign_in_btn = wx.Button(self.pnl, label='Sign In')
        sign_in_btn.Bind(wx.EVT_BUTTON, self.on_signed_in)
        btn_sizer.Add(window=sign_in_btn, proportion=START, flag=wx.ALL | wx.CENTER, border=BORDER)

        # size:
        self.sbs.Add(username_sizer, proportion=START, flag=wx.ALL | wx.CENTER, border=BORDER)
        self.sbs.Add(btn_sizer, proportion=START, flag=wx.ALL | wx.CENTER, border=BORDER)

        self.start()

    def on_signed_in(self, e):
        """
        when the user presses the send button,
        this function is called, which in turn
        generates the query by combining all parameters
        given by the user, and displays the text inside a message box.
        """
        username = self.param_user.GetValue()
        GuiCallOrWait(username)
        self.Close(True)


class GuiCallOrWait(GuiAll):

    def __init__(self, username):
        super().__init__(None, "Call Window")
        self.username = username
        self.start_client(username)
        #self.options = self.client.connected
        self.init_ui()

    def init_ui(self):
        """
        call window
        options for calling or waiting for a call
        """
        # buttons
        call_btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        # call button
        call_btn = wx.Button(self.pnl, label="make call")
        call_btn.Bind(wx.EVT_BUTTON, self.on_call)
        # wait for call button
        #wait_btn = wx.Button(self.pnl, label="wait for call")
        #wait_btn.Bind(wx.EVT_BUTTON, self.on_wait)
        # size
        call_btn_sizer.Add(window=call_btn, proportion=START, flag=wx.ALL | wx.CENTER, border=BORDER)
        #call_btn_sizer.Add(window=wait_btn, proportion=START, flag=wx.ALL | wx.CENTER, border=BORDER)
        self.sbs.Add(call_btn_sizer, proportion=START, flag=wx.ALL | wx.CENTER, border=BORDER)
        wait_for_call_thread = threading.Thread(target=self.on_wait)
        wait_for_call_thread.start()
        self.start()

    def on_call(self, e):
        #self.client.initiate_calling()
        #self.options = self.client.connected
        #print("call or wait options: {}".format(self.options))
        GuiCallOptions(self.client, self.username)
        self.Close(True)

    def on_wait(self):
        """
        waits for someone to call
        """
        print("waiting for call")
        while not self.client.being_called:
            time.sleep(TIME_SLEEP)
            #print("waiting for call")
        #self.close()
        self.Close(True)
        self.getting_called()

    def getting_called(self):
        """
        when gets a call
        """
        person_calling = self.client.person_calling
        if win32ui.MessageBox("{} is calling you. Do you want to answer?".format(self.client.person_calling),
                              "Bringgggg", win32con.MB_YESNOCANCEL) == win32con.IDYES:
            self.on_answer()
        else:
            self.on_dont_answer()

    def on_answer(self):
        """
        when answer clicked
        """
        #self.Close(True)
        self.client.answer()

    def on_dont_answer(self):
        """
        when dont answer clicked
        """
        #self.Close(True)
        self.client.dont_answer()
        #GuiCallOrWait(self.username)


class GuiCallOptions(GuiAll):

    def __init__(self, client, username):
        super().__init__(None, "Options Window")
        #self.text = wx.TextCtrl(self.pnl, style=wx.TE_MULTILINE)
        self.username = username
        self.client = client
        self.options = self.client.connected
        if self.username in self.options:
            self.options.remove(self.username)
        self.options_lstbox = wx.ListBox(self.pnl, choices=self.options, style=wx.LB_SINGLE, name="contacts")
        self.init_ui()

    def init_ui(self):
        # call options
        options_sizer = wx.BoxSizer(wx.HORIZONTAL)
        call_btn = wx.Button(self.pnl, label='Call')
        call_btn.Bind(wx.EVT_BUTTON, self.on_call)
        options_sizer.Add(window=self.options_lstbox, proportion=START, flag=wx.ALL | wx.CENTER, border=BORDER)
        options_sizer.Add(window=call_btn, proportion=START, flag=wx.ALL | wx.CENTER, border=BORDER)
        self.sbs.Add(options_sizer, proportion=START, flag=wx.ALL | wx.CENTER, border=BORDER)
        self.start()

    def on_call(self, e):
        """
        when one option clicked
        """
        calling = self.options_lstbox.GetString(self.options_lstbox.GetSelection())
        print(calling)
        self.client.initiate_calling(calling)
        self.Close(True)
        GuiWait(self.username, self.client)


class GuiWait(GuiAll):
    """
    window in which waits for answer
    """
    def __init__(self, username, client):
        super().__init__(None, "Wait Window")
        self.username = username
        self.client = client
        self.answered_call = False
        self.answered = False
        self.init_ui()

    def init_ui(self):
        text_sizer = wx.BoxSizer(wx.HORIZONTAL)
        wait_text = wx.StaticText(self.pnl, label='Waiting For Answer....')
        text_sizer.Add(window=wait_text, proportion=START, flag=wx.ALL | wx.CENTER, border=BORDER)
        self.sbs.Add(text_sizer, proportion=START, flag=wx.ALL | wx.CENTER, border=BORDER)
        wait_for_answer_thread = threading.Thread(target=self.on_wait_for_answer)
        wait_for_answer_thread.start()
        self.start()
        self.wait_for_answer_forreal()

        #self.on_wait_for_answer()

    def on_wait_for_answer(self):
        """
        waits for someone to call
        """
        print("waiting for answer")
        while not self.client.answered_call:
            time.sleep(TIME_SLEEP)
            #print("waiting for call")
        #self.close()
        if self.client.answered:
            self.answered = True
            print("I was answered!!!")
        else:
            self.answered = False
            print("I wasnt answered!!!")
        self.answered_call = True
        self.Close(True)

    def wait_for_answer_forreal(self):
        """
        out of loop so we can open new gui window gg
        """
        while not self.answered_call:
            time.sleep(TIME_SLEEP)
        if self.answered:  # if answered, starts call
            print("I was answered!!! forreal")
            self.client.start_call(self.client.chosen_contact)
        else:
            print("I wasnt answered!!! forreal")
            self.didnt_answer_window()

    def didnt_answer_window(self):
        """
        if user didnt answer, gives 2 options
        back to main window or disconnect
        """
        if win32ui.MessageBox("{} didnt answer :( go back to main window?".format(self.client.chosen_contact),
                              "didnt answer!!",
                              win32con.MB_YESNOCANCEL) == win32con.IDYES:

            self.anotha_one(self.username)
        else:
            self.client.close_all()
            self.Close(True)


class GuiGettingCalled(GuiAll):
    """
    window which opens when getting called
    """
    def __init__(self, client):
        super().__init__(None, "BRINGGGGG")
        print("here at gui getting called")
        self.client = client
        # person calling this user
        self.person_calling = self.client.person_calling
        print("{} is calling".format(self.person_calling))
        # text:
        text_sizer = wx.BoxSizer(wx.HORIZONTAL)
        label = str(self.person_calling) + " is calling"
        wait_text = wx.StaticText(self.pnl, label=label)
        text_sizer.Add(window=wait_text, proportion=START, flag=wx.ALL | wx.CENTER, border=BORDER)
        # buttons:
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        # call button
        answer_btn = wx.Button(self.pnl, label="answer")
        answer_btn.Bind(wx.EVT_BUTTON, self.on_answer)
        # wait for call button
        dont_answer_btn = wx.Button(self.pnl, label="dont")
        dont_answer_btn.Bind(wx.EVT_BUTTON, self.on_dont_answer)
        btn_sizer.Add(window=answer_btn, proportion=START, flag=wx.ALL | wx.CENTER, border=BORDER)
        btn_sizer.Add(window=dont_answer_btn, proportion=START, flag=wx.ALL | wx.CENTER, border=BORDER)
        # sizers:
        self.sbs.Add(text_sizer, proportion=START, flag=wx.ALL | wx.CENTER, border=BORDER)
        self.sbs.Add(btn_sizer, proportion=START, flag=wx.ALL | wx.CENTER, border=BORDER)
        print("starting window you want:")
        self.start()
        print("started")

    def on_answer(self, e):
        """
        when answer clicked
        """
        self.Close(True)
        self.client.answer()

    def on_dont_answer(self, e):
        """
        when dont answer clicked
        """
        self.Close(True)
        self.client.dont_answer()


def main():
    """
    begins an app loop,
    creates a GUI.
    when user quits, ends loop.
    """
    ex = []
    ex = wx.App(None)
    # ex = wx.App()
    GuiSignIn()
    ex.MainLoop()
    #del ex


if __name__ == '__main__':
    main()