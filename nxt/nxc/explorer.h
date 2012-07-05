#ifndef EXPLORER_H
#define EXPLORER_H

 #define BT_CONN 1
 #define INBOX 5 //device0 5+0
 #define OUTBOX 1 //device0 1+0
 #define DEBUG 3
 int found = 0;
 
 mutex print_mutex;
 mutex blue_mutex;
 
 int id = 10;
 
 void undo_found(void);
 
#endif
