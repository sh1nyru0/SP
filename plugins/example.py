# 插件类
class example:
    # 初始化数据
    def __init__(self):
        self.model = None
    
    # 导入数据
    def set_model(self, model):
        self.model = model
        
    # 编写插件核心执行方法
    def run(self):
        print(self.model)
     
example = example()
example.set_model(self.model)  # 使用外部的 self.model 初始化插件实例的 model 属性
example.run()
        