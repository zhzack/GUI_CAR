
#include "FastLED.h"  // 此示例程序需要使用FastLED库

#define NUM_LEDS 144 * 15  // LED灯珠数量
#define LIGHT_LEDS 80
#define PIN 12           // Arduino输出控制信号引脚
#define LED_TYPE WS2812  // LED灯带型号
#define COLOR_ORDER GRB  // RGB灯珠中红色、绿色、蓝色LED的排列顺序

uint8_t max_bright = 255;  // LED亮度控制变量，可使用数值为 0 ～ 255， 数值越大则光带亮度越高
int index_led = 0;

CRGB leds[NUM_LEDS];  // 建立光带leds


void loop_cir() {
  // fill_gradient 显示两种颜色
  //fill_gradient(leds, 0, CHSV(50, 255,255) , 29, CHSV(150,255,255), SHORTEST_HUES);
  // fill_gradient(leds+index_led, 0, CHSV(50, 255, 255), 144-index_led, CHSV(150, 255, 255), LONGEST_HUES);
  fill_solid(leds, NUM_LEDS, CRGB(0, 0, 0));
  // fill_solid(leds + index_led, LIGHT_LEDS, CRGB::Red);
  if (index_led + (LIGHT_LEDS) > NUM_LEDS) {
    fill_solid(leds + index_led, LIGHT_LEDS - (LIGHT_LEDS + index_led) % NUM_LEDS, CRGB::Red);
    fill_solid(leds, (LIGHT_LEDS + index_led) % NUM_LEDS, CRGB::Red);
  } else {
    fill_solid(leds + index_led, LIGHT_LEDS, CRGB::Red);
  }
  index_led += 1;
  index_led %= NUM_LEDS;
  FastLED.show();
  delay(1);
}

void index_fill_solid_cir(uint8_t index) {
  // fill_gradient 显示两种颜色
  //fill_gradient(leds, 0, CHSV(50, 255,255) , 29, CHSV(150,255,255), SHORTEST_HUES);
  // fill_gradient(leds+index, 0, CHSV(50, 255, 255), 144-index, CHSV(150, 255, 255), LONGEST_HUES);
  fill_solid(leds, NUM_LEDS, CRGB(0, 0, 0));
  // fill_solid(leds + index, LIGHT_LEDS, CRGB::Red);
  if (index + (LIGHT_LEDS) > NUM_LEDS) {
    fill_solid(leds + index, LIGHT_LEDS - (LIGHT_LEDS + index) % NUM_LEDS, CRGB::Red);
    fill_solid(leds, (LIGHT_LEDS + index) % NUM_LEDS, CRGB::Red);
  } else {
    fill_solid(leds + index, LIGHT_LEDS, CRGB::Red);
  }
  index += 1;
  index %= NUM_LEDS;
  FastLED.show();
  delay(1);
}

void index_fill_rainbow(uint8_t index) {

  // fill_solid(leds, NUM_LEDS, CRGB(200, 200, 200));
  fill_solid(leds, NUM_LEDS, CRGB(0, 0, 0));
  if (index + (LIGHT_LEDS) > NUM_LEDS) {
    fill_rainbow(leds + index, LIGHT_LEDS - (LIGHT_LEDS + index) % NUM_LEDS, CRGB::Red);
    fill_rainbow(leds, (LIGHT_LEDS + index) % NUM_LEDS, CRGB::Red);
  } else {
    fill_rainbow(leds + index, LIGHT_LEDS, CRGB::Red);
  }

  FastLED.show();
  delay(1);
}

void index_fill_rainbow_cir(uint8_t index) {
  if (index == 0) {
    index = index_led;
  }
  // fill_solid(leds, NUM_LEDS, CRGB(200, 200, 200));
  fill_solid(leds, NUM_LEDS, CRGB(0, 0, 0));
  // if (index + (LIGHT_LEDS) > NUM_LEDS) {
  //   fill_rainbow_circular(leds + index, LIGHT_LEDS - (LIGHT_LEDS + index) % NUM_LEDS, CRGB::Red);
  //   fill_rainbow_circular(leds, (LIGHT_LEDS + index) % NUM_LEDS, CRGB::Red);
  // } else {
  //   fill_rainbow_circular(leds + index, LIGHT_LEDS, CRGB::Red);
  // }
  fill_rainbow_circular(leds + index, LIGHT_LEDS, CRGB::Red);
  index += 1;
  index %= NUM_LEDS;
  index_led = index;
  FastLED.show();
  delay(1);
}

void index_fill_gradient_RGB(uint16_t index) {
  // if (index == 0) {
  //   index = index_led;
  // }
  // fill_solid(leds, NUM_LEDS, CRGB(200, 200, 200));
  fill_solid(leds, NUM_LEDS, CRGB(0, 0, 0));
  if (index + LIGHT_LEDS > NUM_LEDS) {
    // 绘制尾部
    int tailLength = NUM_LEDS - index;
    fill_gradient_RGB(leds + index, tailLength, CRGB::Red, CRGB::Blue);

    // 绘制头部
    int headLength = LIGHT_LEDS - tailLength;
    fill_gradient_RGB(leds, headLength, CRGB::Red, CRGB::Blue);
  } else {
    // 完全在范围内，正常绘制
    fill_gradient_RGB(leds + index, LIGHT_LEDS, CRGB::Red, CRGB::Blue);
  }
  // index += 1;
  // index %= NUM_LEDS;
  // index_led = index;
  FastLED.show();
  // delay(1);
}


void setup() {
  Serial.begin(115200);
  Serial1.begin(115200);
  LEDS.addLeds<LED_TYPE, PIN, COLOR_ORDER>(leds, NUM_LEDS);  // 初始化光带
  FastLED.setBrightness(max_bright);                         // 设置光带亮度
  fill_solid(leds, NUM_LEDS, CRGB(0, 0, 0));
  FastLED.show();
}

void loop() {
  // loop_cir();


  String inString = "";
  while (Serial.available() > 0) {
    inString += char(Serial.read());
    delay(1);
  }
  String inString1 = "";
  while (Serial1.available() > 0) {
    char c = Serial1.read();  // 读取一个字符
    inString += c;            // 将字符添加到字符串中

    // 如果读取到指定的结束字符，结束读取
    if (c == '!' || c == '+') {
      break;
    }
    delay(1);
  }
  // // 检查是否接收到数据，如果接收到数据，则输出该数据
  if (inString.length() > 0) {
    // Serial.print("Input String:");


    if (inString.indexOf('!') != -1) {
      Serial.println(inString + "1");
      // index_fill_gradient_RGB(inString.toInt() % NUM_LEDS);
      // index_fill_rainbow_cir(inString.toInt() % NUM_LEDS);

      // fill_solid(leds, NUM_LEDS, CRGB(0, 0, 0));
      // fill_gradient_RGB(leds + inString.toInt(), LIGHT_LEDS, CRGB::Red, CRGB::Blue);
      // FastLED.show();
    } else if (inString.indexOf('+') != -1) {
      // Serial1.println(inString + "");
      Serial.println(inString + "2");
    }
  }
  if (inString1 != "") {
    Serial.println(inString1);
  }

  // index_fill_gradient_RGB(random(1, NUM_LEDS));
  // index_fill_gradient_RGB(index_led);
  // index_led += 20;
  // index_led %= NUM_LEDS;
  // Serial.println(index_led);

  // delay(250);
  // fill_palette(leds, NUM_LEDS, 0, 8, OceanColors_p, 255, LINEARBLEND);
  // FastLED.show();
  // delay(25);
}
