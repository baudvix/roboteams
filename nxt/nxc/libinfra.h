#ifndef LIBINFRA_H
#define LIBINFRA_H

//GLOBALS
//fuer lcd_print()
 static int lcd = 7;
//fuer splitMsg()
struct payload{
 char funktion;
 int param[10];
};

struct message{
 string typ;
 int id;
 payload msg;
};


//fuer queue
 payload queue[];
 payload init0;
 payload init1;
 payload init2;
 payload init3;
 payload init4;
 payload init5;
 payload init6;
 payload init7;
 payload init8;
 payload init9;

 int ein_index = 0;
 int aus_index = 0;
 int msg_count = 0;
 mutex queue_mutex;

 void BTCheck(int conn);
 message splitMsg(string in);
 void lcd_print(string msg);
 
 void queueInit(payload &queue[]);
 bool is_empty(void);
 payload dequeue(payload &queue[]);
 void enqueue(payload &queue[], payload elem);
#endif
