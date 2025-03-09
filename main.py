#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import ModernSentinelApp

def main():
    app = QApplication(sys.argv)
    window = ModernSentinelApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
