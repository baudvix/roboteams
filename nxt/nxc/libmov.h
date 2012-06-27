#ifndef LIBMOV_H
#define LIBMOV_H

//GLOBALS
//fuer vor()
 int weiter = 1;

 #define MOTOR_POWER 50
 #define TEPPICH_ABWEICHUNG = 0.2
 int vor(int strecke);
 void zurueck(int umdrehungen);
 void drehen(char richtung, int winkel);

#endif
