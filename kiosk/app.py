from flask import Flask, render_template, redirect, url_for , request, make_response
import serial
import json
import time
import RPi.GPIO as GPIO
import requests
import qrcode
import io
from cryptography.fernet import Fernet
import base64
import os

key = b'redacted'
fernet = Fernet(key)

API_KEY = 'redacted'
API_URL = "redacted"

global offical_kiosk
offical_kiosk = False

global race_running
race_running = False

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)
GPIO.output(18, GPIO.LOW)

port = serial.Serial('/dev/ttyS0', baudrate=115200, timeout=0.1)

if offical_kiosk:
    race_port = serial.Serial('/dev/ttyAMA2', baudrate=115200, timeout=0.1)

data = {
    "machine_id" :"",
    "deep_qa_pass":"",
    "deep_easy_hs":"",
    "deep_easy_win_count":"",
    "deep_easy_fail_count":"",
    "deep_norm_hs":"",
    "deep_norm_win_count":"",
    "deep_norm_fail_count":"",
    "deep_hard_hs":"",
    "deep_hard_win_count":"",
    "deep_hard_fail_count":"",
    "initials":"",
    "deep_official_hs":"",
    "deep_official_win_count":"",
    "deep_official_fail_count":""
}

data_keys = list(data.keys())
kiosk_keys = ["initials","deep_official_hs","deep_official_win_count","deep_official_fail_count"]
expected_keys = []
for key in data_keys:
    if key not in kiosk_keys:
        expected_keys.append(key)

app = Flask(__name__)

@app.route("/")
def index():
    global offical_kiosk
    clear_data()
    GPIO.output(18, GPIO.LOW)
    return render_template("index.html",offical_kiosk=offical_kiosk) 

@app.route("/loading")
def loading():
    return render_template("loading.html")

@app.route("/sync")
def sync():
    global offical_kiosk
    try:
        global data
        data.update(sync_badge())
    except Exception as e:
        print("badge sync fail")
        print(e)
        redir = "failure"
        return redir
    
    try:
        r = requests.post(API_URL+'/api/kioskInit', headers={"X-API-Key":API_KEY}, json={"machine_id": data['machine_id']})
        if r.json()['success'] == True:
            initials=str(r.json()['initials'])
            print(f'\t[*] known badge. machine_id:{ data["machine_id"] } ,initials:{initials}')
            data.update(initials=initials)
            if offical_kiosk:
                redir = "/race"
            else:
                send_data()
                redir = "/complete"
        else:
            print('\t[*] unknown badge. prompting for initials')
            redir = "/initials"
    except Exception as e:
        print("kiosk init request failed. bad API key?")
        print(e)
        redir = "failure"
    return redir

@app.route("/race")
def race():
    global data
    GPIO.output(18, GPIO.LOW)
    if data_empty():
        return redirect('/')
    if out_of_attempts():
        return redirect('/offical_complete')
    return render_template("race.html",data=data)

@app.route("/run_race")
def run_race():
    if data_empty():
        return {"outcome":"empty"}
    if out_of_attempts():
        return {"outcome":"out_of_attempts"}
    return run_race()

@app.route("/initials")
def initials():
    if data_empty():
        return redirect('/')
    return render_template("initials.html")

@app.route("/set_initials")
def set_initials():
    global data
    if data_empty():
        return redirect('/')
    requested_initials = str(request.args.get('initials'))
    if len(requested_initials) != 3:
        return redirect('/initials?error=not3')
    r = requests.post(API_URL+'/api/setInitials', headers={"X-API-Key":API_KEY}, json={ "machine_id": data['machine_id'], "initials": requested_initials })
    if r.json()['success'] == False:
        print(f'\t[*] recieved initials:{requested_initials} are in use already. try again')
        return redirect('/initials?error=taken')
    else:
        print(f'\t[*] recieved initials:{requested_initials} are accepted.')
        data.update(initials=str(requested_initials))
        send_data()
        if offical_kiosk:
            return redirect('/race')
        else:
            return redirect('/complete')

@app.route("/offical_complete")
def offical_complete():
    global data
    print(data)
    if data_empty():
        return redirect('/')
    send_data()
    wins = int(data["cumulative_deep_official_win_count"]) if data["cumulative_deep_official_win_count"] else 0
    fails = int(data["cumulative_deep_official_fail_count"]) if data["cumulative_deep_official_fail_count"] else 0
    
    official_win_ratio = calc_win_ratio(wins,(wins+fails))
    return render_template("offical_complete.html",data=data,official_win_ratio=official_win_ratio)

@app.route("/complete")
def complete():
    if data_empty():
        return redirect('/')
    GPIO.output(18, GPIO.LOW)
    easy_win_ratio = calc_win_ratio(data["deep_easy_win_count"],(data["deep_easy_win_count"]+data["deep_easy_fail_count"])) 
    norm_win_ratio = calc_win_ratio(data["deep_norm_win_count"],(data["deep_norm_win_count"]+data["deep_norm_fail_count"]))
    hard_win_ratio = calc_win_ratio(data["deep_hard_win_count"],(data["deep_hard_win_count"]+data["deep_hard_fail_count"]))
    return render_template("complete.html",data=data,easy_win_ratio=easy_win_ratio,norm_win_ratio=norm_win_ratio,hard_win_ratio=hard_win_ratio)

@app.route('/qr.png')     
def ui_qrcode_page():
    global data
    if data_empty():
        return redirect('/')
    machineID = data['machine_id']
    encmachineID = fernet.encrypt(machineID.encode())
    code = "https://side-quests.kernelcon.org/badgesync?id="+str(base64.b64encode(encmachineID).decode('utf-8'))
    print(code)
    qr_code_img = generate_qr_image(code)
    buffer = io.BytesIO()
    qr_code_img.save(buffer, format="PNG")  
    buffer.seek(0)
    response = make_response(buffer.read()) 
    response.content_type = 'image/png'
    return response

def out_of_attempts():
    global data
    if (int(data['deep_official_fail_count'] or 0) + int(data['deep_official_win_count'] or 0)) >= 3:
        return True
    else:
        return False

def run_race():
    global data
    global race_running

    if not race_running:
        race_running = True
        now = time.time()
        done = False
        race_port.write('go'.encode('utf-8'))
        while (time.time()-now <65) and not done:
            try:
                line = race_port.readline()
                print(line)
                if "fail" in line.decode("utf-8") or "win" in line.decode("utf-8") or "boot" in line.decode("utf-8"):
                    print(line)
                    done = True
                    if "fail" in line.decode("utf-8") or "boot" in line.decode("utf-8"):
                        outcome = "fail"
                        score = None
                        data['deep_official_fail_count'] = int(data['deep_official_fail_count'] or 0)+ 1
                    if "win" in line.decode("utf-8"):
                        outcome = "win"
                        data['deep_official_win_count'] = int(data['deep_official_win_count'] or 0)+ 1
                        score = int(line.decode("utf-8").split()[1])
                        if score > int(data['deep_official_hs'] or 0):
                            data['deep_official_hs'] = score
                    race_running = False
                    return {'outcome':outcome,'score':score}
                time.sleep(.1)
            except Exception as e:
                print(e)
                continue
        race_running = False
        return "timeout"
    return {'outcome':"we_be_running"}
        


def calc_win_ratio(x,y):
    try:
        return int((x/y)*100)
    except ZeroDivisionError:
        return 0

def generate_qr_image(string):
    qr = qrcode.QRCode(version=1, box_size=10, border=4, error_correction=qrcode.constants.ERROR_CORRECT_L)
    qr.add_data(string)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white") 

def data_empty():
    global data
    empty = True
    for key in data:
        if data[key] != "":
            empty = False
    return empty

def clear_data():
    global data
    for key in data:
        data[key] = ""
    print(f'[*] data cleared.')

def send_data():
    try:
        global data
        if data['deep_easy_hs'] == 1000:
            data.update(deep_easy_hs=None)
        if data['deep_norm_hs'] == 1000:
            data.update(deep_norm_hs=None)
        if data['deep_hard_hs'] == 1000:
            data.update(deep_hard_hs=None)
        
        if data['deep_official_hs'] == "":
            data.update(deep_official_hs=None)
        if data['deep_official_win_count'] == "":
            data.update(deep_official_win_count=None)
        if data['deep_official_fail_count'] == "":
            data.update(deep_official_fail_count=None)
        #print(data)
        r = requests.post(API_URL+'/api/uploadScores', headers={"X-API-Key":API_KEY}, json=data)
        #print(r.json())
        response = r.json()['data']
        data.update(deep_easy_hs_rank=response['deep_easy_hs_rank'])
        data.update(deep_norm_hs_rank=response['deep_norm_hs_rank'])
        data.update(deep_hard_hs_rank=response['deep_hard_hs_rank'])
        data.update(deep_official_hs_rank=response['deep_official_hs_rank'])

        data.update(cumulative_deep_official_hs=response['cumulative_deep_official_hs'])
        data.update(cumulative_deep_official_win_count=response['cumulative_deep_official_win_count'])
        data.update(cumulative_deep_official_fail_count=response['cumulative_deep_official_fail_count'])
        data.update(cumulative_deep_official_fail_count=response['cumulative_deep_official_fail_count'])
        print(f"\t[+] {time.strftime('%X %x %Z')} Badge data send. job done.")
    except Exception as e:
        print(e)
        print("[!] sending data has failed")

def sync_badge():
    print(f"[+] {time.strftime('%X %x %Z')} Starting badge sync and send")
    GPIO.output(18, GPIO.HIGH)
    now = time.time()
    done = False
    while (time.time()-now <10) and not done:
        try:
            line = port.readline()
            if line:
                if b'\x00' in line:
                    print("\t[*] ate line with null in it")
                    continue
                data = json.loads(line)
                print(data)
                if data:
                    print("\t[*] Received valid json")
                    if validate_missing_keys(data):
                        print("\t[*] Dictionary contains expected keys")
                        if validate_null_keys(data):
                            print("\t[*] Dictionary contains no null values")
                            if validate_machine_id(data):
                                print("\t[*] machine_id valid")
                                if validate_integer_values(data):
                                    print("\t[*] deep vars are integer")
                                    print("\t[*] communicating to badge 'json-validated'")
                                    port.write('json-validated'.encode('utf-8'))
                                    # data validated
                                    done = True
                                    print("\t[*] Badge sync cycle complete")
                                    #print(data)
                                    return data
                                else:
                                    print("deep vars are not integer")
                            else:
                                print("machine_id not valid")
                        else:
                            print("Dictionary contains null values")
                            port.write('null-values-received'.encode('utf-8'))
                    else:
                        print("Dictionary missing expected keys")
                        port.write('json-missing-keys'.encode('utf-8'))
                else:
                    print("not valid json")
                    port.write('json-not-received'.encode('utf-8'))
        except Exception as e:
            print("things broke. but caught. looping again...")
            print(e)
            continue
    if not done:
        print(f"\t[+] {time.strftime('%X %x %Z')} Badge sync timed out. job done")
        GPIO.output(18, GPIO.LOW)


def validate_missing_keys(data):
    for i in expected_keys:
        if not i in data:
            return False
    return True


def validate_null_keys(data):
    for key, value in data.items():
        if value is None or value == "null" or value == '':
            return False
    return True

def validate_machine_id(data):
    try:
        #pico machine_id is 16 chars
        if len(data["machine_id"]) == 16:
            #validate hexadecimal
            if int(data["machine_id"],16):
                return True
        else:
            return False
    except ValueError:
        return False
    
def validate_integer_values(data):
    for key, value in data.items():
        if key != "machine_id":
            if not isinstance(value, int):
                return False
    return True

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)