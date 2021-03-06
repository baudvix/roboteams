#ifndef LIBMOV_H
#define LIBMOV_H

struct distance{
 int k; // 10000�
 int rest; // x mod 10000�
};

//GLOBALS
//fuer vor()
 int weiter = 1;
 bool hit = 0;

 #define MOTOR_POWER 50
 #define TEPPICH_ABWEICHUNG_L = 1.035
 #define TEPPICH_ABWEICHUNG_R = 0.881
 void vor(int strecke);
 void zurueck(int umdrehungen, distance& d);
 void drehen(char richtung, int winkel);

#endif
