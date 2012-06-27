#ifndef LIBINFRA_H
#define LIBINFRA_H

//GLOBALS
//fuer lcd_print()
 static int lcd = 7;
//fuer splitMsg()
struct message{
 string typ;
 int id;
 string msg;
};


//fuer queue
 static string queue[10];
 int ein_index = 0;
 int aus_index = 0;
 int msg_count = 0;
 mutex queue_mutex;

 void BTCheck(int conn);
 message splitMsg(string in);
 void lcd_print(string msg);
 
 bool is_empty(void);
 string dequeue(void);
 bool enqueue(string elem);
#endif
