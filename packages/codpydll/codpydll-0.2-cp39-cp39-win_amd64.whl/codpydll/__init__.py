import sys,os,ctypes
def mkl_path():
    mkl_path = sys.exec_prefix
    mkl_path = os.path.join(mkl_path,"Library","bin")
    os.environ["PATH"] += os.pathsep + mkl_path
    mkl_path = os.path.join(mkl_path,"mkl_rt.2.dll")
    return mkl_path
hllDll = ctypes.WinDLL(mkl_path())
import codpypyd as cd