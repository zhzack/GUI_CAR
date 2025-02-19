#include <ESP8266WiFi.h>
#include <WiFiClient.h>

#include <Adafruit_NeoPixel.h>  // 操作WS2812B需要使用的库

#define PIN 12              //GPIO0接口
#define PIN_BIG_RGB 14      //射灯开关
#define NUMPIXELS 144 * 15  //彩灯个数
#define LIGHTNUM 144        //亮灯的数量

Adafruit_NeoPixel led(NUMPIXELS, PIN, NEO_GRB + NEO_KHZ800);

const char* ssid = "1";             // WiFi名称
const char* password = "11111111";  // WiFi密码

// const char* serverIP = "172.20.10.2";  // 服务器IP地址
const char* serverIP = "192.168.138.13";  // 服务器IP地址
const int serverPort = 80;                // 服务器端口

WiFiClient client;  // 创建WiFiClient对象

int dis_connect_index = 0;

int last_start_index = 0;



void setup() {
  // 启动串口
  Serial.begin(115200);   // 用于调试输出
  Serial1.begin(115200);  // 串口1，用于与其他设备通信

  led.begin();
  led.setBrightness(255);  //设置亮度 (0~255)

  // 连接Wi-Fi
  // connectToWiFi();

  // 尝试连接TCP服务器
  connectToServer();
}
void setRangeLedLight(int start) {
  for (int i = 0; i < LIGHTNUM; ++i) {
    int ledIndex = (last_start_index + i) % NUMPIXELS;  // 确保LED索引循环
    led.setPixelColor(ledIndex, led.Color(0, 0, 0));    // 将上一组数据设置成关闭
    last_start_index = start;
  }
  for (int i = 0; i < LIGHTNUM; ++i) {
    int ledIndex = (start + i) % NUMPIXELS;             // 确保LED索引循环
    led.setPixelColor(ledIndex, led.Color(255, 0, 0));  // 设置为红色
  }
  led.show();  //刷新显示
}

void setRangeLedLight2(int start) {
  int end = start + LIGHTNUM;
  if (end > start) {
    for (int i = 0; i < NUMPIXELS; ++i) {  //所有灯全部设为红色

      if (i >= start && i <= end) {
        led.setPixelColor(i, led.Color(255, 0, 0));  //红色

      } else {
        led.setPixelColor(i, led.Color(0, 0, 0));
      }
    }
  } else {
    for (int i = 0; i < NUMPIXELS; ++i) {  //所有灯全部设为红色

      if (i >= end && i <= start) {
        led.setPixelColor(i, led.Color(0, 0, 0));  //红色

      } else {
        led.setPixelColor(i, led.Color(255, 0, 0));
      }
    }
  }

  led.show();  //刷新显示
}

void setRangeLedLight1(int start, int end) {
  // 确保 start 和 end 在有效范围内
  start = constrain(start, 0, NUMPIXELS - 1);
  end = constrain(end, 0, NUMPIXELS - 1);

  // 关闭所有灯并更新
  for (int i = 0; i < NUMPIXELS; ++i) {
    led.setPixelColor(i, led.Color(0, 0, 0));  // 关闭所有灯
  }

  // 点亮从起始位置开始的连续 numLedsToLight 个灯
  for (int i = 0; i < 144; ++i) {
    int ledIndex = (start + i) % NUMPIXELS;             // 确保LED索引循环
    led.setPixelColor(ledIndex, led.Color(255, 0, 0));  // 设置为红色
  }
  led.show();  // 更新LED显示
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
      setRangeLedLight2(ledValue);


      digitalWrite(PIN_BIG_RGB, LOW);

      // parseCommand(receivedData);
    }
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
