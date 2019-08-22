from neopixel import NeoPixel

class View():
    def __init__(self, pin, number_of_pixels):
        self.number_of_pixels = number_of_pixels
        self.pin = pin 
        self.np = NeoPixel(self.pin, self.number_of_pixels)  
        self.last_render_time = 0
        
    def render(self, color):
        for i in range(self.number_of_pixels):
            self.np[i] = color.instruction()
            self.np.write()
            self.last_render_time = 0
