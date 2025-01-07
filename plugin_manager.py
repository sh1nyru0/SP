import pluggy
from qtpy import uic

hookspec = pluggy.HookspecMarker("myproject") # hook标签 用于标记hook
hookimpl = pluggy.HookimplMarker("myproject") # hook实现标签 用于标记hook的一个或多个实现

class MySpec:
    """hook集合"""
    @hookspec
    def myhook(self, arg1, arg2):
        pass

    # @hookspec
    # def my_hook_fun1(self, arg1, arg2):
    #     pass
    #
    # @hookspec
    # def my_hook_fun2(self, arg1, arg2):
    #     pass

class Plugin_1:
    """hook实现类1"""
    @hookimpl
    def myhook(self, arg1, arg2):
        print("Plugin_1.myhook called")
        return arg1 + arg2

    # @hookimpl
    # def my_hook_fun1(self, arg1, arg2):

class PluginManager:
    def __init__(self):
        # 初始化PluginManager
        self.pm = pluggy.PluginManager("myproject")

        # 登记hook集合(hook函数声明)
        self.pm.add_hookspecs(MySpec)
        self.plugins = self.pm.get_plugins()

        self.ui = uic.loadUi("plugin_manager.ui")
        self.ui.btnAdd.clicked.connect(self.onAdd)
        # self.ui.btnDelete.clicked.connect(self.onDelete)
        # self.ui.btnStart.clicked.connect(self.onStart)
        for plugin in self.plugins:
            self.ui.comboBox.addItem(plugin)

    def onAdd(self):
        self.pm.register(Plugin_1())
        print(self.plugins)
        for plugin in self.plugins:
            self.ui.comboBox.addItem(plugin)

