from flask import Flask, send_from_directory
from backend import app
from backend.auth.model import User
from backend.api.project.model import Project
from backend.api.hardware.model import HwSet
from backend.shared.hardware_pool import HardwarePool
import os

app = Flask(__name__, static_folder='', static_url_path='/frontend/build')

@app.route('/', methods=["GET"])
def index():
    return send_from_directory('/frontend/build/', 'index.html')

if __name__ == "__main__":
    HardwarePool.objects().delete()
    hwpool1 = HardwarePool(name="HW 1", total_capacity=100, total_availability=100)
    hwpool2 = HardwarePool(name="HW 2", total_capacity=100, total_availability=100)
    hwpool1.save()
    hwpool2.save()
    User.objects().delete()
    Project.objects().delete()
    HwSet.objects().delete()
    #app.run(debug=True)
    app.run(host='0.0.0.0', debug=False, port=os.environ.get('PORT', 80))
