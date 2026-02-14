"""
重构后的主程序入口 - 遵循MVC架构
"""
import tkinter as tk
from controllers.main_controller import MainController


def main():
    root = tk.Tk()
    app = MainController(root)
    root.mainloop()


if __name__ == "__main__":
    main()