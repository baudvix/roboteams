#ifndef EXPLORER_H
#define EXPLORER_H

 #define BT_CONN 3
 #define INBOX 7
 #define OUTBOX 3
 
 #define DEBUG 3
 int found = 0;

 mutex print_mutex;
 mutex blue_mutex;
 
 int id = 10;
 
 void undo_found(void);
 
#endif
