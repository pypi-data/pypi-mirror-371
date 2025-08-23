# 方案2：延迟导入（在函数内部导入）
good_bullins = None
def lazy_import():
    global good_bullins
    from new_python import good_bullins
# 方案2：延迟导入（在函数内部导入）
modules = None
def lazy_import():
    global modules
    from new_python import modules
__version__ = '0.0.1'
__author__ = 'jason'
__all__ = ['good_builtins', 'modules']