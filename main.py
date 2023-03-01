import mjbot
import flaskclient

flaskclient.start()
try:
    mjbot.start()
except:
    pass
flaskclient.stop()
