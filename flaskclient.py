import threading
import sys
from flask import Flask, jsonify, request
from functools import partial
import mjbot

app = Flask(__name__)


class StopThread(StopIteration):
    pass
threading.SystemExit = SystemExit, StopThread
class Thread3(threading.Thread):

    def _bootstrap(self, stop_thread=False):
        def stop():
            nonlocal stop_thread
            stop_thread = True
        self.stop = stop

        def tracer(*_):
            if stop_thread:
                raise StopThread()
            return tracer
        sys.settrace(tracer)
        super()._bootstrap()

partial_run = partial(app.run, host="10.144.177.198", port=80, debug=True, use_reloader=False)

@app.route("/")
async def hello():
    return f"Free channel ALARM"

    
@app.route("/status")
async def status():
    queue = mjbot.get_queue_content()
    status = mjbot.build_channel_status()
    ret = {
        "queue": queue,
        "status": status
    }
    return jsonify(ret)


@app.route("/imagine", methods=["POST"])
async def image():
    data = request.json
    prompt = data["prompt"]
    amount = data["amount"]
    for i in range(amount):
        mjbot.command_queue.put(prompt)
    return "Ok"

flask_thread = Thread3(target=partial_run)

def start():
    flask_thread.start()

def stop():
    flask_thread.stop()