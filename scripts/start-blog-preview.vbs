Set ws = CreateObject("Wscript.Shell")
ws.CurrentDirectory = "D:\CC\shared\investment-portal"
ws.Run """D:\CC\shared\investment-portal\scripts\start-blog-preview.bat""", 0, False
