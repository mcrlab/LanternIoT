import math
import time
import json
from lantern.palette import Palette
from lantern.color import Color

class App():
    def __init__(self,id, config, view, broker, now):
        self.id = id
        self.config = config
        self.view = view
        self.broker = broker
        self.now = now

        self.palette = Palette(view.number_of_pixels)
        self.last_instruction_time = 0
        self.last_ping_time = 0 
        self.last_render_time = 0
        self.broker.set_callback(self.subscription_callback)

    def subscription_callback(self, topic, message):
        try:
            current_time = self.now()
            data = json.loads(message)
            color = Color(data['color']['r'],data['color']['g'],data['color']['b'])
            animation_length = data['time']
            animation_start_time = current_time + data['delay']
            self.palette.update(color, animation_start_time, animation_length, current_time) 
            self.last_instruction_time = current_time
        except Exception as inst:
            print("Error in subscription callback", inst)

    def ping(self, current_time):
        update = json.dumps({
            "id" : self.id,
            "current_color" : self.palette.color_to_render(current_time).as_object()
            })
        self.broker.publish("connect", update)
        self.last_ping_time = current_time

    def main(self, retries):
        try:
            self.broker.connect()
            self.ping(self.now())
            self.broker.subscribe("color/"+self.id)
            self.last_render_time = self.now()
            while True:
                current_time = self.now()
                
                if((current_time - self.last_render_time) > self.config['RENDER_INTERVAL']):
                    color_buffer = self.palette.color_to_render(current_time)
                    self.view.render(color_buffer, current_time)
                    self.last_render_time = current_time

                if((current_time - self.last_ping_time) > self.config['PING_INTERVAL']):
                    self.ping(current_time)

                self.broker.check_msg()
                
            self.broker.disconnect()
        except TypeError as e:
            print('error', e)
        except OSError as error:
            print("Connection error", error)
            time.sleep(5)
            if(retries > 0):
                retries = retries - 1
                self.main(retries)
            else:
                print("Failed too many times")
                self.view.render(Color(0,0,255), self.now())
                time.sleep(5)
                self.view.render(Color(0,0,0), self.now())
            
            