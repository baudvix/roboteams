#ifndef LIBINFRA_H
#define LIBINFRA_H

//GLOBALS
//fuer lcd_print()
 int lcd = 7;
//fuer splitMsg()
struct payload{
 int funktion;
 int param;
};

struct message{
 string typ;
 int id;
 payload msg;
};

//reply queue
/*
 int rqueue1[10];
 int rqueue2[10];
 int rqueue3[10];
 int rqueue4[10];
 int rqueue5[10];

 int rein_index = 0;
 int raus_index = 0;
 int rmsg_count = 0;
 mutex rqueue_mutex;

 void r_queueInit(int &rqueue1[], int &rqueue2[], int &rqueue3[], int &rqueue4[], int &rqueue5[]);
 void r_clean_queue(int &rqueue1[], int &rqueue2[], int &rqueue3[], int &rqueue4[], int &rqueue5[]);
 void r_enqueue(int &rqueue1[], int &rqueue2[], int &rqueue3[], int &rqueue4[], int &rqueue5[], payload elem);
 void r_dequeue(int &rqueue1[], int &rqueue2[], int &rqueue3[], int &rqueue4[], int &rqueue5[]);
 bool r_is_empty(void);*/
//reply queue ende 
 
//fuer normale queue
 int queue1[10];
 int queue2[10];

 int ein_index = 0;
 int aus_index = 0;
 int msg_count = 0;
 mutex queue_mutex;
 
 void clean_queue(int &queue1[], int &queue2[]);
 void queueInit(int &queue1[], int &queue2[]);
 bool is_empty(void);
 payload dequeue(int &queue1[], int &queue2[]);
 void enqueue(int &queue1[], int &queue2[], payload elem);
// normale queue ende 

 void BTCheck(int conn);
 message splitMsg(string in);
 void lcd_print(string msg);
#endif
