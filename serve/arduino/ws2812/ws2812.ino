#include <Adafruit_NeoPixel.h>                  // 操作WS2812B需要使用的库

#define PIN         12    //GPIO0接口
#define NUMPIXELS   144    //彩灯个数

Adafruit_NeoPixel led(NUMPIXELS, PIN, NEO_GRB + NEO_KHZ800);

void setup() {
	led.begin();
	led.setBrightness(255); //设置亮度 (0~255)
	for(int i=0; i<NUMPIXELS; ++i) {	//所有灯全部设为红色
        led.setPixelColor(i,led.Color(255, 0, 0)); //红色
    }
    led.show();   //刷新显示
    delay(1000);
}
void loop() {
	
}
