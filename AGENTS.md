**INISIALISASI**
Panzerbot adalah robot tank menggunakan GSM based dari modem 4G yang terdiri atas komponen motor driver L298N, dan raspberry pi.
Panzerbot terdiri atas 2 dinamo dengan konfigurasi 1 di kiri dan 1 di kanan track
Panzerbot memiliki kemampuan untuk mengirimkan data live video feed dari webcam logitech yang terhubung pada USB raspi dan live audio feed yang terhubung ke raspi menggunakan soundcard pada USB
di sisi tank juga terdapat speaker yang terhubung pada raspi untuk memutar soundboard
Panzerbot dikendalikan menggunakan aplikasi android
Kamera webcam logitech akan dipasangi dengan pan tilt servo

**TRANSMISI DATA**
Data video dan audio secara dua arah akan ditransmisikan menggunakan media MTX 

**APLIKASI ANDROID**
Aplikasi android ini dibuild menggunakan next js dan capacitor js dan dideploy menggunakan android studio 
aplikasi ini berorientasi landscape dengan layar yang full terdiri atas kamera dengan elemen joystick sebagai pengendali panzerbot 
Joystick juga akan mengendalikan orientasi kamera

**SISTEM KONTROL**
L298N akan dikendalikan dengan PWM yang bersifat variabel sesuai dengan besaran input joystick 
Joystick juga akan mengendalikan orientasi kamera
Panzerbot dapat berbelok dengan mengunci salah satu sisi roda ataupun berbelok dengan mengurangi kecepatan pada salah satu dinamo roda

**BAHASA**
Gunakan bahasa pyhton dalam membangun semua algoritma panzerbot ini
Gunakan clean arsitektur

**REPO GITHUB**
Sudah tergabung dengan SSH