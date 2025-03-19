#include <ESP8266WiFi.h>
#include <WiFiUdp.h>

#define RELAY_PIN 0             // 继电器引脚
#define WIFI_SSID "1"           // WiFi名称
#define WIFI_PASSWORD "11111111" // WiFi密码
#define BROADCAST_IP "255.255.255.255"
#define BROADCAST_PORT 5005
#define TCP_PORT 6666
#define UDP_TIMEOUT 5000        // UDP广播超时时间 (毫秒)
#define HEARTBEAT_INTERVAL 1000   // 心跳包间隔 (毫秒)

WiFiUDP udp;
WiFiClient client;

String serverIP = "";
bool isConnectedToServer = false;
unsigned long lastHeartbeatTime = 0;

void setup() {
  Serial.begin(115200);
  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, LOW); // 初始状态关闭继电器

  // 连接 WiFi
  Serial.print("正在连接到WiFi...");
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi连接成功！");
  Serial.print("本地IP地址: ");
  Serial.println(WiFi.localIP());

  // 开始进行UDP广播
  if (findServer()) {
    connectToServer();
  }
}

void loop() {
  if (isConnectedToServer && client.connected()) {
    if (client.available()) {
      String data = client.readStringUntil(',');
      data.trim();
      
      if (data == "1") {
        digitalWrite(RELAY_PIN, HIGH);
        Serial.println("继电器已开启。");
      } else if (data == "0") {
        digitalWrite(RELAY_PIN, LOW);
        Serial.println("继电器已关闭。");
      }
    }

    // 发送心跳包
    if (millis() - lastHeartbeatTime >= HEARTBEAT_INTERVAL) {
      client.print("HEARTBEAT,");
      lastHeartbeatTime = millis();
    }
  } else if (!isConnectedToServer) {
    // 尝试重新连接服务器
    if (findServer()) {
      connectToServer();
    }
  } else if (!client.connected()) {
    Serial.println("连接丢失，正在尝试重连...");
    isConnectedToServer = false;
    client.stop();
  }
}

// 查找服务器 (UDP 广播)
bool findServer() {
  udp.begin(0); // 使用任意可用的本地端口
  udp.beginPacket(BROADCAST_IP, BROADCAST_PORT);
  udp.print("DISCOVER_SERVER");
  udp.endPacket();
  Serial.println("正在发送广播消息...");

  unsigned long startTime = millis();
  while (millis() - startTime < UDP_TIMEOUT) {
    int packetSize = udp.parsePacket();
    if (packetSize) {
      char incomingPacket[255];
      int len = udp.read(incomingPacket, 255);
      if (len > 0) {
        incomingPacket[len] = 0;
      }
      String response = String(incomingPacket);
      Serial.print("收到服务器响应: ");
      Serial.println(response);

      // 解析服务器地址
      int firstComma = response.indexOf(',');
      int lastComma = response.lastIndexOf(',');

      if (firstComma != -1 && lastComma != -1 && firstComma != lastComma) {
        serverIP = response.substring(firstComma + 1, lastComma);
        String port = response.substring(lastComma + 1);

        Serial.print("找到服务器: IP=");
        Serial.print(serverIP);
        Serial.print(", PORT=");
        Serial.println(port);
        udp.stop();
        return true;
      }
    }
    delay(100);
  }
  Serial.println("未找到服务器，广播超时。");
  udp.stop();
  return false;
}

// 连接到TCP服务器
void connectToServer() {
  Serial.print("正在连接到服务器 ");
  Serial.print(serverIP);
  Serial.print(":");
  Serial.println(TCP_PORT);

  if (client.connect(serverIP.c_str(), TCP_PORT)) {
    isConnectedToServer = true;
    Serial.println("TCP 服务器连接成功！");
  } else {
    Serial.println("TCP 服务器连接失败！");
    isConnectedToServer = false;
  }
}
