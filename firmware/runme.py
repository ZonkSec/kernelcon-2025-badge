from machine import Pin,Timer,PWM,unique_id,reset,UART
import tm1637
import time
from neopixel import NeoPixel
from buzzer_music import music
from time import sleep
import itertools
import random
import cryptolib
import json
import _thread
import deflate
import io
import os
import errno

def runme():
    global np
    global rgb_pin
    rgb_pin = Pin(3, Pin.OUT)
    np = NeoPixel(rgb_pin, 7)
    
    global tm
    global count
    tm = tm1637.TM1637(clk=Pin(5), dio=Pin(4))
    tm.write([0, 0, 0, 0])
    count = 1
    
    global start_pad
    global seg1_pad
    global seg2_pad
    global seg3_pad
    global seg4_pad
    global seg5_pad
    global seg6_pad
    global finish_pad
    global poleball_pad
    start_pad = Pin(16, Pin.IN, Pin.PULL_UP)
    seg1_pad = Pin(22, Pin.IN, Pin.PULL_UP)
    seg2_pad = Pin(21, Pin.IN, Pin.PULL_UP)
    seg3_pad = Pin(20, Pin.IN, Pin.PULL_UP)
    seg4_pad = Pin(19, Pin.IN, Pin.PULL_UP)
    seg5_pad = Pin(18, Pin.IN, Pin.PULL_UP)
    seg6_pad = Pin(17, Pin.IN, Pin.PULL_UP)
    finish_pad = Pin(26, Pin.IN, Pin.PULL_UP)
    poleball_pad = Pin(6, Pin.IN, Pin.PULL_UP)
    
    global mem_clear
    mem_clear = Pin(9, Pin.IN, Pin.PULL_UP)
    
    global pogo_detect
    pogo_detect = Pin(2, Pin.IN, Pin.PULL_DOWN)
    
    global custom_track
    global custom_end
    global custom_start
    global custom_detect
    custom_track = Pin(10, Pin.IN, Pin.PULL_UP)
    custom_end = Pin(11, Pin.IN, Pin.PULL_UP)
    custom_start = Pin(12, Pin.IN, Pin.PULL_UP)
    custom_detect = Pin(13, Pin.IN, Pin.PULL_DOWN)
    
    seg_safe_alphas = "acefgjlpuy"
    
    stay_out = "kernel{d117faf0ee59a79997d2c5bbde2a1d89}"

    global buzz_pin
    global buzzer
    buzz_pin = 28
    buzzer = PWM(buzz_pin)
    
    global skip_scroll
    skip_scroll = False
    
    preview_over = True
    led_preview_time  = time.time()

    global safe_lost_time
    global lost
    position = 0
    lost = False
    lost_time = 0
    safe_lost_time = 60
    difficulty = 0
    global idle
    global set_mode
    global set_mode_time
    idle = False
    led_mode = 0
    sound_mode = 0
    last = time.ticks_ms()
    z=0
    config_lifted = False
    
    global achievement_easy
    global achievement_norm
    global achievement_hard
    global achievement_react10
    global achievement_easy30
    global achievement_norm60
    global achievement_hard80
    global achievement_customtrack
    achievement_easy = 0
    achievement_norm = 0
    achievement_hard = 0
    achievement_react10 = 0
    achievement_easy30 = 0
    achievement_norm60 = 0
    achievement_hard80 = 0
    achievement_customtrack = 0
    
    global hs_easy
    global hs_norm
    global hs_hard
    global hs_react
    hs_easy = 1000
    hs_norm = 1000
    hs_hard = 1000
    hs_react = 1000
    
    global deep_qa_pass
    global deep_easy_hs
    global deep_easy_win_count
    global deep_easy_fail_count
    global deep_norm_hs
    global deep_norm_win_count
    global deep_norm_fail_count
    global deep_hard_hs
    global deep_hard_win_count
    global deep_hard_fail_count
    deep_qa_pass = 0
    deep_easy_hs = 1000
    deep_easy_win_count = 0
    deep_easy_fail_count = 0
    deep_norm_hs = 1000
    deep_norm_win_count = 0
    deep_norm_fail_count = 0
    deep_hard_hs = 1000
    deep_hard_win_count = 0
    deep_hard_fail_count = 0
    

    
    #### mess of shit to help with LED patterns ####
    global colors
    segloop = [0b0100000,0b0010000,0b0001000,0b0000100,0b0000010,0b0000001]
    segloop_iter = itertools.cycle(segloop)
    bigsegloop = [[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1],[0,0,0,2],[0,0,0,4],[0,0,0,8],[0,0,8,0],[0,8,0,0],[8,0,0,0],[16,0,0,0],[32,0,0,0]]
    colors = [(80, 0, 0),(80, 40, 0),(80, 80, 0),(40, 80, 0),(0, 80, 0),(0,80,40),(0,80,80),(0,40,80),(0,0,80),(40,0,80),(80,0,80),(80,0,40)]
    colors_iter = itertools.cycle(colors)
    red_count = 0
    red_list = [0,5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,75,70,65,60,55,50,45,40,35,30,25,20,15,10,5]
    fig8segloop=[[32,0,0,0],[16,0,0,0],[8,0,0,0],[0,16,0,0],[0,32,0,0],[0,1,0,0],[0,0,32,0],[0,0,16,0],[0,0,8,0],[0,0,0,16],[0,0,0,32],[0,0,0,1],[0,0,0,2],[0,0,0,4],[0,0,0,8],[0,0,4,0],[0,0,2,0],[0,0,1,0],[0,2,0,0],[0,4,0,0],[0,8,0,0],[4,0,0,0],[2,0,0,0],[1,0,0,0]]
    fig8segloop_iter = itertools.cycle(fig8segloop)
    wallsegloop = [[48, 0, 0, 0], [6, 0, 0, 0], [0, 48, 0, 0], [0, 6, 0, 0], [0, 0, 48, 0], [0, 0, 6, 0], [0, 0, 0, 48], [0, 0, 0, 6], [0, 0, 0, 48], [0, 0, 6, 0], [0, 0, 48, 0], [0, 6, 0, 0], [0, 48, 0, 0], [6, 0, 0, 0]]
    wallsegloop_iter = itertools.cycle(wallsegloop)
    doublewallsegloop = [[48, 0, 0, 6],[6, 0, 0, 48], [0, 48, 6, 0], [0, 6, 48, 0], [0, 48, 6, 0], [6, 0, 0, 48]]
    doublewallsegloop_iter = itertools.cycle(doublewallsegloop)
    a = [0,1,2,1]
    a_iter= itertools.cycle(a)
    b = [5,4,3,4]
    b_iter= itertools.cycle(b)
    wavecount = 0

    try:
        f = open('data.txt', 'rb')
        settings = decrypt(f.read()).decode('utf-8').strip()
        j = json.loads(settings)
        print("loaded data")
        #print("loaded:" + str(j))
        difficulty = int(j['difficulty'])
        led_mode = int(j['led_mode'])
        sound_mode = int(j['sound'])
        achievement_easy = int(j['achievement_easy'])
        achievement_norm = int(j['achievement_norm'])
        achievement_hard = int(j['achievement_hard'])
        hs_easy = int(j['hs_easy'])
        hs_norm = int(j['hs_norm'])
        hs_hard = int(j['hs_hard'])
        hs_react = int(j['hs_react'])
        achievement_easy30 = int(j['achievement_easy30'])
        achievement_norm60 = int(j['achievement_norm60'])
        achievement_hard80 = int(j['achievement_hard80'])
        achievement_react10 = int(j['achievement_react10'])
        achievement_customtrack = int(j['achievement_customtrack'])

        deep_qa_pass = int(j['deep_qa_pass'])
        deep_easy_hs = int(j['deep_easy_hs'])
        deep_easy_win_count = int(j['deep_easy_win_count'])
        deep_easy_fail_count = int(j['deep_easy_fail_count'])
        deep_norm_hs = int(j['deep_norm_hs'])
        deep_norm_win_count = int(j['deep_norm_win_count'])
        deep_norm_fail_count = int(j['deep_norm_fail_count'])
        deep_hard_hs = int(j['deep_hard_hs'])
        deep_hard_win_count = int(j['deep_hard_win_count'])
        deep_hard_fail_count = int(j['deep_hard_fail_count'])
        
        f.close()
        
        if sound_mode == 1:
            buzz_pin = 8
            buzzer = PWM(buzz_pin)
        
    except:
        print("no data or invalid data. creating")
        f = open('data.txt', 'wb')
        data = {"sound":0,
                "difficulty":0,
                "led_mode":0,
                "achievement_easy":0,
                "achievement_norm":0,
                "achievement_hard":0,
                "achievement_react10":0,
                "hs_easy":1000,
                "hs_norm":1000,
                "hs_hard":1000,
                "hs_react":1000,
                "achievement_easy30": 0,
                "achievement_norm60":0,
                "achievement_hard80": 0,
                "achievement_customtrack" : 0,
                "deep_qa_pass" : 0,
                "deep_easy_hs" : 1000,
                "deep_easy_win_count" : 0,
                "deep_easy_fail_count" : 0,
                "deep_norm_hs" : 1000,
                "deep_norm_win_count" : 0,
                "deep_norm_fail_count" : 0,
                "deep_hard_hs" : 1000,
                "deep_hard_win_count" : 0,
                "deep_hard_fail_count" : 0,
                }
        f.write(encrypt(json.dumps(data)))
        
        f.close()
        
    if deep_qa_pass == 0:
        run_qa()
    
    boot_sequence()
    
    #set difficulty and display after boot
    set_mode = True
    set_mode_time = time.time()

    if difficulty == 0:
        tm.show("easy")
        safe_lost_time = 500
    if difficulty == 1:
        tm.show("norm")
        safe_lost_time = 60
    if difficulty == 2:
        tm.show("hard")
        safe_lost_time = 30

    
    
    ######## LOOPSTART ###########
    global idle_detect
    global inside_conf
    inside_conf = False
    idle_detect = time.time()
    while True:
        interrupted()
        
        #### check for pogo and enter serial if needed#####
        if pogo_detect.value() == 1:
            data_to_send = {
                "machine_id": unique_id().hex(),
                "deep_qa_pass" : deep_qa_pass,
                "deep_easy_hs" : deep_easy_hs,
                "deep_easy_win_count" : deep_easy_win_count,
                "deep_easy_fail_count" : deep_easy_fail_count,
                "deep_norm_hs" : deep_norm_hs,
                "deep_norm_win_count" : deep_norm_win_count,
                "deep_norm_fail_count" : deep_norm_fail_count,
                "deep_hard_hs" : deep_hard_hs,
                "deep_hard_win_count" : deep_hard_win_count,
                "deep_hard_fail_count" : deep_hard_fail_count,
                }
            
            #print(data_to_send)
            
            #blank out leds and note sync mode
            np.fill((0,0,0))
            np.write()
            tm.show("sync")
            
            sleep(2)
            try:
                uart = UART(0, baudrate=115200, timeout=500)
                sleep(.1)
            
                uart.write(json.dumps(data_to_send))
                print("sent json")

                #read ack
                line = uart.readline()
                if line:
                    print(line)
                    decoded_line = line.decode('utf-8')
                    if decoded_line == 'json-validated':
                        #wait for kiosk - loop here
                        print("success loop")
                        while True:
                            sleep(1)
                            if pogo_detect.value() == 0:
                                tm.show("done")
                                global buzz_pin
                                pokeheal = music('13 G#5 3 43;0 B5 4 43;5 B5 4 43;10 B5 2 43;16 E6 4 43', pins=[Pin(buzz_pin)])
                                buzz_count = 0
                                knight = [0,1,2,3,4,5,4,3,2,1]
                                knight_iter = itertools.cycle(knight)
                                while buzz_count < 55:
                                    pokeheal.tick()
                                    sleep(0.025)
                                    np.fill((0,0,0))
                                    np[next(knight_iter)] = (0,100,0)
                                    np.write()
                                    buzz_count=buzz_count+1
                                pokeheal.stop()
                                np.fill((0,0,0))
                                np.write()
                                sleep(1)
                                tm.write([0,0,0,0])
                                os.dupterm(None)
                                f.close()
                                break
                    else:
                        raise RuntimeError(decoded_line)
                    
                else:
                    raise RuntimeError("kiosk didn't receive json")

            except Exception as e:
                print(e)
                tm.show("fail")
                sleep(2)
                tm.write([0,0,0,0])
                continue

        #### if memclear held, delete data.txt ###
        if mem_clear.value() == 0:
            clear_memory()
        
        #### enter or exit config mode ###
        if poleball_pad.value() == 0 and config_lifted == True:
            config_lifted = False
            idle_detect = time.time()
            time.sleep_ms(250)
            if poleball_pad.value() == 0:
                time.sleep_ms(250)
                if poleball_pad.value() == 0:
                    inside_conf = not inside_conf
                    if inside_conf:
                        tm.show("conf")
                        buzz(tone=200,length=0.1)
                        buzz(tone=500,length=0.2)
                    else:
                        tm.show("exit")
                        buzz(tone=500,length=0.1)
                        buzz(tone=200,length=0.2)
                        sleep(.5)
                        tm.write([0,0,0,0])
                    debounce()
                    idle_detect = time.time()
        elif poleball_pad.value() == 1:
            config_lifted = True
        
        #### CHANGE DIFFICULTY ####
        if seg5_pad.value() == 0 and inside_conf:
            np.fill((0,0,0))
            np.write()
            idle_detect = time.time()
            set_mode = True
            set_mode_time = time.time()
            buzz(tone=500,length=0.1)
            difficulty=(difficulty+1)%3
            if difficulty == 0:
                tm.show("easy")
                safe_lost_time = 500
            if difficulty == 1:
                tm.show("norm")
                safe_lost_time = 60
            if difficulty == 2:
                tm.show("hard")
                safe_lost_time = 30
            debounce()
        
        #### CHANGE IDLE LED #####        
        if seg1_pad.value() == 0 and inside_conf:
            idle_detect = idle_detect-10
            set_mode = True
            set_mode_time = time.time()
            buzz(tone=500,length=0.1)
            led_mode = (led_mode+1)% (1 + achievement_easy + achievement_norm + achievement_hard + achievement_react10 + achievement_easy30 + achievement_norm60 + achievement_hard80 + achievement_customtrack)
            led_mode_name_list = ["L  1","L  2","L  3","L  4","L  5","L  6","L  7","L  8","L  9"]
            tm.show(led_mode_name_list[led_mode])
            led_preview_time = time.time()
            debounce(0.5)
        
        #### RUN CUSTOM TRACK RACE #####  
        if custom_detect.value() == 1 and not inside_conf:
            tm.scroll("bonus track")
            run_custom_race()
        
        #### ENTER SYNTH MODE #####        
        if seg6_pad.value() == 0 and not inside_conf:
            buzz(tone=500,length=0.1)
            synth_mode()
        
        #### show flags  #####        
        if seg4_pad.value() == 0 and inside_conf:
            buzz(tone=500,length=0.1)
            debounce()
            seg4_pad.irq(trigger=Pin.IRQ_FALLING,handler=interruption_handler)
            if achievement_easy == 0 and achievement_norm == 0 and achievement_hard == 0 and achievement_react10 == 0 and achievement_easy30 == 0 and achievement_norm60 == 0 and achievement_hard80 ==0 and achievement_customtrack==0:
                skipable_scroll("no flags yet")
            else:
                skipable_scroll(str(achievement_easy + achievement_norm + achievement_hard + achievement_react10 + achievement_easy30 +achievement_norm60 + achievement_hard80 + achievement_customtrack)+ " flags")
            if achievement_easy == 1:
                skipable_scroll(deflate.DeflateIO(io.BytesIO(b'\x78\x9c\x05\x80\xbb\x09\x00\x20\x0c\x44\x57\x71\x05\x3f\x07\x3a\x8e\xc5\x61\x93\x42\x10\x8b\xb7\x7d\xf0\x7e\x14\x14\x63\x55\x5f\xc1\xef\xed\xcc\x48\x56\xe7\x07\x6c'), deflate.ZLIB).read().decode())
            if achievement_norm == 1:
                skipable_scroll(deflate.DeflateIO(io.BytesIO(b'\x78\x9c\x05\x40\x41\x0a\x00\x10\x00\xfb\x8a\x47\x2c\xec\x39\x72\x5b\x43\x29\x07\xbf\x5f\xfb\xdc\x55\x1e\x7e\xb7\x39\x2d\x0d\xd5\x06\x06\x5c\x65\x07\x90'), deflate.ZLIB).read().decode())
            if achievement_hard == 1:
                skipable_scroll(deflate.DeflateIO(io.BytesIO(b'\x78\x9c\x05\x40\x51\x0a\x00\x10\x14\xbb\x8a\x33\xc8\xe2\x1d\x67\x21\x5a\xef\x43\xee\xff\xb1\x2e\xff\x2a\x3d\xc7\xd1\x26\x84\x37\x6b\x64\x33\x4e\xa5\x06\xe4'), deflate.ZLIB).read().decode())
            if achievement_react10 == 1:
                skipable_scroll(deflate.DeflateIO(io.BytesIO(b'\x78\x9c\x05\x40\x51\x0a\x00\x10\x14\xbb\x8a\x23\x58\x99\x72\x9c\xd7\xe2\x95\x2f\xc9\x8f\xdb\xaf\x3b\x43\x0f\xb5\x8c\x2e\x62\x9d\xfc\x60\xa4\xd8\xb6\x01\x67\x8d\x07\xe3'), deflate.ZLIB).read().decode())
            if achievement_easy30 == 1:
                skipable_scroll(deflate.DeflateIO(io.BytesIO(b'\x78\x9c\x05\x40\xb1\x09\x00\x20\x0c\x7b\xc5\x13\x62\xac\xd1\x77\xa4\x74\x73\x28\x38\xf9\x7d\x89\xf3\xfe\x40\xeb\x57\x2b\x34\x8d\xb0\xed\xcc\x44\x01\x57\x1c\x06\xb7'), deflate.ZLIB).read().decode())
            if achievement_norm60 == 1:
                skipable_scroll(deflate.DeflateIO(io.BytesIO(b'\x78\x9c\x05\x40\x6d\x06\x00\x20\x14\xbb\x4a\x47\x98\xe8\x75\x9e\x24\x8f\xd1\x87\xfe\xed\xf6\x73\xee\xdf\x81\x32\xab\xb2\xb7\xc7\x64\x48\x1c\x58\x06\x66\xf9\x08\x57'), deflate.ZLIB).read().decode())
            if achievement_hard80 == 1:
                skipable_scroll(deflate.DeflateIO(io.BytesIO(b'\x78\x9c\x05\x40\xb1\x09\x00\x20\x0c\x7b\xc5\x13\x22\x38\xa4\xe7\x04\xb4\x48\x47\x21\x83\xdf\x97\xab\xb7\x89\x51\x4a\x1e\x54\x68\xfd\xb0\x39\x1b\x5a\x7e\x07\x63'), deflate.ZLIB).read().decode())
            if achievement_customtrack == 1:
                skipable_scroll(deflate.DeflateIO(io.BytesIO(b'\x78\x9c\x05\x40\x89\x09\x00\x20\x08\x5c\xa5\x19\xe2\xca\x79\xe2\x08\xa1\x87\xa4\x6c\x7f\xe1\x7f\x7e\xb6\xdf\xc6\x99\x86\x55\xe1\x62\x2f\x19\xa2\xa6\x08\x9b\x42\x09\xf3'), deflate.ZLIB).read().decode())
            seg4_pad.irq(handler=None)
            idle_detect = time.time()
            if inside_conf:
                tm.show("conf")
                
            
        #### ENTER REACTION TEST MODE #####        
        if finish_pad.value() == 0 and not inside_conf:
            buzz(tone=500,length=0.1)
            reaction_test()
            
        #### CHANGE SOUND MODE #####        
        if seg3_pad.value() == 0 and inside_conf:
            sound_mode = (sound_mode+1)%2
            if sound_mode == 0:
                tm.show("S ON")
                buzz_pin = 28
                buzzer = PWM(buzz_pin)
            if sound_mode == 1:
                tm.show("SOFF")
                buzz_pin = 8
                buzzer = PWM(buzz_pin)
            np.fill((0,0,0))
            buzz(tone=500,length=0.1)
            np.write()
            idle_detect = time.time()
            set_mode = True
            set_mode_time = time.time()
            debounce()
        
        #show high scores
        if seg2_pad.value() == 0 and inside_conf:
            buzz(tone=500,length=0.1)
            seg2_pad.irq(trigger=Pin.IRQ_FALLING,handler=interruption_handler)
            skipable_scroll("high scores",200)
            skipable_scroll("easy " + str(hs_easy),200)
            skipable_scroll("norm " + str(hs_norm),200)
            skipable_scroll("hard " + str(hs_hard),200)
            skipable_scroll("react " + str(hs_react),200)
            
            seg2_pad.irq(handler=None)
            idle_detect = time.time()
            
            if inside_conf:
                tm.show("conf")
                
                
        
        #### BEGIN RACE ####
        if start_pad.value() == 0 and not inside_conf:
            tm.write([0,0,0,0])
            run_race()

        #### if no input, do idle mode stuff #####
        else:
            if set_mode and time.time() - set_mode_time > 1:
                if inside_conf:
                    tm.show("conf")
                else:
                    tm.write([0, 0, 0, 0])
                f = open('data.txt', 'wb')
                data = {"sound":sound_mode,
                        "difficulty":difficulty,
                        "led_mode":led_mode,
                        "achievement_easy":achievement_easy,
                        "achievement_norm":achievement_norm,
                        "achievement_hard":achievement_hard,
                        "achievement_react10":achievement_react10,
                        "hs_easy":hs_easy,
                        "hs_norm":hs_norm,
                        "hs_hard":hs_hard,
                        "hs_react":hs_react,
                        "achievement_easy30":achievement_easy30,
                        "achievement_norm60":achievement_norm60,
                        "achievement_hard80":achievement_hard80,
                        "achievement_customtrack" : achievement_customtrack,
                        "deep_qa_pass" : deep_qa_pass,
                        "deep_easy_hs" : deep_easy_hs,
                        "deep_easy_win_count" : deep_easy_win_count,
                        "deep_easy_fail_count" : deep_easy_fail_count,
                        "deep_norm_hs" : deep_norm_hs,
                        "deep_norm_win_count" : deep_norm_win_count,
                        "deep_norm_fail_count" : deep_norm_fail_count,
                        "deep_hard_hs" : deep_hard_hs,
                        "deep_hard_win_count" : deep_hard_win_count,
                        "deep_hard_fail_count" : deep_hard_fail_count,
                        }
                f.write(encrypt(json.dumps(data)))
                
                f.close()
                print("saved data")
                #print("saved: " + str(data))
                set_mode = False
            if time.time() - idle_detect > 5:
                idle = True
                pass
            else:
                idle = False
            
            if inside_conf and (time.time()-led_preview_time)>1:
                preview_over = True
            else:
                preview_over = False
            if idle and not preview_over:
                if led_mode == 0:
                     np.fill((80,0,0))
                     np.write()
                if led_mode == 1:
                     np.fill((0,80,0))
                     np.write()
                if led_mode == 2:
                    np[0] = colors[0]
                    np[1] = colors[1]
                    np[2] = colors[2]
                    np[3] = colors[4]
                    np[4] = colors[6]
                    np[5] = colors[8]
                    np[6] = colors[11]
                    np.write()
                if led_mode == 3:
                    knight = [0,1,2,3,4,5,4,3,2,1]
                    for i in knight:
                        if interrupted(): break
                        np.fill((0,0,0))
                        np[i] = (100,0,0)
                        np.write()
                        sleep(.1)
                if led_mode == 4:
                    np.fill((0,0,0))
                    for j in range(255):
                        if interrupted(): break
                        tm.write(bigsegloop[z])
                        if time.ticks_diff(time.ticks_ms(), last) > 100:
                            z = (z + 1)%11
                            last = time.ticks_ms()
                        rc_index = (6 * 256 // 7) + j
                        np[6] = wheel(rc_index & 255)
                        np[6] = (int(np[6][0]/4),int(np[6][1]/4),int(np[6][2]/4))
                        np.write()
                if led_mode == 5:
                    np.fill((red_list[red_count],0,0))
                    np.write()
                    if time.ticks_diff(time.ticks_ms(), last) > 100:
                        tm.write(next(fig8segloop_iter))
                        red_count = (red_count+1)%(len(red_list))
                        last = time.ticks_ms()
                if led_mode == 6:
                    if wavecount == 0:
                        c = next(colors_iter)
                        c = next(colors_iter)
                    if wavecount%4 ==0:
                            tm.write(next(doublewallsegloop_iter))
                            last = time.ticks_ms()
                    if wavecount%6 ==0:
                            np.fill((0,0,0))
                            last2 = time.ticks_ms()
                            np[next(a_iter)] = c
                            np[next(b_iter)] = c
                            np.write()
                    wavecount=(wavecount+1)%24
                    sleep(.02)
                if led_mode == 7:
                    np[0] = colors[z%len(colors)]
                    np[1] = colors[(z+1)%len(colors)]
                    np[2] = colors[(z+2)%len(colors)]
                    np[3] = colors[(z+3)%len(colors)]
                    np[4] = colors[(z+4)%len(colors)]
                    np[5] = colors[(z+5)%len(colors)]
                    np.write()
                    if time.ticks_diff(time.ticks_ms(), last) > 200:
                        z = (z + 1)%len(colors)
                        tm.write(next(wallsegloop_iter))
                        last = time.ticks_ms()
                if led_mode == 8:
                    if interrupted(): break
                    for j in range(255):
                        if interrupted(): break
                        if time.ticks_diff(time.ticks_ms(), last) > 100:
                            if interrupted(): break
                            tm.write([segloop[z%6],segloop[(z+1)%6],segloop[(z+2)%6],segloop[(z+3)%6]])
                            z = (z + 1)%6
                            last = time.ticks_ms()
                        for i in range(7):
                            if interrupted(): break
                            rc_index = (i * 256 // 7) + j
                            np[i] = wheel(rc_index & 255)
                            np[i] = (int(np[i][0]/4),int(np[i][1]/4),int(np[i][2]/4))
                        np.write()
                     
            else:
                np.fill((0,0,0))
                np.write()

    
def skipable_scroll(string, delay=250):
    global tm
    global skip_scroll
    segments = string if isinstance(string, list) else tm.encode_string(string)
    data = [0] * 8
    data[4:0] = list(segments)
    for i in range(len(segments) + 5):
        if skip_scroll:
            tm.write([0, 0, 0, 0])
            skip_scroll = False
            break
        tm.write(data[0+i:4+i])
        time.sleep_ms(delay)
    debounce()
               
def interruption_handler(pin):
    global skip_scroll
    buzz(tone=500,length=0.025)
    skip_scroll = True

def clear_memory():
    np.fill((0,0,0))
    np.write()
    tm.scroll("hold to clear mem")
    hal_death = music('0 G5 3.3333332538604736 16;12 G4 3.3333332538604736 16;8 C5 3.3333332538604736 16;4 E5 3.3333332538604736 16;16 A4 0.6666666865348816 16;18.66666603088379 C5 0.6666666865348816 16;17.33333396911621 B4 0.6666666865348816 16;20 A4 2.6666667461395264 16;22.66666603088379 C5 0.6666666865348816 16;24 G4 8 16;32 D5 3.3333332538604736 16;36 G5 3.3333332538604736 16;40 E5 3.3333332538604736 16;44 C5 3.3333332538604736 16;49.33333206176758 B4 0.6666666865348816 16;50.66666793823242 C5 0.6666666865348816 16;48 A4 0.6666666865348816 16;54.66666793823242 E5 0.6666666865348816 16;56 D5 6 16;52 D5 2.6666667461395264 16', pins=[Pin(buzz_pin)])
    count = 0;
    sleep_len = 0.08
    tm.show("hold")
    while count < 190:
        if mem_clear.value() == 1:
            hal_death.stop()
            tm.write([0, 0, 0, 0])
            return
        hal_death.tick()
        sleep(sleep_len)
        if count > 100:
            sleep_len = sleep_len + 0.002
        count=count+1
    hal_death.stop()
    
    f = open('data.txt', 'rb')
    settings = decrypt(f.read()).decode('utf-8').strip()
    j = json.loads(settings)
    f.close()
    
    for e in j:
        if "deep" not in e:
            if e in ["hs_easy","hs_norm","hs_hard","hs_react"]:
                j[e] = 1000
            else:
                j[e] = 0
            
    print("mem cleared. writing")
    print(j)
    f = open('data.txt', 'wb')
    f.write(encrypt(json.dumps(j)))
    f.close()
    
    tm.scroll("mem cleared")
    reset()

def reaction_test():
    tm.scroll("react test",150)
    np.fill((0,0,0))
    np[0] = (127,100,0)
    np.write()
    
    _thread.start_new_thread(buzz,(500,0.2))
    sleep(.3)
    np[1] = (127,100,0)
    np.write()
    _thread.start_new_thread(buzz,(500,0.2))
    sleep(.3)
    np[2] = (127,100,0)
    np.write()
    _thread.start_new_thread(buzz,(500,0.2))
    sleep(.3)
    np.fill((0,80,0))
    np.write()
    _thread.start_new_thread(buzz,(1000,0.2))
    if start_pad.value() == 0  or seg1_pad.value() == 0  or seg2_pad.value() == 0  or seg3_pad.value() == 0  or seg4_pad.value() == 0  or seg5_pad.value() == 0  or seg6_pad.value() == 0  or finish_pad.value() == 0:
        np.fill((80,0,0))
        np.write()
        tm.scroll("false start",150)
        global idle_detect
        idle_detect = time.time()
        return
    start = time.ticks_ms()
    while True:
        if start_pad.value() == 0  or seg1_pad.value() == 0  or seg2_pad.value() == 0  or seg3_pad.value() == 0  or seg4_pad.value() == 0  or seg5_pad.value() == 0  or seg6_pad.value() == 0  or finish_pad.value() == 0:
            duration = time.ticks_diff(time.ticks_ms(), start)
            np.fill((0,0,0))
            np.write()
            tm.scroll(str(duration))
            global hs_react
            if duration < hs_react:
                hs_react = duration
                new_hs()
            global achievement_react10
            if duration < 10 and achievement_react10 == 0:
                achievement_react10 = 1
                unlock()
            global idle_detect
            idle_detect = time.time()
            break
        elif time.ticks_diff(time.ticks_ms(), start) > 2000:
            tm.scroll("too slow")
            global idle_detect
            idle_detect = time.time()
            break
    
    
def decrypt(ciphertext):
    return ciphertext

def encrypt(plaintext):
    return plaintext
    
    
def synth_mode():
    tm.show("synth")
    buffer = ""
    nothing_touched_last = True
    m = deflate.DeflateIO(io.BytesIO(b'\x78\x9c\x55\xc9\xc1\x0d\x00\x40\x14\x41\xc1\xa6\x74\xb0\x64\xfb\xef\x88\x70\xfa\x99\xb8\x78\x02\xf1\x32\x15\x4b\xf8\x71\xcb\xda\x3e\x03\x45\x9f\x0c\x3f'), deflate.ZLIB).read().decode()
    j = deflate.DeflateIO(io.BytesIO(b'\x78\x9c\x4d\xc6\x41\x0d\x00\x00\x08\x03\x31\x53\x37\x03\x2c\x01\xff\x8e\x06\x3f\x3e\x4d\xad\xc2\x1a\x7a\xfd\xbb\x07\x5f\xe8\x06\x93'), deflate.ZLIB).read().decode()
    p = deflate.DeflateIO(io.BytesIO(b'\x78\x9c\x35\xc6\x41\x09\x00\x00\x08\x04\xc1\x52\x5b\x40\x44\xb6\x7f\xa3\xbb\x8f\x8f\x81\x11\x99\x3a\xb6\xfe\x01\x3c\x52\x05\x34'), deflate.ZLIB).read().decode()
    while True:
        if poleball_pad.value() == 0:
            tm.write([0,0,0,0])
            return
        if start_pad.value() == 0:
            np.fill((50,0,0))
            np.write()
            buzz(tone=262,length=0.1) #C4
            np.fill((0,0,0))
            np.write()
            if nothing_touched_last:
                buffer += "C4"
                nothing_touched_last = False
        elif seg1_pad.value() == 0:
            np.fill((0,50,0))
            np.write()
            buzz(tone=294,length=0.1) #D4
            np.fill((0,0,0))
            np.write()
            if nothing_touched_last:
                buffer += "D4"
                nothing_touched_last = False
        elif seg2_pad.value() == 0:
            np.fill((0,0,50))
            np.write()
            buzz(tone=330,length=0.1) #E4
            np.fill((0,0,0))
            np.write()
            if nothing_touched_last:
                buffer += "E4"
                nothing_touched_last = False
        elif seg3_pad.value() == 0:
            np.fill((50,50,0))
            np.write()
            buzz(tone=349,length=0.1) #F4
            np.fill((0,0,0))
            np.write()
            if nothing_touched_last:
                buffer += "F4"
                nothing_touched_last = False
        elif seg4_pad.value() == 0:
            np.fill((50,0,50))
            np.write()
            buzz(tone=392,length=0.1) #G4
            np.fill((0,0,0))
            np.write()
            if nothing_touched_last:
                buffer += "G4"
                nothing_touched_last = False
        elif seg5_pad.value() == 0:
            np.fill((50,50,50))
            np.write()
            buzz(tone=440,length=0.1) #A4
            np.fill((0,0,0))
            np.write()
            if nothing_touched_last:
                buffer += "A4"
                nothing_touched_last = False
        elif seg6_pad.value() == 0:
            np.fill((50,0,50))
            np.write()
            buzz(tone=494,length=0.1) #B4
            np.fill((0,0,0))
            np.write()
            if nothing_touched_last:
                buffer += "B4"
                nothing_touched_last = False
        elif finish_pad.value() == 0:
            np.fill((0,50,50))
            np.write()
            buzz(tone=523,length=0.1) #C5
            np.fill((0,0,0))
            np.write()
            if nothing_touched_last:
                buffer += "C5"
                nothing_touched_last = False
        else:
            nothing_touched_last = True
        
        if len(buffer) > 52:
            buffer = buffer[1:]
        if buffer == m:
            skipable_scroll(deflate.DeflateIO(io.BytesIO(b'\x78\x9c\x25\xc2\xb1\x09\x00\x20\x0c\x44\xd1\x55\x32\x82\x20\x09\x66\x9c\x13\xa2\x8d\xc5\xdf\xbf\x4a\x21\xbc\xf3\x74\x6d\x4b\x9f\xad\x91\x95\x02\xa6\x53\x84\x37\xa9\xbb\x0a\x4f'), deflate.ZLIB).read().decode())
            break
        elif buffer[-28:] == j:
            skipable_scroll(deflate.DeflateIO(io.BytesIO(b'\x78\x9c\x05\x40\xdb\x09\x00\x20\x08\x5c\xe5\x66\x10\x7a\x8d\x13\x86\x62\x49\x05\x7d\xb5\xbd\x88\x77\xc5\x33\x5f\x1f\xc3\xf6\x01\x13\xeb\xbc\x9a\x5b\xa9\x42\xc2\x29\x00\xbc\xfe\x0a\xe5'), deflate.ZLIB).read().decode())
            break
        elif buffer[-22:] == p:
            skipable_scroll(deflate.DeflateIO(io.BytesIO(b'\x78\x9c\x05\x40\xc1\x09\x00\x31\x08\x5b\xc5\x11\xc4\x8f\xf3\xf8\x48\x8e\x1e\xa1\xe4\xd3\xfd\x85\x9a\x2f\x7c\x2e\xc6\x16\xa2\xd9\x7f\x39\x4b\x44\x1a\x8f\x0b\xb1\x99\x0a\xf2'), deflate.ZLIB).read().decode())
            break

def print_time(timer):
    global count
    tm.number(count)
    count += 1
    
def race_win():
        global tim
        global tm
        global count
        global level

        tim.deinit()
        
        win1 = music('0 D5 1 10;3 D5 1 10;6 E5 1 10;7 F5 1 10;8 D5 1 10;12 C5 1 10;16 C5 1 10;20 A4 1 10;24 B4 1 10;0 D5 2 46;3 D5 2 46;6 E5 1 46;7 F5 1 46;8 D5 3 46;12 C5 4 46;16 C5 4 46;20 A4 4 46;24 B4 4 46;0 D5 1 12;3 D5 1 12;6 E5 1 12;7 F5 1 12;8 D5 1 12;12 C5 1 12;16 C5 1 12;20 A4 1 12;24 B4 1 12;0 D5 1 11;3 D5 1 11;6 E5 1 11;7 F5 1 11;8 D5 1 11;12 C5 1 11;16 C5 1 11;20 A4 1 11;24 B4 1 11;3 D5 1 10;6 E5 1 10;7 F5 1 10;8 D5 1 10;12 C5 1 10;16 C5 1 10;20 A4 1 10;24 B4 1 10;20 A4 1 9;24 B4 1 9;0 D5 2 50;6 E5 1 50;7 F5 1 50;8 D5 4 50;12 C5 3 50;16 C5 4 50;20 A4 4 50;24 B4 8 50;32 D5 1 10;35 D5 1 10;38 E5 1 10;39 F5 1 10;40 D5 1 10;44 C5 1 10;48 C5 1 10;52 F5 1 10;56 G5 1 10;32 D5 1 11;35 D5 1 11;38 E5 1 11;39 F5 1 11;40 D5 1 11;44 C5 1 11;48 C5 1 11;52 F5 1 11;56 G5 1 11;32 D5 1 12;35 D5 1 12;38 E5 1 12;39 F5 1 12;40 D5 1 12;44 C5 1 12;48 C5 1 12;52 F5 1 12;56 G5 1 12;32 D5 2 50;38 E5 1 50;39 F5 1 50;40 D5 4 50;44 C5 3 50;48 C5 4 50;56 G5 8 50;52 F5 4 50;3 D5 3 50;35 D5 3 50', pins=[Pin(buzz_pin)])
        win2 = music('8 E5 1 16;10 F5 1 16;12 E5 3 16;16 C5 4 16;22 A4 1 16;24 D5 4 16;28 A4 8 16;38 C5 1 16;40 F5 7 16;48 G5 2 16;50 A5 2 16;52 C6 4 16;56 A5 4 16;62.079986572265625 D5 1 16;63.25 E5 1 16;64.42001342773438 D5 9 16;0 F5 7 16', pins=[Pin(buzz_pin)])
        win3 = music('0 C#6 1 0;2 C#6 1 0;4 C#6 1 0;12 A5 2 0;18 B5 2 0;24 C#6 2 0;28 B5 1 0;30 C#6 4 0;6 C#6 2 0', pins=[Pin(buzz_pin)])
        win4 = music('0 G5 1 16;1 F#5 1 16;2 D5 1 16;3 B4 1 16;4 G5 1 16;5 F#5 1 16;6 D5 1 16;7 B4 1 16;8 G5 1 16;9 F#5 1 16;10 D5 1 16;11 B4 1 16;12 G5 1 16;13 F#5 1 16;14 D5 1 16;15 B4 1 16;16 G5 1 16;17 F#5 1 16;18 D5 1 16;19 B4 1 16;20 G5 1 16;21 F#5 1 16;22 D5 1 16;23 B4 1 16;24 G5 1 16;25 F#5 1 16;26 D5 1 16;27 B4 1 16;28 G5 1 16;29 F#5 1 16;30 D5 1 16;31 B4 1 16;32 A5 1 16;33 G5 1 16;34 E5 1 16;35 C5 1 16;36 A5 1 16;37 G5 1 16;38 E5 1 16;39 C5 1 16;40 A5 1 16;41 G5 1 16;42 E5 1 16;43 C5 1 16;44 A5 1 16;45 G5 1 16;46 E5 1 16;47 C5 1 16;48 A5 1 16;49 G5 1 16;50 D#5 1 16;51 C5 1 16;52 A5 1 16;53 G5 1 16;54 D#5 1 16;55 C5 1 16;56 A5 1 16;57 G5 1 16;58 D#5 1 16;59 C5 1 16;60 A5 1 16;61 G5 1 16;62 D#5 1 16;63 C5 1 16', pins=[Pin(buzz_pin)])
        win_selection = random.choice([(win1,180,0.035),(win2,220,0.025),(win3,110,0.022),(win4,192,0.03)])
        buzz_count = 0
        flipflop = 0 
        while buzz_count < win_selection[1]:
            win_selection[0].tick()
            sleep(win_selection[2])
            buzz_count=buzz_count+1
            
            flipflop = (flipflop+1)%11
            if flipflop < 5:
                tm.write([0, 0, 0, 0])
                np.fill((0,0,0))
                np[0] = (80,80,80)
                np[2] = (80,80,80)
                np[4] = (80,80,80)
                np[6] = (80,80,80)
                np.write()
            else:
                tm.number(count)
                np.fill((0,0,0))
                np[1] = (80,80,80)
                np[3] = (80,80,80)
                np[5] = (80,80,80)
                np.write()
        win_selection[0].stop()
        np.fill([0,0,0])
        np.write()
        
        
        #will unlock custom track flag if its a custom track
        if custom_detect.value() == 1:
            global achievement_customtrack
            if achievement_customtrack == 0:
                unlock()
                achievement_customtrack = 1
        #only record scores and sets records if it is not a custom track
        else:
            if safe_lost_time == 500:
                mode = "easy"
                
                global deep_easy_win_count
                deep_easy_win_count = deep_easy_win_count + 1
                
                #check for HS
                global hs_easy
                if count < hs_easy:
                    hs_easy = count
                    new_hs()
                global deep_easy_hs
                if count < deep_easy_hs:
                    deep_easy_hs = count

                #complete achivement if not already
                global achievement_easy
                if achievement_easy == 0:
                    unlock()
                    achievement_easy = 1
                #check the other achivement
                global achievement_easy30
                if achievement_easy30 == 0 and count <=30:
                    achievement_easy30 = 1
                    unlock()
            elif safe_lost_time == 60:
                mode = "normal"
                
                global deep_norm_win_count
                deep_norm_win_count = deep_norm_win_count + 1
                
                #check for HS
                global hs_norm
                if count < hs_norm:
                    hs_norm = count
                    new_hs()
                
                global deep_norm_hs
                if count < deep_norm_hs:
                    deep_norm_hs = count
                #complete achivement if not already
                global achievement_norm
                if achievement_norm == 0:
                    unlock()
                    achievement_norm = 1
                #check the other achivement
                global achievement_norm60
                if achievement_norm60 == 0 and count <=60:
                    achievement_norm60 = 1
                    unlock()
            elif safe_lost_time == 30:
                mode = "hard"
                
                global deep_hard_win_count
                deep_hard_win_count = deep_hard_win_count + 1
                
                #check for HS
                global hs_hard
                if count < hs_hard:
                    hs_hard = count
                    new_hs()
                    
                global deep_hard_hs
                if count < deep_hard_hs:
                    deep_hard_hs = count
                #complete achivement if not already
                global achievement_hard
                if achievement_hard == 0:
                    unlock()
                    achievement_hard = 1
                #check the other achivement
                global achievement_hard80
                if achievement_hard80 == 0 and count <=80:
                    achievement_hard80 = 1
                    unlock()
        
        count = 1
        global position
        global lost
        global lost_time
        position = 0
        lost = 0
        lost_time = 0
        
        global idle_detect
        idle_detect = time.time()
        

def unlock():
    buzz_count = 0
    _thread.start_new_thread(tm.scroll,("new led and flag unlocked",150))
    song = music('4 G#5 1 16;3 A5 1 16;7 C7 1 16;1 F#6 1 16;2 D#6 1 16;0 G6 1 16;5 E6 1 16;6 G#6 1 16', pins=[Pin(buzz_pin)])
    flip = False
    while buzz_count < 24:
        song.tick()
        if flip:
            np[buzz_count%6]=([0,0,0])
        else:
            np[buzz_count%6]=([127,60,0])
        if buzz_count%6 == 5:
            flip = not flip
        np.write()
        sleep(0.04)
        buzz_count=buzz_count+1
    song.stop()
    np.fill([0,0,0])
    np.write()
    sleep(5)
    global set_mode
    set_mode = True
    global set_mode_time
    set_mode_time = time.time()

def new_hs():
    z = 0
    last = time.ticks_ms()
    buzz_count = 0
    song = music('0 C5 1.3333333730697632 14;4 C5 1.3333333730697632 14;8 C5 8 14;16 C#5 1.3333333730697632 14;20 C#5 1.3333333730697632 14;24 C#5 8 14;32 D#5 1.3333333730697632 14;36 D#5 1.3333333730697632 14;40 D#5 4 14;44 F5 1.3333333730697632 14;45.33333206176758 F5 1.3333333730697632 14;46.66666793823242 F5 1.3333333730697632 14;48 G5 8 14;33.33333206176758 A#4 1.3333333730697632 14;37.33333206176758 A#4 1.3333333730697632 14;1.3333333730697632 G4 1.3333333730697632 14;5.333333492279053 G4 1.3333333730697632 14;17.33333396911621 G#4 1.3333333730697632 14;21.33333396911621 G#4 1.3333333730697632 14;34.66666793823242 G4 1.3333333730697632 14;2.6666667461395264 E4 1.3333333730697632 14;18.66666603088379 F4 1.3333333730697632 14;38.66666793823242 A#3 1.3333333730697632 14;22.66666603088379 G#3 1.3333333730697632 14;7 G3 1.3333333730697632 14;40 G4 4 14', pins=[Pin(buzz_pin)])
    _thread.start_new_thread(tm.scroll,("new high score",300))
    while buzz_count < 165:
        song.tick()
        sleep(0.04)
        buzz_count=buzz_count+1
        np[0] = colors[z%len(colors)]
        np[1] = colors[(z+1)%len(colors)]
        np[2] = colors[(z+2)%len(colors)]
        np[3] = colors[(z+3)%len(colors)]
        np[4] = colors[(z+4)%len(colors)]
        np[5] = colors[(z+5)%len(colors)]
        np[6] = (0,0,0)
        np.write()
        if time.ticks_diff(time.ticks_ms(), last) > 100:
            z = (z + 1)%len(colors)
            last = time.ticks_ms()
    song.stop()
    global set_mode
    set_mode = True
    global set_mode_time
    set_mode_time = time.time()
    np.fill([0,0,0])
    np.write()

def race_failed():
        global tim
        global tm
        global count
        tim.deinit()
        np.fill((127,0,0))
        np.write()
        
        fail1 = music('26 F4 6 14;0 A#4 2 14;4 F4 2 14;8 D4 3 14;11 G4 2 14;13 A4 2 14;15 G4 2 14;17 F#4 3 14;20 G#4 3 14;23 F#4 3 14;60 A#7 1 43;26 D4 1 14;27 C4 1 14;28 D4 4 14', pins=[Pin(buzz_pin)])
        fail2 = music('0 C4 1 15;2 C4 1 15;3 B3 1.5 15;9 A3 1.5 15;12 G#3 8 15;6 A#3 1.5 15', pins=[Pin(buzz_pin)])
        fail3 = music('0 C6 4 51;4 B5 4 51;8 A#5 4 51;12 A5 20 51', pins=[Pin(buzz_pin)])
        fail_selection = random.choice([(fail1,100),(fail2,61),(fail3,52)])
        buzz_count=0
        flipflop = 0
        while buzz_count < fail_selection[1]:
            fail_selection[0].tick()
            sleep(0.04)
            buzz_count=buzz_count+1
            
            flipflop = (flipflop+1)%11
            if flipflop < 5:
                tm.write([0, 0, 0, 0])
            else:
                tm.show("fail")
        fail_selection[0].stop()
        tm.write([0, 0, 0, 0])
        
        global deep_easy_fail_count
        global deep_norm_fail_count
        global deep_hard_fail_count
        
        if safe_lost_time == 500:
            mode = "easy"
            deep_easy_fail_count = deep_easy_fail_count + 1
        elif safe_lost_time == 60:
            mode = "normal"
            deep_norm_fail_count = deep_norm_fail_count + 1
        elif safe_lost_time == 30:
            mode = "hard"
            deep_hard_fail_count = deep_hard_fail_count + 1
        
        count = 1
        global position
        global lost
        global lost_time
        position = 0
        lost = 0
        lost_time = 0
        
        np.fill((0,0,0))
        np.write()
        global idle_detect
        idle_detect = time.time()
        global set_mode
        set_mode = True
        global set_mode_time
        set_mode_time = time.time()
        
def interrupted():
    r = False
    for x in [start_pad, seg1_pad, seg2_pad, seg3_pad, seg4_pad, seg5_pad, seg6_pad, finish_pad,poleball_pad]:
        if x.value() == 0:
            r = True
            if x != seg1_pad:
                global idle_detect
                idle_detect = time.time()
    return r

def boot_sequence():
    intro = music('0 A2 6 5 0.8976377844810486;6 A2 1 5 0.8976377844810486;7 B2 1 5 0.8976377844810486;8 C3 2 5 0.8976377844810486;10 B2 1 5 0.8976377844810486;11 A2 1 5 0.8976377844810486;12 G2 1 5 0.8976377844810486;13 A2 1 5 0.8976377844810486;14 B2 2 5 0.8976377844810486;16 E2 16 5 0.8976377844810486', pins=[Pin(buzz_pin)])
    string = random.choice(["lets race","hello world","hack the planet","ready set go","need 4 speed","stay on track"])
    segments = string if isinstance(string, list) else tm.encode_string(string)
    data = [0] * 8
    data[4:0] = list(segments)
    i = 0

    led_count = 0;
    color_pick = 0
    
    buzz_count = 0;
    sleep_delay = 0;
    while buzz_count < 80:
        intro.tick()
        sleep(0.06)
        buzz_count=buzz_count+1
        
        np.fill((0,0,0))
        if led_count == 6:
            color_pick=color_pick+1
            
        np[led_count] = colors[color_pick%len(colors)]
        np.write()
        led_count =(led_count+1)%7
        
        sleep_delay = sleep_delay + 1;
        if (sleep_delay%4 == 1):
            tm.write(data[0+i:4+i])
            i=i+1
    intro.stop()
    np.fill((0,0,0))
    np.write()
    
def buzz(tone,length):
    buzzer.freq(tone)
    buzzer.duty_u16(1000)
    sleep(length)
    buzzer.duty_u16(0)

def run_custom_race():
    global tim
    tim = Timer()
    lost = False
    while custom_detect.value() == 1:
        np.fill((0,0,0))
        np.write()
        if custom_start.value() == 0:
            np[0] = (127,100,0)
            np.write()
            _thread.start_new_thread(buzz,(500,0.4))
            time.sleep_ms(500)
            if custom_start.value() == 0:
                np[1] = (127,100,0)
                np.write()
                _thread.start_new_thread(buzz,(500,0.4))
                time.sleep_ms(500)
                if custom_start.value() == 0:
                    np[2] = (127,100,0)
                    np.write()
                    _thread.start_new_thread(buzz,(500,0.4))
                    time.sleep_ms(500)
                    if custom_start.value() == 0:
                        #race is started!
                        tim.init(period=100, mode=Timer.PERIODIC, callback=print_time)
                        np.fill((0,127,0))
                        np.write()
                        buzz(1000,0.4)
                        position = 0
                        while True:
                            if position == 0:
                                if custom_start.value() == 0:
                                    lost = False
                                elif custom_track.value() == 0:
                                    position = 1
                                    lost = False
                                else:
                                    if lost == False:
                                        lost = True
                                        lost_time = time.ticks_ms()
                                    else:
                                        if (time.ticks_diff(time.ticks_ms(), lost_time)) > safe_lost_time:
                                            race_failed()
                                            break
                                        else:
                                            pass
                            if position == 1:
                                if custom_start.value() == 0:
                                    position = 0
                                    lost = False
                                elif custom_track.value() == 0:
                                    lost = False
                                elif custom_end.value() == 0:
                                    race_win()
                                    break
                                else:
                                    if lost == False:
                                        lost = True
                                        lost_time = time.ticks_ms()
                                    else:
                                        if (time.ticks_diff(time.ticks_ms(), lost_time)) > safe_lost_time:
                                            race_failed()
                                            break
                                        else:
                                            pass
def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        return (0, 0, 0)
    if pos < 85:
        return (255 - pos * 3, pos * 3, 0)
    if pos < 170:
        pos -= 85
        return (0, 255 - pos * 3, pos * 3)
    pos -= 170
    return (pos * 3, 0, 255 - pos * 3)

def run_race():
    global tim
    tim = Timer()
    position = 0
    np.fill((0,0,0))
    np.write()
    np[0] = (127,100,0)
    np.write()
    _thread.start_new_thread(buzz,(500,0.4))
    time.sleep_ms(500)
    global lost
    lost = False
    if start_pad.value() == 0:
        np[1] = (127,100,0)
        np.write()
        _thread.start_new_thread(buzz,(500,0.4))
        time.sleep_ms(500)
        if start_pad.value() == 0:
            np[2] = (127,100,0)
            np.write()
            _thread.start_new_thread(buzz,(500,0.4))
            time.sleep_ms(500)
            if start_pad.value() == 0:
                #race is started!
                tim.init(period=100, mode=Timer.PERIODIC, callback=print_time)
                np.fill((0,127,0))
                np.write()
                buzz(1000,0.4)
                while True:
                    if position == 0:
                        if start_pad.value() == 0:
                            lost = False
                        elif seg1_pad.value() == 0:
                            position = 1
                            lost = False
                        else:
                            if lost == False:
                                lost = True
                                lost_time = time.ticks_ms()
                            else:
                                if (time.ticks_diff(time.ticks_ms(), lost_time)) > safe_lost_time:
                                    race_failed()
                                    break
                                else:
                                    pass
                    if position == 1:
                        if start_pad.value() == 0:
                            position = 0
                            lost = False
                        elif seg1_pad.value() == 0:
                            lost = False
                        elif seg2_pad.value() == 0:
                            position = 2
                            lost = False
                        else:
                            if lost == False:
                                lost = True
                                lost_time = time.ticks_ms()
                            else:
                                if (time.ticks_diff(time.ticks_ms(), lost_time)) > safe_lost_time:
                                    race_failed()
                                    break
                                else:
                                    pass
                    if position == 2:
                        if seg1_pad.value() == 0:
                            position = 1
                            lost = False
                        elif seg2_pad.value() == 0:
                            lost = False
                        elif seg3_pad.value() == 0:
                            position = 3
                            lost = False
                        else:
                            if lost == False:
                                lost = True
                                lost_time = time.ticks_ms()
                            else:
                                if (time.ticks_diff(time.ticks_ms(), lost_time)) > safe_lost_time:
                                    race_failed()
                                    break
                                else:
                                    pass
                    if position == 3:
                        if seg2_pad.value() == 0:
                            position = 1
                            lost = False
                        elif seg3_pad.value() == 0:
                            lost = False
                        elif seg4_pad.value() == 0:
                            position = 4
                            lost = False
                        else:
                            if lost == False:
                                lost = True
                                lost_time = time.ticks_ms()
                            else:
                                if (time.ticks_diff(time.ticks_ms(), lost_time)) > safe_lost_time:
                                    race_failed()
                                    break
                                else:
                                    pass
                    if position == 4:
                        if seg3_pad.value() == 0:
                            position = 1
                            lost = False
                        elif seg4_pad.value() == 0:
                            lost = False
                        elif seg5_pad.value() == 0:
                            position = 5
                            lost = False
                        else:
                            if lost == False:
                                lost = True
                                lost_time = time.ticks_ms()
                            else:
                                if (time.ticks_diff(time.ticks_ms(), lost_time)) > safe_lost_time:
                                    race_failed()
                                    break
                                else:
                                    pass
                    if position == 5:
                        if seg4_pad.value() == 0:
                            position = 1
                            lost = False
                        elif seg5_pad.value() == 0:
                            lost = False
                        elif seg2_pad.value() == 0:
                            position = 6
                            lost = False
                        else:
                            if lost == False:
                                lost = True
                                lost_time = time.ticks_ms()
                            else:
                                if (time.ticks_diff(time.ticks_ms(), lost_time)) > safe_lost_time:
                                    race_failed()
                                    break
                                else:
                                    pass
                    if position == 6:
                        if seg5_pad.value() == 0:
                            position = 1
                            lost = False
                        elif seg2_pad.value() == 0:
                            lost = False
                        elif seg6_pad.value() == 0:
                            position = 7
                            lost = False
                        else:
                            if lost == False:
                                lost = True
                                lost_time = time.ticks_ms()
                            else:
                                if (time.ticks_diff(time.ticks_ms(), lost_time)) > safe_lost_time:
                                    race_failed()
                                    break
                                else:
                                    pass
                    if position == 7:
                        if seg2_pad.value() == 0:
                            position = 1
                            lost = False
                        elif seg6_pad.value() == 0:
                            lost = False
                        elif finish_pad.value() == 0:
                            race_win()
                            break
                        else:
                            if lost == False:
                                lost = True
                                lost_time = time.ticks_ms()
                            else:
                                if (time.ticks_diff(time.ticks_ms(), lost_time)) > safe_lost_time:
                                    race_failed()
                                    break
                                else:
                                    pass
def debounce(length=0.2):
    sleep(length)

def run_qa():
    ####TEST DISPLAY#####
    tm.show("8888")
    sleep(1)

    ####TEST LEDs#####
    tm.show("leds")
    for x in range(7):
        np.fill((0,0,0))
        np[x] = (80,0,0)
        np.write()
        sleep(.1)
        np.fill((0,0,0))
        np[x] = (0,80,0)
        np.write()
        sleep(.1)
        np.fill((0,0,0))
        np[x] = (0,0,80)
        np.write()
        sleep(.1)
        np.fill((0,0,0))
        np.write()
        
    ####TEST BUZZER#####
    tm.show("buzz")
    buzz_count = 0
    song = music('4 G#5 1 16;3 A5 1 16;7 C7 1 16;1 F#6 1 16;2 D#6 1 16;0 G6 1 16;5 E6 1 16;6 G#6 1 16', pins=[Pin(buzz_pin)])
    while buzz_count < 24:
        song.tick()
        sleep(0.04)
        buzz_count=buzz_count+1
    song.stop()

    ####TEST track#####
    tm.show("strt")
    while True:
        if start_pad.value() == 0:
            tm.show("good")
            sleep(.5)
            break
        else:
            sleep(.01)
            
    tm.show("seg1")
    while True:
        if seg1_pad.value() == 0:
            tm.show("good")
            sleep(.5)
            break
        else:
            sleep(.01)
            
    tm.show("seg2")
    while True:
        if seg2_pad.value() == 0:
            tm.show("good")
            sleep(.5)
            break
        else:
            sleep(.01)

    tm.show("seg3")
    while True:
        if seg3_pad.value() == 0:
            tm.show("good")
            sleep(.5)
            break
        else:
            sleep(.01)

    tm.show("seg4")
    while True:
        if seg4_pad.value() == 0:
            tm.show("good")
            sleep(.5)
            break
        else:
            sleep(.01)

    tm.show("seg5")
    while True:
        if seg5_pad.value() == 0:
            tm.show("good")
            sleep(.5)
            break
        else:
            sleep(.01)

    tm.show("seg6")
    while True:
        if seg6_pad.value() == 0:
            tm.show("good")
            sleep(.5)
            break
        else:
            sleep(.01)

    tm.show("fnsh")
    while True:
        if finish_pad.value() == 0:
            tm.show("good")
            sleep(.5)
            break
        else:
            sleep(.01)

    tm.show("ball")
    while True:
        if poleball_pad.value() == 0:
            tm.show("good")
            sleep(.5)
            break
        else:
            sleep(.01)
            
    tm.show("done")
    sleep(1)
    f = open('data.txt', 'rb')
    settings = decrypt(f.read()).decode('utf-8').strip()
    j = json.loads(settings)
    global deep_qa_pass
    deep_qa_pass = 1
    j['deep_qa_pass'] = deep_qa_pass
    print("passed QA. writing")
    print(j)
    f.write(encrypt(json.dumps(j)))
    
    f.close()

runme()


