#include "esp_camera.h"
#include <WiFi.h>
#include <PubSubClient.h>

#define CAMERA_MODEL_AI_THINKER
#include "camera_pins.h"

#define FLASH_LED_GPIO_NUM 4

const char* ssid = "Valenet_mb71";
const char* password = "key2023@mb71";
IPAddress ip(192, 168, 2, 100);  // Ip do webserver
IPAddress gateway(192, 168, 2, 1); 
IPAddress subnet(255, 255, 255, 0);

bool cameraServerActive = false;
void startCameraServer();
int stopCameraServer();
void flashOn();
void flashOff();
void callback(char* topic, byte* payload, unsigned int length);
void reconnect();
void configurations();

const char* mqttServer = "192.168.2.142"
const int mqttPort = 1883;
const char* mqttUser = "rover";
const char* mqttPassword = "password1234";

WiFiClient wifiClient;
PubSubClient client(wifiClient);

bool cameraOn = false;

void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Mensagem recebida: ");
  for (int i = 0; i < length; i++) {
    Serial.print((char)payload[i]);
  }
  Serial.println();
  char comando[length + 1];
  for (int i = 0; i < length; i++) {
    comando[i] = (char)payload[i];
  }
  comando[length] = '\0';
  if ((strcmp(comando, "L") == 0) && !cameraOn) {
    Serial.println("Ligando...");
    configurations();
    startCameraServer();
    flashOn();
    Serial.println("Camera Ligada");
    cameraOn = true;
  } else if ((strcmp(comando, "D") == 0) && cameraOn){
    Serial.println("Desligando");
    cameraOn = false;
    flashOff();
    ESP.restart();
    }
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Tentando se reconectar ao servidor MQTT...");
    if (client.connect("ESP32-CAM", mqttUser, mqttPassword)) {
      Serial.println(" Conectado");
      client.subscribe("/cam");
    } else {
      Serial.print("falhou, rc=");
      Serial.print(client.state());
      delay(5000);
    }
  }
}

void configurations(){

  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.frame_size = FRAMESIZE_VGA;
  config.pixel_format = PIXFORMAT_JPEG;
  config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;
  config.fb_location = CAMERA_FB_IN_PSRAM;
  config.jpeg_quality = 10;
  config.fb_count = 1;
  
  if(config.pixel_format == PIXFORMAT_JPEG){
    if(psramFound()){
      config.jpeg_quality = 10;
      config.fb_count = 1;
      config.grab_mode = CAMERA_GRAB_LATEST;
    } else {
      config.frame_size = FRAMESIZE_SVGA;
      config.fb_location = CAMERA_FB_IN_DRAM;
    }
  } else {
    config.frame_size = FRAMESIZE_240X240;
#if CONFIG_IDF_TARGET_ESP32S3
    config.fb_count = 2;
#endif
  }

  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    return;
  }

  sensor_t * s = esp_camera_sensor_get();
  if (s->id.PID == OV3660_PID) {
    s->set_vflip(s, 1);
    s->set_brightness(s, 1); 
    s->set_saturation(s, -2);
  }

  if(config.pixel_format == PIXFORMAT_JPEG){
    s->set_framesize(s, FRAMESIZE_VGA);
  }

  ledcAttachPin(FLASH_LED_GPIO_NUM, 1);
  ledcSetup(1, 5000, 8);

  flashOff();

}

void setup() {
  Serial.begin(115200);

  // Inicializar a conexão MQTT
  client.setServer(mqttServer, mqttPort);
  client.setCallback(callback);

  // Inicializa conexão Webserver
  WiFi.begin(ssid, password);
  WiFi.setSleep(false);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  WiFi.config(ip, gateway, subnet);
  Serial.println("");
  Serial.println("WiFi connected");


}

void flashOn(){
  ledcWrite(1, 255);
}

void flashOff(){
  ledcWrite(1, 0);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
  delay(500);
}