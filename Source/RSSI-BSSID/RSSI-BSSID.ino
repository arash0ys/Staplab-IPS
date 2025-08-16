#include "WiFi.h"
#include "esp_wifi.h"

// === Configuration ===
const uint8_t TARGET_CHANNEL = 6;
const unsigned int SCAN_INTERVAL_MS = 200;

// Add BSSIDs (MAC addresses) of the APs you want to track
const uint8_t NUM_TARGETS = 3;
const uint8_t TARGET_BSSIDS[NUM_TARGETS][6] = {
  {0x00, 0x1E, 0xE3, 0xE8, 0x94, 0x81},  // BSSID 1
  {0x7C, 0xA6, 0x82, 0x31, 0x6B, 0xF5},  // BSSID 2
  {0x06, 0xC0, 0xEB, 0x9D, 0xD5, 0x11}   // BSSID 3
};

// === Variables ===
unsigned long lastScanTime = 0;
bool scanInProgress = false;
int scanCount = 0;

bool compareBSSID(const uint8_t* b1, const uint8_t* b2) {
  for (int i = 0; i < 6; i++) {
    if (b1[i] != b2[i]) return false;
  }
  return true;
}

void printBSSID(const uint8_t* bssid) {
  for (int i = 0; i < 6; i++) {
    if (i > 0) Serial.print(":");
    Serial.printf("%02X", bssid[i]);
  }
}

void setup() {
  Serial.begin(115200);
  WiFi.mode(WIFI_STA);
  WiFi.disconnect();
  delay(100);

  esp_wifi_set_promiscuous(true);
  esp_wifi_set_channel(TARGET_CHANNEL, WIFI_SECOND_CHAN_NONE);

  Serial.println("\nFast ESP32 WiFi RSSI Sniffer (Multi-BSSID)");
  Serial.printf("Tracking %d BSSID(s) on channel %d\n", NUM_TARGETS, TARGET_CHANNEL);
  for (int i = 0; i < NUM_TARGETS; i++) {
    Serial.print("  -> ");
    printBSSID(TARGET_BSSIDS[i]);
    Serial.println();
  }
  Serial.println("----------------------------------");
}

void loop() {
  unsigned long currentTime = millis();

  if (!scanInProgress && (currentTime - lastScanTime >= SCAN_INTERVAL_MS)) {
    WiFi.scanDelete();
    scanInProgress = true;
    lastScanTime = currentTime;

    WiFi.scanNetworks(true, true, false, 50, TARGET_CHANNEL);
  }

  if (scanInProgress) {
    int scanComplete = WiFi.scanComplete();

    if (scanComplete > 0) {
      scanInProgress = false;
      scanCount++;

      for (int i = 0; i < scanComplete; i++) {
        const uint8_t* bssid = WiFi.BSSID(i);
        for (int t = 0; t < NUM_TARGETS; t++) {
          if (compareBSSID(bssid, TARGET_BSSIDS[t])) {
            int rssi = WiFi.RSSI(i);
            Serial.printf("%02X:%02X:%02X:%02X:%02X:%02X,%d\n",
              bssid[0], bssid[1], bssid[2],
              bssid[3], bssid[4], bssid[5],
              rssi);

          }
        }
      }
    } else if (scanComplete == 0) {
      scanInProgress = false;
    }
  }

  delay(1);
}
