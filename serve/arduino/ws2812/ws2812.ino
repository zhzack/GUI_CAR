#include <ESP8266WiFi.h>
#include <WiFiClient.h>
#include "FastLED.h"  // 此示例程序需要使用FastLED库

#include "FastLED.h"  // 此示例程序需要使用FastLED库

#define NUM_LEDS 144 * 15  // LED灯珠数量
#define LIGHT_LEDS 80
#define PIN 12           // Arduino输出控制信号引脚
#define LED_TYPE WS2812  // LED灯带型号
#define COLOR_ORDER GRB  // RGB灯珠中红色、绿色、蓝色LED的排列顺序

#define PIN_BIG_RGB 14  //射灯开关


uint8_t max_bright = 255;  // LED亮度控制变量，可使用数值为 0 ～ 255， 数值越大则光带亮度越高
int index_led = 0;

CRGB leds[NUM_LEDS];  // 建立光带leds

int dis_connect_index = 0;

int last_start_index = 0;





const char* ssid = "1";             // WiFi名称
const char* password = "11111111";  // WiFi密码

// const char* serverIP = "172.20.10.2";  // 服务器IP地址
const char* serverIP = "192.168.138.13";  // 服务器IP地址
const int serverPort = 80;                // 服务器端口

WiFiClient client;  // 创建WiFiClient对象


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


void setup() {
  // 启动串口
  Serial.begin(115200);   // 用于调试输出
  Serial1.begin(115200);  // 串口1，用于与其他设备通信

  LEDS.addLeds<LED_TYPE, PIN, COLOR_ORDER>(leds, NUM_LEDS);  // 初始化光带
  FastLED.setBrightness(max_bright);                         // 设置光带亮度
  fill_solid(leds, NUM_LEDS, CRGB(0, 0, 0));
  FastLED.show();

  // 连接Wi-Fi
  // connectToWiFi();

  // 尝试连接TCP服务器
  connectToServer();
}






int parseCommand(String command) {
  // 查找字符 'P' 和 'T' 的位置
  int pwmStartIndex = command.indexOf("P") + 1;  // PWM 数据从 'P' 后开始
  int pwmEndIndex = command.indexOf("T");        // 'T' 表示 PWM 结束

  // 提取 PWM 数据字符串
  String pwm_str = command.substring(pwmStartIndex, pwmEndIndex);

  // 将字符串转换为整数
  int pwm = pwm_str.toInt();  // pwm 是一个整数

  // 输出 PWM 值
  Serial.print("解析到的PWM值: ");
  Serial.println(pwm);
  return pwm;
}

void loop() {
  // 如果TCP连接丢失，尝试重新连接
  if (!client.connected()) {
    Serial.println("TCP连接丢失,正在重新连接...");
    connectToServer();
  }


  while (client.connected() || client.available()) {
    String receivedData = "";
    if (client.available()) {
      receivedData = client.readStringUntil('!');
      receivedData += '!';
      // Serial.println(receivedData);
    }
    if (receivedData.length() > 0) {

      // // 将接收到的数据通过串口1发送
      // Serial1.println(receivedData);

      // 将数据发送回TCP服务器
      if (client.connected()) {
        // client.println(receivedData);
      } else {
        Serial.println("TCP 连接断开，无法发送数据");
      }
      int addIndex = receivedData.indexOf("+");
      int ledValue = receivedData.substring(0, addIndex).toInt();

      String servoValue = receivedData.substring(addIndex + 1);
      Serial.println(ledValue);
      // Serial.println(servoValue);
      //   setRangeLedLight2(ledValue);
      // index_fill_solid_cir(ledValue);


      digitalWrite(PIN_BIG_RGB, LOW);

      // parseCommand(receivedData);
    }
    yield();    // 允许ESP8266处理后台任务
    delay(10);  // 延时10ms以防止占用过多CPU
  }

  delay(10);  // 延时100ms以防止占用过多CPU
}

// 连接Wi-Fi网络
void connectToWiFi() {
  Serial.println("连接到Wi-Fi...");
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("正在连接Wi-Fi...");
  }

  Serial.println("已连接到Wi-Fi");
  Serial.print("IP地址: ");
  Serial.println(WiFi.localIP());
  dis_connect_index = 0;
}

// 连接到TCP服务器
void connectToServer() {
  connectToWiFi();
  // 连接到指定的IP和端口
  while (!client.connect(serverIP, serverPort)) {
    Serial.println(WiFi.localIP());
    Serial.println(serverIP);
    Serial.println("无法连接到服务器，正在重试...");
    dis_connect_index++;
    delay(1000);
    if (dis_connect_index >= 5) {
      digitalWrite(PIN_BIG_RGB, HIGH);
    }
  }

  Serial.println("已连接到TCP服务器");
}
