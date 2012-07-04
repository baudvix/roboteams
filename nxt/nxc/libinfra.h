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


//fuer queue
 int queue1[10];
 int queue2[10];

 int ein_index = 0;
 int aus_index = 0;
 int msg_count = 0;
 mutex queue_mutex;

 void BTCheck(int conn);
 message splitMsg(string in);
 void lcd_print(string msg);
 
 void sd(int &queue1[], int &queue2[]);
 void queueInit(int &queue1[], int &queue2[]);
 bool is_empty(void);
 payload dequeue(int &queue1[], int &queue2[]);
 void enqueue(int &queue1[], int &queue2[], payload elem);
#endif
