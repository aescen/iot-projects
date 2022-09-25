/********************************************************************************************Includes**/
#include <RF24.h>
#include <RF24Network.h>
#include <RF24Mesh.h>
#include <SPI.h>
#include <RFID.h>
/**/
#define F_CPU 16000000UL
#define sprint Serial.print
#define sprintln Serial.println
/********************************************************************************************RFID setup**/
#define SS_PIN 10
#define RST_PIN 2
RFID rfid(SS_PIN, RST_PIN);
/**/
/********************************************************************************************Radio setup**/
RF24 radio(7, 8); //CE,CSN
RF24Network network(radio);
RF24Mesh mesh(radio, network);
const uint16_t nodeID = 01;
const char HEADER_NODE_KERANJANG  = 'K';
/**/
/********************************************************************************************Variables**/
/* variabel pewaktu pembaca rfid */
//unsigned long tStart = 0;
//uint32_t tInterval = 370; //interval pembacaan rfid
//bool timer = false;
/**/
/* variabel / data rfid */
const uint8_t RFID_OCTET_LENGTH = 5;
bool productTagIsFound = false;
uint8_t detectedCardId[RFID_OCTET_LENGTH] = {0, 0, 0, 0, 0};
// daftar card id produk
const uint8_t productsCard[][RFID_OCTET_LENGTH] = {
  {211, 114, 175, 93, 83},  // Tag produk INDEX_ITEM_KERUDUNG / index 0
  {195, 180, 175, 93, 133}, // Tag produk INDEX_ITEM_KAOS_PUTIH / index 1
  {195, 120, 175, 93, 73},  // Tag produk INDEX_ITEM_KAOS_HITAM / index 2
  {195, 174, 175, 93, 159}, // Tag produk INDEX_ITEM_CELANA_SPORT / index 3
  {195, 168, 175, 93, 153}, // Tag produk INDEX_ITEM_LEGGING / index 4
};
const uint8_t INDEX_ITEM_KERUDUNG = 0;
const uint8_t INDEX_ITEM_KAOS_PUTIH = 1;
const uint8_t INDEX_ITEM_KAOS_HITAM = 2;
const uint8_t INDEX_ITEM_CELANA_SPORT = 3;
const uint8_t INDEX_ITEM_LEGGING = 4;
//--
// jumlah tiap produk
uint8_t jumlahByProductIndex[] = {
  // jumlah
  0, // Tag produk INDEX_ITEM_KERUDUNG / index 0
  0, // Tag produk INDEX_ITEM_KAOS_PUTIH / index 1
  0, // Tag produk INDEX_ITEM_KAOS_HITAM / index 2
  0, // Tag produk INDEX_ITEM_CELANA_SPORT / index 3
  0, // Tag produk INDEX_ITEM_LEGGING / index 4
};
//--
// index produk yang diperbarui selanjutnya
int updateProductAtIndex = -1;
//--
// data temporer untuk pengecekan pembaruan
int8_t tempJumlah = -1;
uint8_t tempProductId[RFID_OCTET_LENGTH] = { 0, 0, 0, 0, 0 };
//--
/**/
/* variabel payload / update data */
// variabel struktur data payload
struct PayloadOut {
  float cIDa;   //card serial number octet 1 / index 0
  float cIDb;   //card serial number octet 2 / index 1
  float cIDc;   //card serial number octet 3 / index 2
  float cIDd;   //card serial number octet 4 / index 3
  float cIDe;   //card serial number octet 5 / index 4
  float jumlah; // jumlah produk
  float nid;    // id node keranjang
};
//--
/**/
/********************************************************************************************Functions**/
// kirim data ke server
void sendPayload( uint8_t jumlah, uint8_t productId[RFID_OCTET_LENGTH] ) {
  RF24NetworkHeader header;
  PayloadOut payload = {
    (float)productId[0], // rfid octet 1
    (float)productId[1], // rfid octet 2
    (float)productId[2], // rfid octet 3
    (float)productId[3], // rfid octet 4
    (float)productId[4], // rfid octet 5
    (float)jumlah,       // jumlah produk
    (float)nodeID        // id node keranjang
  };
  if (!mesh.write(&payload, HEADER_NODE_KERANJANG, sizeof(payload))) {
    // If a write fails, check connectivity to the mesh network
    if ( !mesh.checkConnection() ) {
      //refresh the network address
      sprintln(F("|#Renewing Address"));
      mesh.renewAddress(10000);
      if (!mesh.write(&payload, HEADER_NODE_KERANJANG, sizeof(payload))) {
        // If a write STILL fails, mesh network is error
        sprintln(F("|#Send fail, mesh network is error"));
      }
    } else {
      sprintln(F("|#Send fail, test OK"));
    }
  }
}
//--
// cek id terdeteksi sama?
bool validateTagId(uint8_t id1[RFID_OCTET_LENGTH], uint8_t id2[RFID_OCTET_LENGTH]) {
  bool isIdValid = false;
  for (uint8_t cardOctet = 0; cardOctet < RFID_OCTET_LENGTH; cardOctet += 1 ) {
    if (id1[cardOctet] == id2[cardOctet]) {
      isIdValid = true;
    } else {
      isIdValid = false;
    }
  }
  return isIdValid;
}
//--
// baca rfid
void readProductCardSerial() {
  while (rfid.isCard()) {
    while (rfid.readCardSerial()) {
      // cek jika rfid ada di data produk
      int8_t productFoundAtIndex = -1;
      for (uint8_t productIndex = 0; productIndex < sizeof(productsCard); productIndex += 1) {
        // cek rfid ditemukan?
        bool isIdFound = validateTagId(rfid.serNum, productsCard[productIndex]);
        if (isIdFound) {
          // set id deteksi dengan id terdeteksi
          for (uint8_t i; i < RFID_OCTET_LENGTH; i += 1) {
            detectedCardId[i] = rfid.serNum[i];
          }
          // set index produk
          productFoundAtIndex = productIndex;
        }
      }

      if (productFoundAtIndex != -1) {
        // produk ditemukan
        productTagIsFound = true;
        jumlahByProductIndex[productFoundAtIndex] += 1;
        updateProductAtIndex = productFoundAtIndex;
      } else {
        // produk tidak ditemukan
        productTagIsFound = false;
        updateProductAtIndex = -1;
      }

      break;
    }
    break;
  }
  rfid.halt();
}
//--
// cek data temporer
bool checkTempData(uint8_t currentProductId[RFID_OCTET_LENGTH], uint8_t currentJumlah) {
  // data identik?
  bool isDataIdentic = false;
  // produk identik?
  bool isProductIdIdentic = validateTagId(tempProductId, currentProductId);
  // jumlah identik?
  bool isJumlahIdentic = tempJumlah == currentJumlah;

  // cek bila data temporer tidak sama dengan data terdeteksi sekarang
  if (isJumlahIdentic && isProductIdIdentic) {
    // jika identik
    isDataIdentic = true;
  } else {
    // jika tidak identik
    isDataIdentic = false;
  }

  return isDataIdentic;
}
//--
// perbarui produk
void productUpdate() {
  // cek produk terdeteksi dan index produk terdeteksi valid (bukan -1)
  if (productTagIsFound && updateProductAtIndex != -1) {
    // ambil id produk
    uint8_t productId[RFID_OCTET_LENGTH] = {
      productsCard[updateProductAtIndex][0],
      productsCard[updateProductAtIndex][1],
      productsCard[updateProductAtIndex][2],
      productsCard[updateProductAtIndex][3],
      productsCard[updateProductAtIndex][4],
    };
    // ambil jumlah sesuai id produk
    uint8_t jumlah = jumlahByProductIndex[updateProductAtIndex];

    // cek data temporer identik atau tidak bila tidak, perbarui data server
    bool isDataIdentical = checkTempData(productId, jumlah);
    if (!isDataIdentical) {
      // kirim pembaruan data produk ke server
      sendPayload(jumlah, productId);
      // set data temporer agar sama dengan data sekarang
      // sehingga identik agar tidak memperbarui server lagi
      tempJumlah = jumlah;
      for (uint8_t i; i < RFID_OCTET_LENGTH; i += 1) {
        tempProductId [i] = productId[i];
      }
    }
  }
}
/**/
/********************************************************************************************Arduino Setup**/
void setup() {
  Serial.begin(115200);
  SPI.begin();
  //Set the nodeID manually
  mesh.setNodeID(nodeID);
  //Connect to the mesh
  mesh.begin(97, RF24_1MBPS, 3700);
  sprintln(F("Connecting to the mesh..."));
  //RFID
  sprintln(F("Initializing RFID..."));
  rfid.init();
  sprintln(F("Initialization done."));
  sprintln(F("Start main loop."));
}
/**/
/********************************************************************************************Loop start**/
void loop() {
  //update mesh
  mesh.update();
  //baca rfid
  readProductCardSerial();
  //cek bila ada pembaruan produk
  productUpdate();
}
/**/
/* END */
