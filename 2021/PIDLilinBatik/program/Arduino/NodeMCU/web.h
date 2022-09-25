void handleRoot() {
  Serial.println("New connection on /index");
  server.send(200, "text/html", index_html);
}

void handle_data() {
  if (globalDoc["T"] != nullptr) {
    valConstants = "Sp:"+ globalDoc["data"]["SP"].as<String>() + ", Kp:" + globalDoc["data"]["KP"].as<String>() +
                   " , Ki:" + globalDoc["data"]["KI"].as<String>() + ", Kd:" + globalDoc["data"]["KD"].as<String>();
    digitalWrite(LED, !digitalRead(LED));
    dataJson = "{\"temp\":\"" + globalDoc["T"].as<String>() + "\",\"pid\":\"" + globalDoc["PID"].as<String>() + "\",\"error\":\"" + globalDoc["E"].as<String>() +
               "\",\"angle\":\"" + globalDoc["α"].as<String>() + "\",\"clock\":\"" + globalDoc["C"].as<String>() + "\",\"constants\":\"" + valConstants + "\"}";
    server.send(200, "application/json", dataJson);
    valConstants = "";
    dataJson = "";
    globalDoc.clear();
  } else {
    server.send(204, "text/plain", "null");
  }
}

void handleNotFound() {
  String message = "File Not Found\n\n";
  message += "URI: ";
  message += server.uri();
  message += "\nMethod: ";
  message += (server.method() == HTTP_GET) ? "GET" : "POST";
  message += "\nArguments: ";
  message += server.args();
  message += "\n";
  for (uint8_t i = 0; i < server.args(); i++) {
    message += " " + server.argName(i) + ": " + server.arg(i) + "\n";
  }
  server.send(404, "text/plain", message);
}
